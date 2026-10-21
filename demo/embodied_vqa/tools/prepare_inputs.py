"""Prepare one-episode Data-Juicer input manifests."""

import argparse
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", choices=["droid", "robocasa"], required=True)
    parser.add_argument("--raw", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--episode-id")
    parser.add_argument("--episode-index", type=int)
    parser.add_argument("--primary-view")
    parser.add_argument("--annotations", type=Path, help="Official DROID language-annotation JSON")
    args = parser.parse_args()
    raw = args.raw.resolve()
    if args.source == "droid":
        from data_juicer.utils.robot_utils import read_instruction

        if (raw / "trajectory.h5").is_file():
            from droid_input import prepare_recording

            prepared = prepare_recording(
                raw,
                args.episode_index if args.episode_index is not None else 0,
                args.annotations,
            )
            args.episode_index = prepared["episode_index"]
            args.primary_view = args.primary_view or prepared["primary_view"]
        if args.episode_index is None or not args.episode_id or not args.primary_view:
            parser.error("DROID requires episode-id, episode-index and primary-view")
        for name in ["metadata.parquet", "state.parquet", args.primary_view + ".mp4"]:
            if not (raw / name).is_file():
                raise FileNotFoundError(raw / name)
        text, _ = read_instruction(raw / "metadata.parquet")
        row = {
            "source": "droid",
            "episode_id": args.episode_id,
            "episode_index": args.episode_index,
            "primary_view": args.primary_view,
            "raw_dir": str(raw),
            "text": text,
            "metadata_path": str(raw / "metadata.parquet"),
            "state_path": str(raw / "state.parquet"),
        }
    else:
        from robocasa_download import download

        episode = args.episode_id or "episode_000009"
        download(raw, episode)
        text = json.loads((raw / f"extras/{episode}/ep_meta.json").read_text())["lang"]
        row = {
            "source": "robocasa",
            "episode_id": episode,
            "raw_dir": str(raw),
            "text": text,
        }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(row) + "\n")
    print("Prepared", args.source, "episode manifest:", args.output)


if __name__ == "__main__":
    main()
