"""Adapt official DROID HDF5 recordings without modifying source annotations."""

import hashlib
import json
from pathlib import Path

from data_juicer.utils.lazy_loader import LazyLoader

np = LazyLoader("numpy")


def prepare_recording(root, episode_index, annotations=None):
    import h5py
    import pyarrow as pa
    import pyarrow.parquet as pq

    root = Path(root).resolve()
    metadata_files = sorted(root.glob("metadata_*.json"))
    if len(metadata_files) != 1:
        raise ValueError("Expected exactly one official DROID episode metadata JSON")
    metadata = json.loads(metadata_files[0].read_text())
    if annotations is not None:
        annotation_path = Path(annotations)
        values = json.loads(annotation_path.read_text())[metadata["uuid"]]
        annotation_digest = hashlib.sha256(annotation_path.read_bytes()).hexdigest()
    else:
        receipt = json.loads((root / "source_manifest.json").read_text())
        if receipt["uuid"] != metadata["uuid"]:
            raise ValueError("Annotations and recording UUID differ")
        values = receipt["annotations"]
        annotation_digest = receipt["annotation_sha256"]
    instructions = {
        f"other_information.language_instruction_{i}": values.get(f"language_instruction{i}", "").strip()
        for i in (1, 2, 3)
    }
    if not any(instructions.values()):
        raise ValueError("Official task annotations are required for this episode")
    with h5py.File(root / "trajectory.h5", "r") as recording:
        signal = np.asarray(recording["observation/robot_state/gripper_position"], dtype=np.float64).reshape(-1)
    if not np.isfinite(signal).all() or len(signal) != metadata["trajectory_length"]:
        raise ValueError("Gripper states do not match the recorded trajectory")
    cameras = [str(metadata[key]) for key in ("wrist_cam_serial", "ext1_cam_serial", "ext2_cam_serial")]
    for camera in cameras:
        if not camera.isdecimal():
            raise ValueError("Camera serial must be a decimal recording identifier")
        video = root / (camera + ".mp4")
        if not video.is_file():
            original = root / "recordings/MP4" / video.name
            if not original.is_file():
                raise FileNotFoundError(original)
            video.symlink_to(original.relative_to(root))
    pq.write_table(
        pa.Table.from_pylist([dict(episode_index=episode_index, **instructions)]),
        root / "metadata.parquet",
    )
    pq.write_table(
        pa.table(
            {
                "episode_index": np.full(len(signal), episode_index, dtype=np.int64),
                "frame_index": np.arange(len(signal), dtype=np.int64),
                "observation.state.gripper_position": signal,
            }
        ),
        root / "state.parquet",
    )
    result = {
        "episode_index": episode_index,
        "primary_view": str(metadata["ext1_cam_serial"]),
        "state_frame_count": len(signal),
        "annotation_sha256": annotation_digest,
        "trajectory_sha256": hashlib.sha256((root / "trajectory.h5").read_bytes()).hexdigest(),
        "instruction_columns": list(instructions),
    }
    (root / "prepared_manifest.json").write_text(json.dumps(result, indent=2) + "\n")
    return result
