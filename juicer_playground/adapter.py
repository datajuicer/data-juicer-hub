#!/usr/bin/env python3
"""Build Juicer-friendly prompts and parse Juicer tagged outputs.

The adapter is intentionally dependency-free so it can be copied into small
data-pipeline jobs. It standardizes the prompt and output contract around the
schema used in the model card:

    <status>KEEP|DROP</status><clean_text>...</clean_text>
"""

from __future__ import annotations

import argparse
import csv
import html
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


TAGGED_RE = re.compile(
    r"<status>\s*(?P<status>KEEP|DROP)\s*</status>\s*<clean_text>(?P<clean_text>.*?)</clean_text>",
    re.IGNORECASE | re.DOTALL,
)


@dataclass(frozen=True)
class Scenario:
    name: str
    title: str
    recipe: str
    extra_input: str = ""
    output_format: str = "tagged_text"
    output_rules: tuple[str, ...] = (
        "status must be KEEP or DROP.",
        "If status is KEEP, clean_text must be the final refined text.",
        "If status is DROP, clean_text should be empty unless the task explicitly asks for an explanation.",
        "Do not output markdown, code fences, or explanations.",
    )


SCENARIOS: dict[str, Scenario] = {
    "recipe_cleaning": Scenario(
        name="recipe_cleaning",
        title="General data-refinement recipe",
        recipe="{recipe}",
    ),
    "dedupe_normalize": Scenario(
        name="dedupe_normalize",
        title="Deduplicate and normalize text",
        recipe=(
            "Apply these operations exactly in order:\n"
            "1. Remove exact duplicate sentences, keeping the first occurrence.\n"
            "2. Normalize whitespace.\n"
            "3. Preserve the original language and factual content."
        ),
    ),
    "pii_redaction": Scenario(
        name="pii_redaction",
        title="PII redaction",
        recipe=(
            "Apply these operations exactly in order:\n"
            "1. Remove or mask email addresses, phone numbers, street addresses, government IDs, and access tokens.\n"
            "2. Keep non-sensitive surrounding content when it remains useful.\n"
            "3. If the text is mostly sensitive credentials or private identifiers, return DROP."
        ),
    ),
    "hallucination_grounding": Scenario(
        name="hallucination_grounding",
        title="Reference-grounded hallucination cleanup",
        recipe=(
            "Apply these operations exactly in order:\n"
            "1. Compare the raw input against the reference.\n"
            "2. Remove claims that are not supported by the reference.\n"
            "3. Keep supported wording concise and faithful to the reference.\n"
            "4. Return DROP if no useful supported claim remains."
        ),
        extra_input="Reference:\n<reference>\n{reference}\n</reference>\n\n",
    ),
    "quality_rubric": Scenario(
        name="quality_rubric",
        title="Quality-rubric filtering",
        recipe=(
            "Apply these operations exactly in order:\n"
            "1. Keep text that is coherent, specific, non-empty, and useful for downstream tasks.\n"
            "2. Drop boilerplate, broken formatting, near-empty text, spam, or text dominated by placeholders.\n"
            "3. When keeping text, lightly normalize whitespace without changing meaning."
        ),
    ),
    "rubric_scoring": Scenario(
        name="rubric_scoring",
        title="HelpSteer2 rubric scoring",
        recipe=(
            "Score all HelpSteer2 rubric attributes for the response. "
            "Use integer scores from 0 to 4 for helpfulness, correctness, coherence, complexity, and verbosity."
        ),
        output_format="json",
        output_rules=(
            'Return only this JSON shape: {"helpfulness": 0-4, "correctness": 0-4, "coherence": 0-4, "complexity": 0-4, "verbosity": 0-4}.',
            "Use integers only.",
            "Do not output markdown, code fences, comments, explanations, or extra keys.",
        ),
    ),
    "safety_filter": Scenario(
        name="safety_filter",
        title="Safety filtering",
        recipe=(
            "Apply these operations exactly in order:\n"
            "1. Drop content that gives actionable instructions for wrongdoing, self-harm, weapons, or cyber abuse.\n"
            "2. Keep benign, educational, or refusal-style safety text.\n"
            "3. When keeping text, preserve the original meaning and normalize whitespace."
        ),
    ),
}


