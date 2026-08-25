"""Juicer Demo（中文版）— FastAPI backend + HTML frontend.

Run: python app_zh.py  (then open http://localhost:7861)
Serves static/index_zh.html. Requires an OpenAI-compatible Juicer service at JUICER_BASE_URL.
"""

from __future__ import annotations

import json
import os
import random
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from openai import OpenAI

import adapter

BASE_URL = os.getenv("JUICER_BASE_URL", "http://localhost:8000/v1")
# AB comparison is opt-in: the raw (base model) service is not required for the
# core Juicer experience. Set JUICER_RAW_BASE_URL only when you want AB tab active.
RAW_BASE_URL = os.getenv("JUICER_RAW_BASE_URL", "")
ARCHIVE_FAILURES = os.getenv("JUICER_ARCHIVE_FAILURES", "0").lower() in {"1", "true", "yes"}
CASES_DIR = Path(__file__).parent / "cases"
STATIC_DIR = Path(__file__).parent / "static"
REPORTS_DIR = Path(__file__).parent / "reports"
FAILURES_FILE = REPORTS_DIR / "failures.jsonl"

_failures_lock = threading.Lock()


def verify_output(parsed: dict, expected_status: str, expected_text: str, output_format: str) -> dict:
    """Compare parsed model output against expected values from a case row."""
    if output_format == "json":
        try:
            expected_json = json.loads(expected_text or "{}")
            actual_json = parsed.get("json")
            match = actual_json == expected_json
        except Exception:
            match = False
        return {"match": match, "fields": {"json": match}}
    status_match = (parsed.get("status") or "").upper() == (expected_status or "").upper()
    text_match = (parsed.get("clean_text") or "").strip() == (expected_text or "").strip()
    return {"match": status_match and text_match, "fields": {"status": status_match, "text": text_match}}


def archive_failure(record: dict) -> None:
    with _failures_lock:
        REPORTS_DIR.mkdir(exist_ok=True)
        with FAILURES_FILE.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")

CATEGORY_LABELS = {
    "atomic_mapper": "原子 Mapper（单步变换）",
    "atomic_filter": "原子 Filter（单步过滤）",
    "pii": "PII 脱敏",
    "hallucination": "幻觉检测",
    "rubric": "质量评分（HelpSteer2）",
    "safety": "安全分类（Aegis）",
    "order_sensitive": "顺序敏感",
    "compositional": "组合操作",
}

app = FastAPI(title="Juicer Demo")
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


