# Showcase Cases Index

Juicer showcase cases, grouped by CDR-Bench-aligned capability. Each case uses a structured recipe to demonstrate a specific data-refinement operator or pipeline.

## Category Overview

| Category | File | Count | Capabilities |
|----------|------|-------|--------------|
| Atomic Mapper | `atomic_mapper.jsonl` | 6 | Single-step text transforms: copyright removal, whitespace normalization, email/IP cleaning, plus multi-step mapper chains |
| Atomic Filter | `atomic_filter.jsonl` | 5 | Single-step filter decisions: text length, alphanumeric ratio, character repetition, max line length |
| PII Redaction | `pii.jsonl` | 10 | Name / ID / address / contact / temporal placeholder redaction |
| Hallucination | `hallucination.jsonl` | 5 | Reference-grounded detection and correction (JSON output) |
| Rubric Scoring | `rubric.jsonl` | 4 | HelpSteer2 dimension scoring (complexity, verbosity, coherence, correctness) |
| Safety | `safety.jsonl` | 6 | Aegis safety-label classification (prompt_label, response_label) + multi-step combos |
| Order-sensitive | `order_sensitive.jsonl` | 8 | Multi-operator chains where execution order matters |
| Compositional | `compositional.jsonl` | 7 | Multi-step end-to-end pipelines (PII redaction combos, safety classification chains) |

**Total: 51 cases** across 8 capability dimensions.

## Design Principles

**CDR-Bench-aligned operator taxonomy**: cases follow CDR-Bench's `atomic_m` / `atomic_f` / `semantic_*` / `order_*` track structure; each case maps to a clear `operator` and `operator_kind`.

**Atomic-first, compositional as supplement**: most cases are single-step atomic operations (atomic mapper / atomic filter), while compositional cases show multi-step operator coordination.

**Structured prompt format**: explicit numbered steps make operation order and output requirements easy to inspect.

**Showcase-oriented**: cases demonstrate the breadth of Juicer's data-refinement capabilities across all major CDR-Bench operator categories.

## Case Data Format (unified schema)

Each case is a JSONL line; all categories share the same schema:

```json
{
  "id": "am-001",
  "capability": "atomic_mapper",
  "operator": "whitespace_normalization_mapper",
  "operator_kind": "mapper",
  "title": "Whitespace normalization",
  "description": "Atomic mapper: collapse multiple spaces, trim leading/trailing whitespace",
  "input_text": "  The   quick  brown   fox.  ",
  "reference": "(optional; for hallucination detection and other reference-grounded tasks)",
  "recipe": "Normalize whitespace: collapse multiple spaces to one, trim.",
  "output_format": "tagged_text",
  "expected_status": "KEEP",
  "expected_text": "The quick brown fox.",
  "why_good": "What capability this case demonstrates"
}
```

Field notes:
- `output_format`: `tagged_text` (outputs `<status>KEEP|DROP</status><clean_text>...</clean_text>`) or `json` (outputs structured JSON)
- `operator_kind`: `mapper` / `filter` / `semantic_mapper` / `compositional`

## Per-Category Notes

### Atomic Mapper (`atomic_mapper.jsonl`)
Single-step text-transform operators, plus short mapper chains for demonstrating CDR-Bench-style data transformations.

Cases:
- `am-001` copyright removal, `am-002` whitespace normalization, `am-005` email cleaning
- `am-003` / `am-004` 4-step pipelines (email + IP + links + more), `am-006` 2-step pipeline (IP + MAC)

### Atomic Filter (`atomic_filter.jsonl`)
Single-step filter-decision operators that demonstrate threshold-based KEEP/DROP decisions.

Cases:
- `af-001` / `af-004` text length filter, `af-002` alphanumeric ratio filter, `af-003` character repetition filter, `af-006` max line length filter

### PII Redaction (`pii.jsonl`)
A natural advantage of local deployment: redact sensitive data without it leaving your machines.

Cases:
- `pii-001` / `pii-006` person names, `pii-002` / `pii-007` ID numbers, `pii-003` / `pii-004` addresses
- `pii-005` contact info (email/phone), `pii-008` / `pii-009` / `pii-010` temporal/birth-date info

### Hallucination (`hallucination.jsonl`)
Reference-grounded comparison tasks, JSON output.

Cases:
- `hall-001` / `hall-003` / `hall-006` hallucination correction (fix hallucinated content using reference)
- `hall-004` / `hall-007` hallucination detection (determine if text contains hallucinated content)

### Rubric Scoring (`rubric.jsonl`)
HelpSteer2 dimension scoring: one atomic case per dimension.

Cases:
- `rub-001` complexity, `rub-002` verbosity, `rub-003` coherence, `rub-004` correctness

### Safety (`safety.jsonl`)
Aegis safety-label classification: atomic per-field cases plus multi-step combos.

Cases:
- `safe-001` / `safe-005` prompt_label classification, `safe-002` / `safe-003` response_label classification
- `safe-004` / `safe-006` 3-step pipelines (prompt_label + response_label + violated_categories)

### Order-sensitive (`order_sensitive.jsonl`)
Multi-operator chains where the specified execution order determines the result. Showcases Juicer's ability to follow recipe order precisely.

Cases:
- `os-001` through `os-008`: diverse 3-5 step pipelines mixing filters and mappers (length filters, copyright cleaning, IP/MAC/links removal, word filters, punctuation normalization)

### Compositional (`compositional.jsonl`)
Multi-step end-to-end pipelines, showcasing complex recipe handling.

Cases:
- `comp-001` / `comp-002` / `comp-004` PII redaction combos (person + temporal, contact + location)
- `comp-003` / `comp-005` / `comp-006` / `comp-007` safety classification chains (prompt_label + response_label + violated_categories)
