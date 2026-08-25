# Examples

Juicer usage examples. All examples call the vLLM OpenAI-compatible API directly — no extra framework needed.

## Prerequisites

Start the Juicer model service:

```bash
vllm serve "$MODEL_ID" --port 8000 --tensor-parallel-size 2 --max-model-len 32768
```

## Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| `single_clean.py` | Minimal call: single-text cleaning | `python single_clean.py` |
| `batch_clean.py` | Batch cleaning: read JSONL → call API → write results | `python batch_clean.py input.jsonl output.jsonl` |
| `pii_redact.py` | PII redaction: email/phone placeholder replacement | `python pii_redact.py` |

## Output formats

Juicer always outputs one of two contracts:

**tagged_text** (cleaning / filtering / redaction):
```
<status>KEEP</status><clean_text>processed text</clean_text>
<status>DROP</status><clean_text></clean_text>
```

**json** (tagging / scoring / classification):
```json
{"helpfulness": 4, "correctness": 4, "coherence": 4, "complexity": 1, "verbosity": 2}
```

## adapter.py

`adapter.py` (in the repo root) provides prompt construction and output parsing:

- `build_prompt_from_row(row)` — build a prompt from a case row
- `parse_output(text, output_format)` — parse tagged_text or json output
- CLI: `python adapter.py build-prompts ...` / `python adapter.py parse-outputs ...`

See the **Integration Code** section in [README.md](../README.md) for full code snippets.
