"""Episode paths, JSON files and model settings."""

import json
import os
from pathlib import Path


def read_json(path):
    return json.loads(Path(path).read_text())


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")


def episode_root(sample, output_dir):
    if sample["source"] not in {"droid", "robocasa"}:
        raise ValueError("Unknown episode source")
    identifier = sample["episode_id"]
    if not identifier or Path(identifier).name != identifier or identifier in {".", ".."}:
        raise ValueError("episode_id must be a safe filename component")
    root = Path(output_dir).resolve() / sample["source"] / identifier
    root.mkdir(parents=True, exist_ok=True)
    sample["episode_dir"] = str(root)
    return root


def vlm_settings(model, endpoint):
    endpoint = (endpoint or os.environ.get("VLM_URL", "http://127.0.0.1:8000/v1")).rstrip("/")
    model = model or os.environ.get("VLM_MODEL")
    if not model:
        raise ValueError("Set VLM_MODEL or the model parameter")
    return model, endpoint