def load_cases() -> dict[str, list[dict]]:
    cases: dict[str, list[dict]] = {}
    for f in sorted(CASES_DIR.glob("*.jsonl")):
        items = []
        with open(f, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line:
                    items.append(json.loads(line))
        cases[f.stem] = items
    return cases


ALL_CASES = load_cases()


def detect_model_name() -> str:
    """Auto-detect model name from /v1/models; fall back to env or 'juicer'."""
    env_model = os.getenv("JUICER_MODEL")
    if env_model:
        return env_model
    try:
        client = OpenAI(base_url=BASE_URL, api_key="EMPTY")
        models = client.models.list()
        if models.data:
            return models.data[0].id
    except Exception:
        pass
    return "juicer"


@app.get("/", response_class=HTMLResponse)
async def index():
    return (STATIC_DIR / "index_zh.html").read_text(encoding="utf-8")


@app.get("/api/health")
async def health():
    """Check model-service reachability via /v1/models and return detected model name.

    Used by the Playground header to show a green/red model status dot. Always
    returns 200 with an ``ok`` boolean so the frontend can render either state
    without catching HTTP errors.
    """
    try:
        client = OpenAI(base_url=BASE_URL, api_key="EMPTY")
        models = client.models.list()
        ids = [m.id for m in models.data] if models.data else []
        model = ids[0] if ids else os.getenv("JUICER_MODEL", "juicer")
        return {"ok": True, "model": model, "base_url": BASE_URL, "models": ids}
    except Exception as e:
        return {
            "ok": False,
            "model": os.getenv("JUICER_MODEL", "juicer"),
            "base_url": BASE_URL,
            "models": [],
            "error": str(e),
        }


@app.get("/api/categories")
async def get_categories():
    return {
        k: {"label": v, "count": len(ALL_CASES.get(k, []))}
        for k, v in CATEGORY_LABELS.items()
        if k in ALL_CASES
    }


@app.get("/api/cases")
async def list_cases(category: Optional[str] = None):
    if category:
        if category not in ALL_CASES:
            raise HTTPException(status_code=404, detail=f"Unknown category: {category}")
        return {"category": category, "items": ALL_CASES[category]}
    return {k: v for k, v in ALL_CASES.items()}


@app.get("/api/cases/random")
async def random_case(category: Optional[str] = None):
    if category:
        items = ALL_CASES.get(category)
        if not items:
            raise HTTPException(status_code=404, detail=f"Unknown category: {category}")
    else:
        items = [c for group in ALL_CASES.values() for c in group]
    return random.choice(items)


@app.get("/api/cases/{case_id}")
async def get_case(case_id: str):
    for group in ALL_CASES.values():
        for case in group:
            if case.get("id") == case_id:
                return case
    raise HTTPException(status_code=404, detail=f"Case not found: {case_id}")


@app.get("/api/cases/{pair_id}/pair")
async def get_pair(pair_id: str):
    """Return both A/B variants for an order-sensitive pair."""
    pair = []
    for group in ALL_CASES.values():
        for case in group:
            if case.get("pair_id") == pair_id:
                pair.append(case)
    if not pair:
        raise HTTPException(status_code=404, detail=f"Pair not found: {pair_id}")
    pair.sort(key=lambda c: c.get("variant", ""))
    return {"pair_id": pair_id, "items": pair}


@app.post("/api/run")
async def run(data: dict):
    text = (data.get("text") or data.get("input_text") or "").strip()
    recipe = (data.get("recipe") or "").strip()
    output_format = (data.get("output_format") or "tagged_text").strip()
    reference = (data.get("reference") or "").strip()
    case_id = (data.get("case_id") or data.get("id") or "").strip()
    capability = (data.get("capability") or "").strip()
    expected_status = (data.get("expected_status") or "").strip()
    expected_text = (data.get("expected_text") or "").strip()

    if not text:
        raise HTTPException(status_code=400, detail="text is required")
    if not recipe:
        raise HTTPException(status_code=400, detail="recipe is required")
    if output_format not in ("tagged_text", "json"):
        raise HTTPException(status_code=400, detail=f"Unknown output_format: {output_format}")

    row = {
        "input_text": text,
        "recipe": recipe,
        "output_format": output_format,
        "reference": reference if reference else None,
    }
    prompt = adapter.build_prompt_from_row(row)
    model = detect_model_name()

    client = OpenAI(base_url=BASE_URL, api_key="EMPTY")
    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=4096,
            extra_body={"chat_template_kwargs": {"enable_thinking": False}},
        )
        raw = resp.choices[0].message.content or ""
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"model service call failed: {e}")

    parsed = adapter.parse_output(raw, output_format)

    verify_result = None
    if expected_status or expected_text:
        verify_result = verify_output(parsed, expected_status, expected_text, output_format)
        if not verify_result["match"] and ARCHIVE_FAILURES:
            archive_failure({
                "ts": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "case_id": case_id or None,
                "capability": capability or None,
                "output_format": output_format,
                "expected_status": expected_status or None,
                "expected_text": expected_text or None,
                "actual_status": parsed.get("status"),
                "actual_text": parsed.get("clean_text") if output_format != "json" else None,
                "actual_json": parsed.get("json") if output_format == "json" else None,
                "input_text": text,
                "recipe": recipe,
            })

    return {**parsed, "output_format": output_format, "model": model, "prompt": prompt, "verify": verify_result}


def _detect_model_at(base_url: str, fallback: str) -> str:
    try:
        client = OpenAI(base_url=base_url, api_key="EMPTY")
        models = client.models.list()
        if models.data:
            return models.data[0].id
    except Exception:
        pass
    return fallback


def _run_at(base_url: str, model: str, prompt: str, output_format: str) -> dict:
    client = OpenAI(base_url=base_url, api_key="EMPTY")
    resp = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        max_tokens=4096,
        extra_body={"chat_template_kwargs": {"enable_thinking": False}},
    )
    raw = resp.choices[0].message.content or ""
    return adapter.parse_output(raw, output_format)


