#!/bin/bash
set -e
cd /home/paladin/local-ai
rm -f dist/belt.zip dist/belt.zip.part*
echo "[1/3] zipping (store mode, weights don't compress)..."
zip -0 -q -r dist/belt.zip models llama.cpp/build/bin
echo "[2/3] zip done: $(du -h dist/belt.zip|cut -f1). splitting into 95M parts..."
split -b 95M -d -a 2 dist/belt.zip dist/belt.zip.part
rm -f dist/belt.zip
echo "[3/3] parts:"; ls -la dist/belt.zip.part* | awk '{print $5, $9}'
echo "sha256 manifest:"; sha256sum dist/belt.zip.part* > dist/belt.zip.sha256; cat dist/belt.zip.sha256
echo "PARTS DONE"
