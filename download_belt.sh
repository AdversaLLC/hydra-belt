#!/bin/bash
# Belt model downloader — ungated HF resolve URLs, no auth needed
set -u
B=/home/paladin/local-ai/models
HF=https://huggingface.co
log(){ echo "[$(date +%H:%M:%S)] $*"; }
get(){ # repo  path  destdir
  local url="$HF/$1/resolve/main/$2"
  local out="$B/$3/$(basename "$2")"
  if [ -s "$out" ]; then log "skip (have) $3/$(basename "$2")"; return; fi
  log "GET $1/$2"
  wget -q "$url" -O "$out" && log "  ok $(du -h "$out"|cut -f1) -> $3/$(basename "$2")" || { log "  FAIL $1/$2"; rm -f "$out"; }
}

# --- router (Supra-Router-51M, Q8_0 near-lossless, tiny) ---
get SupraLabs/Supra-Router-51M-gguf Supra-Router-51M-Q8_0.gguf router

# --- generative LLM + code (Q4_K_M) ---
get unsloth/Qwen3-0.6B-GGUF Qwen3-0.6B-Q4_K_M.gguf llm
get bartowski/Qwen2.5-Coder-0.5B-Instruct-GGUF Qwen2.5-Coder-0.5B-Instruct-Q4_K_M.gguf code

# --- embeddings (potion-base-8M, model2vec static) ---
for f in config.json model.safetensors modules.json special_tokens_map.json tokenizer.json tokenizer_config.json vocab.txt; do
  get minishlab/potion-base-8M "$f" embed
done

# --- always-on prompt-injection guard (bert-tiny 4.4M) ---
for f in config.json model.safetensors special_tokens_map.json tokenizer.json tokenizer_config.json vocab.txt; do
  get marklkelly/bert-tiny-injection-detector "$f" guard
done

# --- forensic: threat/IOC NER (SecBERT) ---
for f in config.json vocab.txt model.safetensors; do
  get jackaduma/SecBERT "$f" security
done
# --- forensic: file-type from raw bytes (mimelens, custom_code) ---
for f in config.json configuration_mimelens.py modeling_mimelens.py manifest.json model.safetensors tokenizer.json tokenizer_config.json; do
  get mjbommar/mimelens-001-tiny-bpe-16k-s1 "$f" security
done
# --- PII detection (gravitee, quantized ONNX = CPU-ideal) ---
for f in config.json model.quant.onnx special_tokens_map.json tokenizer.json tokenizer_config.json vocab.txt; do
  get gravitee-io/bert-small-pii-detection "$f" security
done

log "=== DONE. Belt contents: ==="
du -sh "$B"/*/ 2>/dev/null
echo "TOTAL: $(du -sh "$B" | cut -f1)"
