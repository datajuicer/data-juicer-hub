"""Recipe-specific RoboCasa extraction and IR-to-VQA operators."""

from pathlib import Path

from data_juicer.ops.base_op import OPERATORS, UNFORKABLE, Mapper

from .runtime import episode_root, vlm_settings, write_json
from .task_ir import render_file, write_targets


class _EpisodeMapperBase(Mapper):
    def __init__(self, output_dir: str = "output/episodes", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.output_dir = output_dir


@OPERATORS.register_module("robocasa_scene_extraction_mapper")
@UNFORKABLE.register_module("robocasa_scene_extraction_mapper")
class RoboCasaSceneExtractionMapper(_EpisodeMapperBase):
    """Replay recorded RoboCasa states and extract calibrated scene IR at 720p."""

    def process_single(self, sample):
        from .robocasa_scene import extract_scene_ir

        if sample["source"] != "robocasa":
            raise ValueError("Expected RoboCasa input")
        root = episode_root(sample, self.output_dir)
        extract_scene_ir(Path(sample["raw_dir"]), root, sample["episode_id"])
        return sample


@OPERATORS.register_module("generate_vqa_from_ir_mapper")
class GenerateVQAFromIRMapper(_EpisodeMapperBase):
    """Construct selected VQA families from DROID perception IR or RoboCasa scene IR."""

    def __init__(
        self,
        families: list[str] = None,
        model: str = None,
        endpoint: str = None,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.families = families
        self.model, self.endpoint = model, endpoint

    def process_single(self, sample):
        root = episode_root(sample, self.output_dir)
        if sample["source"] == "droid":
            from .droid_vqa import build_targets

            model, endpoint = vlm_settings(self.model, self.endpoint)
            items = build_targets(root, model, endpoint)
        else:
            from .robocasa_vqa import build_targets

            items = build_targets(root)
        available = {item["metadata"]["family"] for item in items}
        if self.families is not None:
            unknown = set(self.families) - available
            if unknown:
                raise ValueError(f"Unknown families: {sorted(unknown)}")
            items = [item for item in items if item["metadata"]["family"] in self.families]
        path = write_targets(root, items, "vqa_targets.json")
        rows = render_file(path)
        write_json(root / "vqa.json", rows)
        sample["vqa_path"], sample["target_ir"] = str(root / "vqa.json"), str(path)
        sample["vqa_count"] = len(rows)
        sample["family_count"] = len({row["metadata"]["family"] for row in rows})
        return sample
