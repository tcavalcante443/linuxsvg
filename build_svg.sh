#!/usr/bin/env bash
set -euo pipefail

BITS="${BITS:-32}"
OUT_WIN="${OUT_WIN:-/mnt/c/Users/Public/linux.svg}"
OWNER_USER="${SUDO_USER:-$USER}"

cd "$(dirname "$0")"
mkdir -p build out build/files

if ! command -v gcc >/dev/null 2>&1 || [ ! -f /usr/include/stdlib.h ]; then
  echo "Instalando gcc e libc6-dev..."
  DEBIAN_FRONTEND=noninteractive apt-get update -qq
  DEBIAN_FRONTEND=noninteractive apt-get install -y -qq gcc libc6-dev
fi

chmod +x init build/root/sbin/init 2>/dev/null || true

if [ ! -f "build/build_files" ]; then
  echo "Compilando build/build_files..."
  gcc tinyemu/build_filelist.c tinyemu/fs_utils.c tinyemu/cutils.c -o build/build_files
fi

echo "Gerando build/files/root..."
rm -rf build/files/root
mkdir -p build/files/root
./build/build_files build/root build/files/root

BBL=$(find . -maxdepth 4 -name "bbl${BITS}.bin" 2>/dev/null | head -n 1)
KRN=$(find . -maxdepth 4 -name "kernel-riscv${BITS}.bin" 2>/dev/null | head -n 1)
EMU=$(find . -maxdepth 4 -name "riscvemu${BITS}.js" 2>/dev/null | head -n 1)

test -n "$BBL" || { echo "ERRO: bbl${BITS}.bin nao encontrado"; exit 1; }
test -n "$KRN" || { echo "ERRO: kernel-riscv${BITS}.bin nao encontrado"; exit 1; }
test -n "$EMU" || { echo "ERRO: riscvemu${BITS}.js nao encontrado"; exit 1; }
test -f "vm_${BITS}.cfg" || { echo "ERRO: vm_${BITS}.cfg nao encontrado"; exit 1; }

cp "vm_${BITS}.cfg" "$BBL" "$KRN" build/files/

if [ ! -f "build/pako.min.js" ]; then
  wget -q "https://cdn.jsdelivr.net/npm/pako@2.1.0/dist/pako.min.js" -O "build/pako.min.js"
fi

echo "Empacotando arquivos e gerando SVG..."
python3 embed_files.py file_template.js build/files/ build/files.js
cat build/pako.min.js build/files.js pdflinux.js "$EMU" > out/compiled.js
python3 gen_svg.py out/compiled.js out/linux.svg

python3 - << 'PYEOF'
from pathlib import Path

p = Path("out/linux.svg")
txt = p.read_text(encoding="utf-8")

old = "  if (scriptDirectory.indexOf('blob:') !== 0) {"
new = (
    "  if (typeof scriptDirectory === 'undefined' || !scriptDirectory) { "
    "scriptDirectory = (typeof window !== 'undefined' && window.location && window.location.href) ? window.location.href : ''; "
    "}\n" + old
)
if old in txt and new not in txt:
    txt = txt.replace(old, new, 1)

txt = txt.replace("scriptDirectory.indexOf(", "(scriptDirectory || '').indexOf(")
txt = txt.replace("locateFile(path).indexOf(", "(locateFile(path) || '').indexOf(")

p.write_text(txt, encoding="utf-8")
PYEOF

if [ -d "$(dirname "$OUT_WIN")" ]; then
  cp out/linux.svg "$OUT_WIN"
fi

chown -R "$OWNER_USER:$OWNER_USER" build out 2>/dev/null || true

ls -lh out/compiled.js out/linux.svg "$OUT_WIN" 2>/dev/null || ls -lh out/compiled.js out/linux.svg
echo "Build concluido com sucesso."
