#!/usr/bin/env python3
"""Download one pinned NVIDIA raw episode and only its XML-referenced assets."""

import concurrent.futures
import gzip
import hashlib
import io
import json
import posixpath
import struct
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
import zipfile
import zlib

from asset_paths import normalize_episode_metadata

DATASET = "nvidia/PhysicalAI-Robotics-Manipulation-Kitchen-Demos"
REVISION = "522e4ffa3bb9d9729f79b241c65fc9e589f2659c"
BASE = "pretrain/atomic/PickPlaceCounterToStove/20250819/lerobot"
ARCHIVES = [
    ("robocasa/robocasa-assets", "fixtures.zip"),
    ("IIFAN/robocasa365-lightwheel-fixtures", "fixtures_lightwheel.zip"),
    ("robocasa/robocasa-assets", "textures.zip"),
    ("robocasa/robocasa-assets", "generative_textures.zip"),
    ("robocasa/robocasa-assets", "objaverse.zip"),
    ("IIFAN/robocasa365-lightwheel-objects", "objects_lightwheel.zip"),
]
ASSET_REVISIONS = {
    "robocasa/robocasa-assets": "1b92c3d02ca4354984fec961357db0bff7b32166",
    "IIFAN/robocasa365-lightwheel-fixtures": "0cf51d45ab07fce13c4733ee1fe20bb01399768c",
    "IIFAN/robocasa365-lightwheel-objects": "3f7f7aee8ef4367dfdc85a86778467cf8527f8fb",
}


def fetch_bytes(url, headers=None):
    for attempt in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=headers or {}), timeout=60) as r:
                return r.read(), {k.lower(): v for k, v in r.headers.items()}
        except (urllib.error.URLError, TimeoutError, ConnectionError):
            if attempt == 3:
                raise
            time.sleep(attempt + 1)


def file_sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_archive_index(repo, filename):
    revision = ASSET_REVISIONS[repo]
    url = f"https://huggingface.co/datasets/{repo}/resolve/{revision}/{filename}"
    tail, headers = fetch_bytes(url + "?range=tail", {"Range": "bytes=-65536"})
    if not headers.get("content-range"):
        raise RuntimeError("Archive host must support HTTP Range")
    total = int(headers["content-range"].split("/")[-1])
    end = tail.rfind(b"PK\x05\x06")
    if end < 0 or len(tail) - end < 22:
        raise ValueError("Missing ZIP end-of-directory record")
    fields = struct.unpack("<4s4H2LH", tail[end : end + 22])
    _, offset = fields[5:7]
    central, _ = fetch_bytes(url + "?range=central", {"Range": f"bytes={offset}-{total - 1}"})
    with zipfile.ZipFile(io.BytesIO(central)) as archive:
        entries = {info.filename: info for info in archive.infolist()}
    # Restore the offsets shifted by parsing the directory without its file data.
    for info in entries.values():
        info.header_offset += offset
    return url, entries, revision


def extract_entry(url, info, output):
    n = 30 + len(info.filename.encode()) + len(info.extra) + info.compress_size + 2048
    chunk, _ = fetch_bytes(
        url + "?range=" + str(info.header_offset),
        {"Range": f"bytes={info.header_offset}-{info.header_offset + n - 1}"},
    )
    if chunk[:4] != b"PK\x03\x04":
        raise RuntimeError("Unexpected ZIP range response")
    fields = struct.unpack("<4s5H3L2H", chunk[:30])
    start = 30 + fields[-2] + fields[-1]
    payload = chunk[start : start + info.compress_size]
    if info.compress_type == zipfile.ZIP_DEFLATED:
        payload = zlib.decompress(payload, -15)
    elif info.compress_type != zipfile.ZIP_STORED:
        raise ValueError("Unsupported ZIP compression")
    if len(payload) != info.file_size or zlib.crc32(payload) != info.CRC:
        raise ValueError("ZIP CRC mismatch")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(payload)
    return str(output), file_sha256(output)


def download(root, episode):
    ready = root / "download_manifest.json"
    cached_manifest = {}
    if ready.is_file():
        cached_manifest = json.loads(ready.read_text())
        if (
            cached_manifest["episode"] == episode
            and cached_manifest["revision"] == REVISION
            and bool(cached_manifest["assets"])
            and all(
                (root / p).is_file() and file_sha256(root / p) == digest
                for p, digest in cached_manifest["files"].items()
            )
            and all(
                (root / "assets" / p).is_file() and file_sha256(root / "assets" / p) == digest
                for p, digest in cached_manifest["assets"].items()
            )
        ):
            print("Using cached episode and assets:", root)
            return
    paths = [
        f"extras/{episode}/ep_meta.json",
        f"extras/{episode}/model.xml.gz",
        f"extras/{episode}/states.npz",
        f"data/chunk-000/{episode}.parquet",
        "extras/dataset_meta.json",
        "meta/info.json",
    ]
    manifest = {
        "dataset": DATASET,
        "revision": REVISION,
        "base": BASE,
        "episode": episode,
        "files": {},
        "assets": {},
        "archive_revisions": {},
    }
    for p in paths:
        out = root / p
        out.parent.mkdir(parents=True, exist_ok=True)
        expected_hash = cached_manifest.get("files", {}).get(p)
        if not out.exists() or (expected_hash and file_sha256(out) != expected_hash):
            out.write_bytes(fetch_bytes(f"https://huggingface.co/datasets/{DATASET}/resolve/{REVISION}/{BASE}/{p}")[0])
        manifest["files"][p] = file_sha256(out)
    normalize_episode_metadata(root, episode)
    for relative in paths:
        manifest["files"][relative] = file_sha256(root / relative)
    xml = ET.fromstring(gzip.decompress((root / f"extras/{episode}/model.xml.gz").read_bytes()))
    needed = {
        posixpath.normpath(e.get("file").split("robocasa/models/assets/")[1])
        for e in xml.iter()
        if "robocasa/models/assets/" in e.get("file", "")
    }
    for repo, name in ARCHIVES:
        if not needed:
            break
        print("Index", repo, name, flush=True)
        url, entries, revision = read_archive_index(repo, name)
        manifest["archive_revisions"][repo] = revision
        matches = []
        for relative in sorted(needed):
            suffix = relative
            if relative.startswith("objects/"):
                suffix = relative[len("objects/") :]
            candidates = [i for p, i in entries.items() if p == suffix or p.endswith("/" + suffix)]
            if not candidates:
                continue
            matches.append((relative, candidates[0]))

        def download_asset(item):
            relative, info = item
            out = root / "assets" / relative
            expected_hash = cached_manifest.get("assets", {}).get(relative)
            if not out.exists() or (expected_hash and file_sha256(out) != expected_hash):
                extract_entry(url, info, out)
            return relative, file_sha256(out)

        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
            for relative, digest in ex.map(download_asset, matches):
                manifest["assets"][relative] = digest
                needed.remove(relative)
        print("Retrieved", len(matches), "remaining", len(needed), flush=True)
    if needed:
        raise FileNotFoundError("Missing assets: " + str(sorted(needed)))
    (root / "download_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print("Raw episode and referenced assets ready:", root)
