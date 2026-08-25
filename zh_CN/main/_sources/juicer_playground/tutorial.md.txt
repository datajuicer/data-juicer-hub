# Juicer Quick Start

## 1. Start the model

The Playground connects to an OpenAI-compatible API. vLLM is the recommended serving option, while SGLang and other compatible servers can be used as well.

### vLLM (recommended)

The included launcher is suitable for a single H20 (96GB):

```bash
export MODEL_PATH=/path/to/juicer-model
bash serve.sh --model "$MODEL_PATH"

# Stop the service when finished
bash serve.sh --stop
```

The default API is `http://localhost:8000/v1`. Use `--port` to select another port.

### SGLang

Install SGLang for your accelerator environment by following the [official installation guide](https://docs.sglang.io/docs/get-started/install), then launch:

```bash
export MODEL_PATH=/path/to/juicer-model
python -m sglang.launch_server \
  --model-path "$MODEL_PATH" \
  --served-model-name juicer \
  --port 8000 \
  --trust-remote-code
```

### Local Transformers

For direct Python inference without a service, see the local Transformers example in [README.md](README.md).

## 2. Open the Playground

```bash
pip install -r requirements.txt
export JUICER_BASE_URL=http://localhost:8000/v1
python app.py
```

Open `http://localhost:7860` in a browser. For the Chinese interface, run `python app_zh.py` and open `http://localhost:7861`.

If `JUICER_MODEL` is unset, the backend detects the first model exposed by `/v1/models`.

## 3. Playground guide

The Playground is a single-page app with four tabs:

### 3.1 Try Juicer

1. Optionally select a case category.
2. Load a random case or enter custom text and a recipe.
3. Select `tagged_text` or `json` as the output format.
4. Click **Run** to inspect the parsed result and raw response.

Order-sensitive paired cases provide a button for switching the operation order.

### 3.2 Showcase Gallery

Browse 51 cases across eight CDR-Bench-aligned categories. A case can be inspected in the detail dialog or loaded into the try page.

### 3.3 Capability Showcase

Explore representative examples for ordered execution, PII redaction, hallucination handling, rubric scoring, and safety classification.

### 3.4 AB Comparison

If multiple GPUs are available, start the base model and Juicer together:

```bash
bash serve_ab.sh \
  --juicer /path/to/juicer-model \
  --raw /path/to/Qwen3.6-35B-A3B

export JUICER_BASE_URL=http://localhost:8000/v1
export JUICER_RAW_BASE_URL=http://localhost:8001/v1
python app.py
```

By default Juicer uses GPU 0 and port 8000, while the base model uses GPU 1 and port 8001. Override them with `--juicer-gpus`, `--raw-gpus`, `--juicer-port`, and `--raw-port`. For small functional tests, `--gdn-prefill-backend triton --moe-backend triton --enforce-eager` avoids the initial FlashInfer JIT build, torch compilation, and CUDA Graph capture; omit those flags for vLLM's automatic backend selection and throughput-oriented serving. Stop both services with `bash serve_ab.sh --stop`.

## 4. Call from code

```bash
python examples/single_clean.py
python examples/batch_clean.py
python examples/pii_redact.py
```

All examples use `JUICER_BASE_URL` and optionally `JUICER_MODEL`.

## 5. Write recipes

Juicer accepts natural-language recipes. Numbered steps make execution order explicit, and an explicit output contract makes downstream parsing easier.

Tagged-text example:

```text
Apply these operations exactly in order:
1. Remove HTML tags.
2. Remove duplicate sentences.
3. Normalize whitespace.

Return: <status>KEEP|DROP</status><clean_text>...</clean_text>
```

JSON example:

```text
Score the response for helpfulness and correctness from 0 to 4.
Return only: {"helpfulness": int, "correctness": int}.
```

## 6. Case library

The `cases/` directory contains eight categories:

- `atomic_mapper.jsonl` — single-step text transforms
- `atomic_filter.jsonl` — single-step filtering decisions
- `pii.jsonl` — PII redaction
- `hallucination.jsonl` — hallucination detection and correction
- `rubric.jsonl` — HelpSteer2 quality scoring
- `safety.jsonl` — Aegis safety classification
- `order_sensitive.jsonl` — ordered multi-step pipelines
- `compositional.jsonl` — compositional pipelines

See [cases/README.md](cases/README.md) for the schema.

## 7. Format adapter

`adapter.py` standardizes prompt construction and output parsing:

```python
import adapter

row = {
    "input_text": "  The   quick  brown fox.  ",
    "recipe": "Normalize whitespace.",
    "output_format": "tagged_text",
}
prompt = adapter.build_prompt_from_row(row)
parsed = adapter.parse_output(model_output_text, row["output_format"])
```

It also provides CLI commands for batch prompt construction and parsing:

```bash
python adapter.py build-prompts \
  --input your_data.jsonl \
  --output prompts.jsonl \
  --scenario recipe_cleaning \
  --output-format messages-jsonl

python adapter.py parse-outputs \
  --input model_outputs.jsonl \
  --output parsed.jsonl
```

## 8. Connect another compatible service

Change the endpoint and optional model name without modifying the Playground:

```bash
export JUICER_BASE_URL=http://server-address:8000/v1
export JUICER_MODEL=served-model-name
python app.py
```

## Requirements

- Python 3.10 or newer
- Enough accelerator memory for the selected precision and inference framework
- An OpenAI-compatible service for the Playground, or Transformers for direct local inference
