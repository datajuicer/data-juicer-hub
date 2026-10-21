"""Store task targets and render VQA records."""

import json
from copy import deepcopy
from pathlib import Path


def target_item(identifier, images, question, target, metadata):
    return {
        "id": identifier,
        "images": images,
        "question": question,
        "target": deepcopy(target),
        "metadata": deepcopy(metadata),
    }


def final_value(target):
    kind = target["type"]
    if kind == "choice":
        return target["correct_label"]
    if kind == "point_or_no_object" and target["expected_kind"] == "no_object":
        return target.get("accepted_text", ["No object"])[0]
    if kind in {"point", "point_or_no_object"}:
        points = target.get("points", [target["point"]] if "point" in target else [])
    elif kind == "traj2d":
        points = target["traj"]
    else:
        raise ValueError(f"Unsupported task target: {kind}")
    key = target.get("key", "point_2d")
    return json.dumps([{key: point} for point in points], separators=(",", ":"))


def render_target(item):
    value = final_value(item["target"])
    return {
        "id": item["id"],
        "images": list(item["images"]),
        "messages": [
            {
                "role": "user",
                "content": "\n".join(["<image>"] * len(item["images"]) + [item["question"]]),
            }
        ],
        "answer": value,
        "metadata": deepcopy(item["metadata"]),
    }


def write_targets(root, items, name):
    root = Path(root).resolve()
    path = root / "ir" / name
    path.parent.mkdir(parents=True, exist_ok=True)
    if len({item["id"] for item in items}) != len(items):
        raise ValueError("Duplicate task IR IDs")
    path.write_text(json.dumps({"schema_version": 1, "items": items}, indent=2) + "\n")
    return path


def render_file(path):
    path = Path(path).resolve()
    document = json.loads(path.read_text())
    return [render_target(item) for item in document["items"]]


def point_target(point):
    return {"type": "point", "point": point, "key": "point_2d"}
