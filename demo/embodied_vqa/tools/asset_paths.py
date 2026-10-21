"""Normalize machine-specific paths in downloaded simulation metadata."""

import gzip
import json
import xml.etree.ElementTree as ET
from pathlib import Path

ASSET_PREFIXES = ("robocasa/models/assets/", "robosuite/models/assets/")


def portable_path(value):
    for prefix in ASSET_PREFIXES:
        if prefix in value:
            return prefix + value.split(prefix, 1)[1]
    return value


def normalize_values(value):
    if isinstance(value, dict):
        return {key: normalize_values(item) for key, item in value.items()}
    if isinstance(value, list):
        return [normalize_values(item) for item in value]
    if isinstance(value, str):
        return portable_path(value)
    return value


def normalize_episode_metadata(root: Path, episode: str):
    metadata = root / "extras" / episode / "ep_meta.json"
    original = json.loads(metadata.read_text())
    normalized = normalize_values(original)
    if normalized != original:
        metadata.write_text(json.dumps(normalized, indent=2) + "\n")

    model = root / "extras" / episode / "model.xml.gz"
    tree = ET.fromstring(gzip.decompress(model.read_bytes()))
    changed = False
    for element in tree.iter():
        path = element.get("file")
        if path is None:
            continue
        normalized_path = portable_path(path)
        if normalized_path != path:
            element.set("file", normalized_path)
            changed = True
    if changed:
        model.write_bytes(gzip.compress(ET.tostring(tree, encoding="utf-8"), mtime=0))
