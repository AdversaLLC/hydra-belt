# FABLE HANDOFF — Build the Local Small-Model Tool Belt ("Hydra Cortex")

**Written by:** Opus 5 session, 2026-08-29, for a fresh **Fable** session.
**Everything you need is in this one folder: `/home/paladin/local-ai/`** (models, engine, router kit, findings).

---

## 0. The mission (why this exists)

A **tool belt of small specialized local models** that offloads cheap deterministic work
(routing, embedding, PII/injection detection, threat NER, file-type ID) so the **big model
(you, Fable) only spends tokens on real reasoning and writing.** The zero-model BM25 router
ties it together; the Hydra **wisdom/evolve** skills are meant to grow *around* this belt.

Honest framing (verified this session): the combo will **not** out-reason a single big model —
its generative ceiling is Qwen3-0.6B. Its win is **architectural**: specialist accuracy +
always-on cheapness + local privacy, on hardware where no big model runs well anyway.

---

## 1. HARDWARE TRUTH (do not fight this)

- **CPU:** Intel i5-2500S (Sandy Bridge, 2011), 4 cores. **AVX only — NO AVX2, NO FMA, NO F16C, NO BMI2.**
  Stock llama.cpp / candle / onnxruntime-with-avx2 binaries **SIGILL** here. This is the #1 gotcha.
- **GPU:** none usable. Radeon HD 6730M is pre-GCN TeraScale → no ROCm, no hardware Vulkan
  (Mesa shows only `llvmpipe`). **CPU-only inference. Do not chase GPU.**
- **RAM:** 23 GB (plenty for small models). **Disk:** root is a `/cow` overlay; persistence is
  `sda3` = `casper-rw` ext4, ~36 G free. Installs here DO persist across reboot.
- **OS:** Ubuntu 24.04. **Node 24 LTS + jq installed.** User: `paladin`. HF acct: `AdversaLLC`.

---

## 2. ALREADY BUILT & VERIFIED — do NOT redo these

- **Inference engine:** `~/local-ai/llama.cpp/build/bin/llama-cli` and `llama-server`,
  **compiled from source AVX-only** (`-DGGML_AVX=ON -DGGML_AVX2=OFF -DGGML_FMA=OFF -DGGML_F16C=OFF -DGGML_BMI2=OFF`).
  This is the ONLY safe engine on this CPU. Rebuild cmd is in `~/local-ai/` history if needed.
- **BM25 router (Tier 2, zero-download):** `~/local-ai/router/router.py`.
  Measured **97% top-1 / 100% top-3 on `golden.jsonl`** (friendly phrasing).
- **Honest fitness harness:** `~/local-ai/router/robustness.py` + `adversarial.jsonl`.
  **Measured 40% top-1 on paraphrased queries** — this is the PROOF the embedding tier (potion)
  is needed: BM25 misses when user vocabulary ≠ skill vocabulary ("tampered with"↛hashdeep,
  "seized iphone"↛leapp). This is the fitness signal `hydra-evolve` was missing.
- **Rollback substrate:** `~/.claude/skills` is now a **git repo** (baseline commit `75e6816`,
  97 skills tracked; 8 belt clones gitignored). Every mutation = one `git revert`.
- **Wisdom store:** `~/.hydra/wisdom.jsonl` (8 [V] records), `HYDRA_WISDOM` pinned in `.bashrc`.
- **Skills:** full Hydra belt+suite installed; `hydra-router` skill installed; backup at
  `~/Downloads/all-skills-backup-2026-08-29.zip` (104 skills).

---

## 3. THE BELT (models, all downloaded, in `~/local-ai/models/`)

| Folder | Model | Job | Runtime |
|---|---|---|---|
| `router/` | Supra-Router-51M (Q8_0, 54M) | Tier-1 planner: prompt→structured route JSON | llama.cpp |
| `llm/` | Qwen3-0.6B (Q4_K_M, 379M) | Chat/reason offload (generative ceiling) | llama.cpp |
| `code/` | Qwen2.5-Coder-0.5B (Q4_K_M, 380M) | Code offload | llama.cpp |
| `embed/` | potion-base-8M (Model2Vec, 29M) | **Tier-1.5 semantic routing** + wisdom search | model2vec (no torch) |
| `guard/` | bert-tiny-injection-detector (4.4M) | Always-on prompt-injection firewall | onnxruntime/transformers |
| `security/` | SecBERT (84M) | Threat/IOC/CVE NER (forensic) | transformers |
| `security/` | mimelens (7.4M) | File-type from raw bytes (forensic) | transformers (custom_code) |
| `security/` | gravitee bert-small-pii (quant ONNX, 28M) | PII detection/redaction | onnxruntime |
| `models/` | orchestrator.gguf (66M) | earlier Llama-3.2-1B router candidate — SUPERSEDED by Supra-Router; keep or delete |

