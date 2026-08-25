"""batch_clean.py — Batch cleaning: read JSONL -> call Juicer API -> write results"""
import json
import os
from openai import OpenAI

client = OpenAI(base_url=os.getenv("JUICER_BASE_URL", "http://localhost:8000/v1"), api_key="EMPTY")
MODEL = os.getenv("JUICER_MODEL", "juicer")

RECIPE = """Apply these operations exactly in order:
1. Remove HTML tags.
2. Remove duplicate sentences, keeping the first occurrence.
3. Normalize whitespace."""

def clean_text(text: str) -> str:
    prompt = (
        f"Task:\n{RECIPE}\n\n"
        f"Raw input text:\n<input>\n{text}\n</input>\n\n"
        "Return tagged output only.\n"
        "Use exactly this format: <status>KEEP|DROP</status><clean_text>...</clean_text>\n"
    )
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0, max_tokens=4096,
        extra_body={"chat_template_kwargs": {"enable_thinking": False}},
    )
    return resp.choices[0].message.content

input_path = "input.jsonl"   # one {"text": "..."} per line
output_path = "output.jsonl"

with open(input_path) as fin, open(output_path, "w") as fout:
    for line in fin:
        row = json.loads(line)
        result = clean_text(row["text"])
        row["juicer_output"] = result
        fout.write(json.dumps(row, ensure_ascii=False) + "\n")
        print(f"Processed: {row.get('id', '?')} → {result[:80]}")

print(f"Done. Results written to {output_path}")