def read_jsonl(path: Path) -> Iterable[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            line = line.strip()
            if not line:
                continue
            try:
                value = json.loads(line)
            except json.JSONDecodeError as exc:
                raise SystemExit(f"{path}:{line_number}: invalid JSON: {exc}") from exc
            if not isinstance(value, dict):
                raise SystemExit(f"{path}:{line_number}: expected a JSON object per line")
            yield value


def read_csv(path: Path) -> Iterable[dict[str, Any]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        yield from csv.DictReader(handle)


def read_txt(path: Path, text_field: str) -> Iterable[dict[str, Any]]:
    text = path.read_text(encoding="utf-8")
    for index, block in enumerate(re.split(r"\n\s*\n", text.strip()), 1):
        if block.strip():
            yield {"id": f"txt-{index}", text_field: block.strip()}


def read_rows(path: Path, input_format: str, text_field: str) -> list[dict[str, Any]]:
    if input_format == "auto":
        suffix = path.suffix.lower()
        if suffix == ".jsonl":
            input_format = "jsonl"
        elif suffix == ".csv":
            input_format = "csv"
        else:
            input_format = "txt"
    readers = {
        "jsonl": read_jsonl,
        "csv": read_csv,
        "txt": lambda p: read_txt(p, text_field),
    }
    return list(readers[input_format](path))


def get_value(row: dict[str, Any], field: str, default: str = "") -> str:
    value = row.get(field, default)
    if value is None:
        return default
    if isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=False)


def build_prompt(
    row: dict[str, Any],
    scenario: Scenario,
    text_field: str,
    recipe_field: str,
    reference_field: str,
) -> str:
    text = get_value(row, text_field)
    recipe = scenario.recipe.format(recipe=get_value(row, recipe_field, scenario.recipe))
    reference = get_value(row, reference_field)
    extra_input = scenario.extra_input.format(reference=reference)
    rules = "\n".join(f"- {rule}" for rule in scenario.output_rules)
    if scenario.output_format == "json":
        return (
            f"Task:\n{recipe}\n\n"
            f"{extra_input}"
            f"Input:\n{text}\n\n"
            f"Rules:\n{rules}"
        )
    return (
        f"Task:\n{recipe}\n\n"
        f"{extra_input}"
        f"Raw input text:\n<input>\n{text}\n</input>\n\n"
        "Return tagged output only.\n"
        "Use exactly this format: <status>KEEP|DROP</status><clean_text>...</clean_text>\n"
        f"Rules:\n{rules}"
    )


def build_prompt_from_row(
    row: dict[str, Any],
    text_field: str = "input_text",
    recipe_field: str = "recipe",
    reference_field: str = "reference",
) -> str:
    """Build a prompt directly from a unified case row.

    Unlike ``build_prompt``, this trusts the row's own ``recipe`` and
    ``output_format`` fields. It only adds a minimal, non-contradictory
    footer so recipes that already specify a return format are reinforced
    rather than overridden. Used by the playground app.
    """
    text = get_value(row, text_field)
    recipe = get_value(row, recipe_field)
    if not recipe:
        raise ValueError("case row is missing a recipe")
    reference = get_value(row, reference_field)
    ref_block = f"Reference:\n<reference>\n{reference}\n</reference>\n\n" if reference else ""
    output_format = row.get("output_format", "tagged_text")

    if output_format == "json":
        return (
            f"Task:\n{recipe}\n\n"
            f"{ref_block}"
            f"Input:\n{text}\n\n"
            "Return only the JSON object. No markdown, no code fences, no explanations."
        )
    return (
        f"Task:\n{recipe}\n\n"
        f"{ref_block}"
        f"Raw input text:\n<input>\n{text}\n</input>\n\n"
        "Return tagged output only.\n"
        "Use exactly this format: <status>KEEP|DROP</status><clean_text>...</clean_text>"
    )


def row_id(row: dict[str, Any], id_field: str, index: int) -> str:
    value = row.get(id_field)
    if value is None or value == "":
        return f"row-{index}"
    return str(value)


def write_prompt_record(
    handle: Any,
    output_format: str,
    model: str,
    record_id: str,
    prompt: str,
    max_tokens: int,
) -> None:
    messages = [{"role": "user", "content": prompt}]
    if output_format == "prompt-jsonl":
        record = {"id": record_id, "prompt": prompt}
    elif output_format == "messages-jsonl":
        record = {"id": record_id, "messages": messages}
    elif output_format == "openai-batch-jsonl":
        record = {
            "custom_id": record_id,
            "method": "POST",
            "url": "/v1/chat/completions",
            "body": {
                "model": model,
                "messages": messages,
                "temperature": 0,
                "max_tokens": max_tokens,
                "chat_template_kwargs": {"enable_thinking": False},
            },
        }
    else:
        raise AssertionError(output_format)
    handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def cmd_build_prompts(args: argparse.Namespace) -> None:
    scenario = SCENARIOS[args.scenario]
    rows = read_rows(args.input, args.input_format, args.text_field)
    with args.output.open("w", encoding="utf-8") as handle:
        for index, row in enumerate(rows, 1):
            prompt = build_prompt(row, scenario, args.text_field, args.recipe_field, args.reference_field)
            write_prompt_record(
                handle=handle,
                output_format=args.output_format,
                model=args.model,
                record_id=row_id(row, args.id_field, index),
                prompt=prompt,
                max_tokens=args.max_tokens,
            )


def extract_model_text(row: dict[str, Any], output_field: str) -> str:
    if output_field in row:
        return get_value(row, output_field)
    try:
        return row["response"]["body"]["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError):
        pass
    try:
        return row["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError):
        pass
    raise SystemExit(
        "Could not find model output. Pass --output-field or use OpenAI batch/chat-completion shaped JSONL."
    )


def parse_tagged(text: str) -> dict[str, Any]:
    match = TAGGED_RE.search(text)
    if not match:
        return {"parse_ok": False, "status": None, "clean_text": None, "raw_output": text}
    status = match.group("status").upper()
    clean_text = html.unescape(match.group("clean_text").strip())
    return {"parse_ok": True, "status": status, "clean_text": clean_text, "raw_output": text}


def parse_json_output(text: str) -> dict[str, Any]:
    """Extract the first JSON object from a model response."""
    stripped = text.strip()
    try:
        value = json.loads(stripped)
        return {"parse_ok": True, "json": value, "raw_output": text}
    except json.JSONDecodeError:
        pass
    match = re.search(r"\{[\s\S]*\}", stripped)
    if match:
        try:
            value = json.loads(match.group(0))
            return {"parse_ok": True, "json": value, "raw_output": text}
        except json.JSONDecodeError:
            pass
    return {"parse_ok": False, "json": None, "raw_output": text}


def parse_output(text: str, output_format: str = "tagged_text") -> dict[str, Any]:
    """Dispatch parser based on the expected output_format."""
    if output_format == "json":
        return parse_json_output(text)
    return parse_tagged(text)


def cmd_parse_outputs(args: argparse.Namespace) -> None:
    rows = read_rows(args.input, "jsonl", args.text_field)
    with args.output.open("w", encoding="utf-8") as handle:
        for index, row in enumerate(rows, 1):
            text = extract_model_text(row, args.output_field)
            parsed = parse_tagged(text)
            parsed["id"] = row.get("custom_id") or row.get(args.id_field) or f"row-{index}"
            handle.write(json.dumps(parsed, ensure_ascii=False) + "\n")


def add_build_prompts_parser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    parser = subparsers.add_parser("build-prompts", help="Convert user data into Juicer prompt JSONL")
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--input-format", choices=["auto", "jsonl", "csv", "txt"], default="auto")
    parser.add_argument("--output-format", choices=["prompt-jsonl", "messages-jsonl", "openai-batch-jsonl"], default="messages-jsonl")
    parser.add_argument("--scenario", choices=sorted(SCENARIOS), required=True)
    parser.add_argument("--model", default="juicer")
    parser.add_argument("--id-field", default="id")
    parser.add_argument("--text-field", default="text")
    parser.add_argument("--recipe-field", default="recipe")
    parser.add_argument("--reference-field", default="reference")
    parser.add_argument("--max-tokens", type=int, default=4096)
    parser.set_defaults(func=cmd_build_prompts)


def add_parse_outputs_parser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    parser = subparsers.add_parser("parse-outputs", help="Parse Juicer tagged outputs into JSONL")
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--id-field", default="id")
    parser.add_argument("--text-field", default="text")
    parser.add_argument("--output-field", default="output")
    parser.set_defaults(func=cmd_parse_outputs)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(required=True)
    add_build_prompts_parser(subparsers)
    add_parse_outputs_parser(subparsers)
    args = parser.parse_args(argv)
    args.func(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
