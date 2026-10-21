"""Build VQA semantic targets from episode images with a served VLM."""

import base64
import hashlib
import json
import os
import urllib.request
from pathlib import Path

from data_juicer.utils.robot_perception_utils import contact_sheet


class SemanticAnnotator:
    def __init__(self, root, model=None, endpoint=None):
        self.root = Path(root).resolve()
        self.model = model or os.environ.get("VLM_MODEL")
        self.endpoint = (endpoint or os.environ.get("VLM_URL", "http://127.0.0.1:8000/v1")).rstrip("/")
        if not self.model:
            raise ValueError("Semantic label generation requires VLM_MODEL")

    def choose(self, family, images, question, options):
        labels = [chr(65 + i) for i in range(len(options))]
        prompt = (
            "Annotate the following visual question from the numbered panels. "
            "Each Image N panel is one supplied image, in the original order. "
            "Use only visible evidence and the task instruction. Do not assume task "
            "success merely because an instruction is present. Seeing an object near "
            "a gripper does not establish that it is held securely. Object movement "
            "does not establish that the instructed goal was achieved. Describe "
            "only the visible relation or change. For next-action "
            "prediction, infer the next action from the supplied context. "
            "Return JSON with exactly answer and evidence. answer must be one option "
            "letter, or null when no option can be determined from the images. "
            "evidence must describe the visual basis. No annotation has been provided to you.\n"
            + question
            + "\n"
            + "\n".join(f"({label}) {text}" for label, text in zip(labels, options))
        )
        paths = [(Path(p) if Path(p).is_absolute() else self.root / p).resolve() for p in images]
        hashes = [hashlib.sha256(p.read_bytes()).hexdigest() for p in paths]
        request_hash = hashlib.sha256(
            json.dumps([self.model, self.endpoint, prompt, hashes, "numbered-sheet-v1"]).encode()
        ).hexdigest()
        output = self.root / "ir/vlm_semantic_labels" / (hashlib.sha256(family.encode()).hexdigest()[:16] + ".json")
        cached = json.loads(output.read_text()) if output.is_file() else None
        if cached and cached.get("request_sha256") == request_hash:
            record = cached
        else:
            model_input = output.with_name(output.stem + "_input.jpg")
            contact_sheet(paths, model_input)
            encoded = base64.b64encode(model_input.read_bytes()).decode()
            content = [
                {"type": "text", "text": prompt},
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{encoded}"},
                },
            ]
            payload = {
                "model": self.model,
                "messages": [{"role": "user", "content": content}],
                "temperature": 0,
                "max_tokens": 512,
                "chat_template_kwargs": {"enable_thinking": False},
                "response_format": {"type": "json_object"},
            }
            headers = {"Content-Type": "application/json"}
            if os.environ.get("VLM_API_KEY"):
                headers["Authorization"] = "Bearer " + os.environ["VLM_API_KEY"]
            request = urllib.request.Request(
                self.endpoint + "/chat/completions",
                data=json.dumps(payload).encode(),
                headers=headers,
            )
            with urllib.request.urlopen(request, timeout=180) as response:
                raw = json.loads(response.read())["choices"][0]["message"]["content"]
            parsed = json.loads(raw)
            record = {
                "family": family,
                "generator": "vlm",
                "request_sha256": request_hash,
                "question": question,
                "options": dict(zip(labels, options)),
                "images": [str(p.relative_to(self.root)) for p in paths],
                "image_sha256": hashes,
                "model_input": str(model_input.relative_to(self.root)),
                "model_input_sha256": hashlib.sha256(model_input.read_bytes()).hexdigest(),
                "response": raw,
                "annotation": parsed,
            }
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(json.dumps(record, indent=2) + "\n")
        annotation = record["annotation"]
        if (
            set(annotation) != {"answer", "evidence"}
            or annotation.get("answer") not in labels
            or not isinstance(annotation.get("evidence"), str)
        ):
            raise ValueError(f"Invalid VLM response schema for {family}; see {output}")
        return options[labels.index(annotation["answer"])], {
            "generator": "vlm",
            "annotation_file": str(output.relative_to(self.root)),
            "request_sha256": request_hash,
            "image_sha256": hashes,
            "evidence": annotation["evidence"],
        }