**Runtime caveat to VERIFY first:** confirm `onnxruntime` CPU wheel runs on this AVX-only CPU
(it uses runtime dispatch, usually OK, but TEST with a 1-line inference before trusting). If it
SIGILLs, run the BERT models via `transformers`+torch CPU, or convert to GGUF for llama.cpp.

**Sanity test the engine now:**
```bash
~/local-ai/llama.cpp/build/bin/llama-cli -m ~/local-ai/models/llm/Qwen3-0.6B-Q4_K_M.gguf -p "hi" -n 20 -no-cnv
```

---

## 4. WHAT TO BUILD — "Hydra Cortex" (full detail in `CORTEX-FINDINGS.md`)

A **3-tier router** as the stack's nervous system (the 20-agent synthesis, 6 layers):
- **Tier 2** = existing BM25 (`router.py`) — floor, zero-download, always works. **Wrap it, don't rewrite it.**
- **Tier 1.5** = potion-base-8M embeddings — paraphrase-robust (fixes the measured 40%→ higher).
- **Tier 1** = Supra-Router-51M — structured route/complexity/plan when ambiguous.

**Critical path (from the synthesis):**
1. **MEASURE first** — extend `adversarial.jsonl`, wire potion Tier-1.5, re-run `robustness.py`;
   prove the embedding tier lifts the 40%. This is the acceptance test for everything after.
2. **Clear the collision** — resolve the 4-way session-start claim (focal/napkin/theorist/wisdom-memory)
   into ONE declarative boot spine BEFORE wiring any hook.
3. **Guard, then wire** — secrets/PII guard on the wisdom write path, then router-memory fusion.

---

## 5. HARD GUARDRAILS (the skeptic's #1 risk — read before touching settings.json)

- **`settings.json` has ZERO hooks today. Keep it near that.** The biggest risk is **hook pile-up**:
  every angle bolting its own `UserPromptSubmit`/`SessionStart` hook **recreates the exact
  "many things claim the auto-slot, no arbiter" disease** — in undebuggable shell instead of prose.
- **Rule: exactly ONE `UserPromptSubmit` and ONE `SessionStart` hook**, each a thin dispatcher that
  calls submodules (route→recall→guard→telemetry) in a declared order, with **hard per-hook timeout
  and mandatory fail-open (exit 0, empty stdout)** so no hook can ever block or blind a prompt.
- **HUMAN-GATE these (do NOT do without explicit user approval):** wiring any hook; moving skills to
  a cold "armory"; rewriting SKILL.md frontmatters. Propose as a mutation list; user approves.
- **Any compile:** always the AVX-only flags from §2. Never trust a prebuilt x86 wheel/binary
  without confirming it avoids AVX2/BMI2.
- **Every mutation is git-committed in `~/.claude/skills`** so `git revert` undoes it atomically.
- License is a non-issue (user is a researcher, local use). Gated HF repos → use ungated GGUF quants.

---

## 6. Vetted model corrections (Hub ground truth, not the other session's claims)

- Blueprint UNDERSTATED sizes: protectai deberta-v3-base = **184M** (not 86M); ModernGuard = **307M**;
  rogue sentinel-v2 = **596M + gated**; SingGuard = **1.1B multimodal** (heavy, skip on CPU); porthor = **~6GB** (skip).
- Llama-Prompt-Guard-2-22M is **70.8M total** + gated (the "22M" is non-embedding only).
- UNVERIFIED / likely hallucinated (no real repo): Cisco Antares "beats GPT-5.5", QTyBERT, TinyGPT-0.88M, BERTector.
  Do not include without confirming on the Hub.
- All belt picks confirmed real + ungated + CPU-fit (see §3).

---

## 7. Open notes

- **Fable theory:** user suspects the forensic skills' auto-triggers keep pulling in Fable-5.
  The router/boot-arbitration work (clearing 61 auto-triggers → routed dispatch) should reduce
  unwanted skill activation generally; worth checking whether that resolves it.
- Recall context at session start: `python3 ~/.claude/skills/wisdom-memory/scripts/wisdom.py --store ~/.hydra/wisdom.jsonl search "router"`.
- A baton is dropped in `~/.baton/` — grab-check it (`ls -t ~/.baton/`).
