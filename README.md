# hydra-belt — local small-model tool belt (CPU-only, preserved weights)

A self-contained, **offline-durable** archive of a small-model "tool belt" for CPU-only
inference on legacy hardware, plus the router/design work around it. The model **weights are
committed here** (as split zip parts) so research can continue even if the upstream
HuggingFace repos disappear. Private archive under AdversaLLC.

## What's here
- **`dist/belt.zip.part00..13`** — the belt models + AVX-only llama.cpp binaries, zipped and
  split to ≤95 MB parts (no Git LFS needed). Rebuild per **`REASSEMBLE.md`**. `belt.zip.sha256` verifies integrity.
- **`FABLE-HANDOFF.md`** — full build spec + hardware truth + guardrails for continuing the work.
- **`CORTEX-FINDINGS.md`** — the 23-agent "Hydra Cortex" architecture synthesis.
- **`router/`** — the zero-download BM25 skill router + eval + adversarial fitness harness
  (`router.py`, `eval.py`, `golden.jsonl`, `robustness.py`, `adversarial.jsonl`). Measured 97% friendly / 40% paraphrase.
- **`download_belt.sh`** — re-pull weights from HuggingFace (only if the upstreams still exist).
- **`make_parts.sh`** — rebuild the split archive after updating models.

## The belt (see FABLE-HANDOFF.md §3 for roles)
Supra-Router-51M · Qwen3-0.6B · Qwen2.5-Coder-0.5B · potion-base-8M · bert-tiny-injection-detector
· SecBERT · mimelens · gravitee PII. All CPU-fit; engine is llama.cpp compiled AVX-only (no AVX2/BMI2).

## Quick start
```bash
cd dist && sha256sum -c belt.zip.sha256 && cat belt.zip.part* > belt.zip && cd .. && unzip dist/belt.zip
./llama.cpp/build/bin/llama-cli -m models/llm/Qwen3-0.6B-Q4_K_M.gguf -p "hello" -n 20 -no-cnv
```
