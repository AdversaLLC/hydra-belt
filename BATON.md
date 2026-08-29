# Baton: build the local small-model tool belt (Hydra Cortex)

**Intent & Goal:** Build a CPU-only tool belt of small specialist models on this AVX-only i5 so the big model only spends tokens on reasoning. Full spec + models: `~/local-ai/FABLE-HANDOFF.md`.

**State of Play (VERIFIED):** Engine built (llama.cpp AVX-only, `~/local-ai/llama.cpp/build/bin/`). Belt models downloaded to `~/local-ai/models/`. BM25 router 97% friendly / 40% paraphrase (measured — proves potion tier needed). `~/.claude/skills` git baseline `75e6816` (rollback ready). Wisdom store `~/.hydra/wisdom.jsonl`. 20-agent "Hydra Cortex" design in `~/local-ai/CORTEX-FINDINGS.md`.

**Learnings & Landmines:** NO AVX2/BMI2 → stock binaries SIGILL, always compile AVX-only. No usable GPU. Biggest risk = HOOK PILE-UP: exactly ONE UserPromptSubmit + ONE SessionStart hook, fail-open. Human-gate hook wiring / armory move / frontmatter rewrites. Verify onnxruntime runs on AVX-only before trusting BERT models.

**Pointers:** `~/local-ai/FABLE-HANDOFF.md` (master), `CORTEX-FINDINGS.md` (design), `~/local-ai/router/` (router+eval+robustness kit).

**Next Steps:** (1) sanity-test engine on Qwen3-0.6B. (2) wire potion Tier-1.5, re-run robustness.py, prove paraphrase lift. (3) resolve 4-way session-start collision into one boot spine. (4) then, human-gated, wire the single dispatcher hook.

**Open Questions:** Does onnxruntime CPU run on this Sandy Bridge? Does routed dispatch resolve the "Fable keeps getting invoked" theory?
