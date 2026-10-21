# Embodied VQA construction

Data-Juicer recipes for converting DROID recordings and RoboCasa simulator
episodes into intermediate representations and VQA records.

| Source | Recipe | VQA families per episode |
| --- | --- | --- |
| DROID (optional DA3 depth) | [embodied-vqa-droid.yaml](../embodied-vqa-droid.yaml) | 29 |
| RoboCasa | [embodied-vqa-robocasa.yaml](../embodied-vqa-robocasa.yaml) | 39 |

Run the following commands from the data-juicer-hub root directory.

## Setup

```bash
export DATA_JUICER_ROOT=/path/to/data-juicer
pip install -e "$DATA_JUICER_ROOT"
pip install 'transformers>=5.8' 'torch>=2.11' torchvision modelscope h5py \
  opencv-contrib-python imageio imageio-ffmpeg 'mujoco==3.3.1' 'robosuite==1.5.2'
```

Make the recipe package importable by Data-Juicer worker processes:

```bash
export PYTHONPATH="$PWD/demo${PYTHONPATH:+:$PYTHONPATH}"
```

DROID uses a CUDA GPU, SAM3 and an OpenAI-compatible VLM endpoint. The perception
runtime uses Transformers 5.8 and PyTorch 2.11. Set the endpoint and model through
environment variables:

```bash
export VLM_MODEL=your-served-model
export VLM_URL=http://127.0.0.1:8000/v1
```

`VLM_API_KEY` supplies API credentials. `SAM3_MODEL` selects a local SAM3 weight
directory or model ID. `CUDA_VISIBLE_DEVICES` selects the inference GPU.
RoboCasa rendering uses MuJoCo 3.3.1 and robosuite 1.5.2. For headless rendering:

```bash
export MUJOCO_GL=egl
export PYOPENGL_PLATFORM=egl
```

Set `MUJOCO_EGL_DEVICE_ID` when selecting a rendering device.

## DROID

Prepare a recording with `trajectory.h5`, `metadata_*.json`, the three camera
MP4 files and the official language-annotation JSON:

```bash
python demo/embodied_vqa/tools/prepare_inputs.py \
  --source droid \
  --raw /path/to/droid_episode \
  --annotations /path/to/annotations.json \
  --episode-id episode_000001 \
  --output inputs/embodied_vqa/droid.jsonl

dj-process --config demo/embodied-vqa-droid.yaml
```

Input directories with `metadata.parquet`, `state.parquet` and camera MP4 files
are also accepted. For that format, supply `--episode-index` and
`--primary-view` (the camera filename without `.mp4`). Multiple episode rows can
be placed in the same input JSONL file.

The recipe processes the complete videos. VLM/SAM3 produces object and gripper
tracks, followed by destination grounding, interaction geometry and semantic
annotations. The generation mapper renders 29 VQA families from task IR.

### Optional DA3 depth

Install the [Depth Anything 3](https://github.com/ByteDance-Seed/Depth-Anything-3)
SDK and its depth-inference dependencies in the same environment. Then uncomment
the `robot_depth_estimation_mapper` block in
`demo/embodied-vqa-droid.yaml`, between object tracking and gripper tracking:

```bash
pip install --no-deps "depth-anything-3 @ git+https://github.com/ByteDance-Seed/Depth-Anything-3.git@3d835ec1a5802d64a8b8b15f817a1ab54809bfe4"
pip install omegaconf addict evo e3nn plyfile pillow_heif pycolmap trimesh 'moviepy==1.0.3'

dj-process --config demo/embodied-vqa-droid.yaml
```

The default model is `depth-anything/DA3METRIC-LARGE`. `DA3_MODEL` can point to a
local checkpoint directory. Every camera frame produces a depth array in
`ir/da3_depth/<camera>/`. Interaction geometry samples object and gripper depth from these predictions. It does not change the VQA family set.

Without calibration, depth units are `focal_normalized`. To obtain metres,
provide source-resolution 3×3 matrices in the input sample's
`camera_intrinsics` dictionary.
Any-view DA3 models use `inference_batch_size: 0` for joint processing within
each camera.

## RoboCasa

Prepare an episode from NVIDIA's kitchen demonstrations. The command downloads
the recorded states, scene metadata and referenced assets:

```bash
python demo/embodied_vqa/tools/prepare_inputs.py \
  --source robocasa \
  --raw /path/to/robocasa_episode \
  --episode-id episode_000009 \
  --output inputs/embodied_vqa/robocasa.jsonl

dj-process --config demo/embodied-vqa-robocasa.yaml
```

The scene mapper replays recorded simulator states and renders two 1280×720
camera views. Instance masks, depth, camera projections, contacts and temporal
states provide the IR for 39 VQA families, with 40 records per episode including
present/absent localization.

## Operators

DROID episode-to-IR operators are native Data-Juicer mappers. RoboCasa replay,
VQA semantic annotation, task templates and answer construction live in this Hub
recipe package, loaded through `custom_operator_paths`.

| Location | Operator | Output |
| --- | --- | --- |
| Main | `robot_gripper_anchor_mapper` | Gripper-state anchor and instruction |
| Main | `robot_object_tracking_mapper` | Full camera frames and object track |
| Main | `robot_depth_estimation_mapper` | Optional per-frame depth and depth samples |
| Main | `robot_gripper_tracking_mapper` | Gripper detection and full track |
| Main | `robot_destination_grounding_mapper` | Final-view target point |
| Main | `robot_interaction_geometry_mapper` | Interaction geometry and episode IR |
| Recipe | `robocasa_scene_extraction_mapper` | Rendered scene and simulator IR |
| Recipe | `generate_vqa_from_ir_mapper` | Semantic task targets and family-specific VQA records |

Each episode is one Data-Juicer sample. GPU models are loaded on first use and
reused within a worker. The `families` parameter of the generation mapper selects
a subset of families; the supplied recipes generate all families.

## Outputs

Each recipe writes its episode dataset to `outputs/<recipe-name>/episodes.jsonl`
and episode files under `outputs/<recipe-name>/episodes/<source>/<episode-id>/`:

- Camera frames and videos.
- Perception or simulator IR under `ir/`.
- Typed task targets and `vqa.json`.

Each VQA record contains `id`, `images`, `messages`, `answer` and `metadata`.
The corresponding typed answer target remains in the episode task IR.

## Data sources

DROID: [dataset](https://droid-dataset.github.io/), CC BY 4.0.

RoboCasa recordings:
[NVIDIA kitchen demonstrations](https://huggingface.co/datasets/nvidia/PhysicalAI-Robotics-Manipulation-Kitchen-Demos),
CC BY 4.0. Scene assets come from RoboCasa and Lightwheel; robot meshes come from
robosuite.
