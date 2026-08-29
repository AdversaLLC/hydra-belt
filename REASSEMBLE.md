# The model belt is stored as split zip parts — how to rebuild it

The model weights (~1.3 GB) don't fit as single files in a normal git repo (GitHub caps
files at 100 MB). So the whole `models/` folder **plus the AVX-only `llama.cpp` binaries**
were zipped **uncompressed** (weights don't compress) and split into **14 parts of ≤95 MB**
(`dist/belt.zip.part00` … `belt.zip.part13`), which commit as ordinary git blobs — **no Git
LFS, no quota.**

## Reassemble (any Linux/macOS, no special tools)

```bash
cd dist
# 1. verify the parts arrived intact
sha256sum -c belt.zip.sha256
# 2. concatenate parts back into one zip (order is guaranteed by the 00..13 suffixes)
cat belt.zip.part* > belt.zip
# 3. unzip into the project root
cd .. && unzip dist/belt.zip
```

That recreates `models/` (the belt) and `llama.cpp/build/bin/` (the AVX-only engine binaries).

## Or skip the zip entirely — re-pull from the source

The weights are all public on HuggingFace. To fetch fresh copies instead of reassembling:

```bash
bash download_belt.sh      # re-downloads every belt model to models/
```

## Why it's parted (the short version)

- GitHub hard-limits single files to 100 MB; three weights exceed that (Qwen3 379M, Coder 380M, SecBERT 321M).
- Git LFS would handle big files but its free tier is only 1 GB storage — the belt is ~1.1 GB, over the line.
- Splitting under 100 MB keeps every part a normal git blob: no LFS, no quota, universal `cat` reassembly.
- `belt.zip.sha256` lets you confirm each part transferred byte-for-byte before rebuilding.