@app.get("/api/ab/health")
async def ab_health():
    """Check whether the raw (baseline) model service is reachable for AB comparison.

    Returns ``configured: False`` when JUICER_RAW_BASE_URL is unset (the default),
    so the frontend can show a setup notice instead of an error. When configured,
    probes the service and returns the detected model name.
    """
    if not RAW_BASE_URL:
        return {"ok": False, "configured": False, "raw_model": None, "raw_base_url": None}
    try:
        client = OpenAI(base_url=RAW_BASE_URL, api_key="EMPTY")
        models = client.models.list()
        ids = [m.id for m in models.data] if models.data else []
        return {"ok": bool(ids), "configured": True,
                "raw_model": ids[0] if ids else None, "raw_base_url": RAW_BASE_URL}
    except Exception as e:
        return {"ok": False, "configured": True, "raw_model": None,
                "raw_base_url": RAW_BASE_URL, "error": str(e)}


@app.post("/api/ab/run")
async def ab_run(data: dict):
    """Run the same recipe on both Juicer and the raw baseline, return side-by-side results."""
    if not RAW_BASE_URL:
        raise HTTPException(status_code=400, detail="AB comparison is not configured")
    text = (data.get("text") or data.get("input_text") or "").strip()
    recipe = (data.get("recipe") or "").strip()
    output_format = (data.get("output_format") or "tagged_text").strip()
    reference = (data.get("reference") or "").strip()
    expected_status = (data.get("expected_status") or "").strip()
    expected_text = (data.get("expected_text") or "").strip()

    if not text:
        raise HTTPException(status_code=400, detail="text is required")
    if not recipe:
        raise HTTPException(status_code=400, detail="recipe is required")
    if output_format not in ("tagged_text", "json"):
        raise HTTPException(status_code=400, detail=f"Unknown output_format: {output_format}")

    prompt = adapter.build_prompt_from_row({
        "input_text": text, "recipe": recipe,
        "output_format": output_format, "reference": reference or None,
    })

    def one(base_url: str, fallback: str) -> dict:
        model = _detect_model_at(base_url, fallback)
        try:
            parsed = _run_at(base_url, model, prompt, output_format)
        except Exception as e:
            return {"model": model, "error": str(e), "verify": None}
        verify = None
        if expected_status or expected_text:
            verify = verify_output(parsed, expected_status, expected_text, output_format)
        return {**parsed, "model": model, "verify": verify}

    juicer_res = one(BASE_URL, "juicer")
    raw_res = one(RAW_BASE_URL, "raw")
    return {
        "output_format": output_format,
        "prompt": prompt,
        "expected_status": expected_status or None,
        "expected_text": expected_text or None,
        "juicer": juicer_res,
        "raw": raw_res,
    }


@app.get("/api/failures")
async def get_failures():
    """Return all archived failure records from reports/failures.jsonl."""
    if not ARCHIVE_FAILURES:
        return {"enabled": False, "count": 0, "items": []}
    if not FAILURES_FILE.exists():
        return {"count": 0, "items": []}
    items = []
    with FAILURES_FILE.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                try:
                    items.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    return {"enabled": True, "count": len(items), "items": items}


@app.delete("/api/failures")
async def clear_failures():
    """Clear all archived failure records."""
    if not ARCHIVE_FAILURES:
        return {"ok": False, "enabled": False}
    with _failures_lock:
        if FAILURES_FILE.exists():
            FAILURES_FILE.write_text("", encoding="utf-8")
    return {"ok": True, "enabled": True}


if __name__ == "__main__":
    import uvicorn
    print()
    print("=" * 50)
    print("  Juicer Demo（中文版）")
    print("  Open: http://localhost:7861")
    print(f"  API:  {BASE_URL}")
    ab_status = "on" if RAW_BASE_URL else "off (set JUICER_RAW_BASE_URL to enable)"
    print(f"  AB:   {ab_status}")
    print("=" * 50)
    print()
    uvicorn.run(app, host="0.0.0.0", port=7861)
