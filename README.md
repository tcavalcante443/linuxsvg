# LinuxPDF

This is Linux running inside a PDF file via a RISC-V emulator, which is based on [TinyEMU](https://bellard.org/tinyemu/).

Try it here: [linux.pdf](https://linux.doompdf.dev/linux.pdf)

https://github.com/user-attachments/assets/7e992dd1-41a5-4d32-87cc-878b395e3d92

See also: [DoomPDF](https://github.com/ading2210/doompdf)

## Explanation

This works in a very similar way to my previous [DoomPDF](https://github.com/ading2210/doompdf) project.

You might expect PDF files to only be comprised of static documents, but surprisingly, the PDF file format supports Javascript with its own separate standard library. Modern browsers (Chromium, Firefox) implement this as part of their PDF engines. However, the APIs that are available in the browser are much more limited. 

The full specfication for the JS in PDFs was only ever implemented by Adobe Acrobat, and it contains some ridiculous things like the ability to do [3D rendering](https://opensource.adobe.com/dc-acrobat-sdk-docs/library/jsapiref/JS_API_AcroJS.html#annot3d), make [HTTP requests](https://opensource.adobe.com/dc-acrobat-sdk-docs/library/jsapiref/JS_API_AcroJS.html#net-http), and [detect every monitor connected to the user's system](https://opensource.adobe.com/dc-acrobat-sdk-docs/library/jsapiref/JS_API_AcroJS.html#monitor). However, on Chromium and other browsers, only a tiny subset of this API was ever implemented, due to obvious security concerns. With this, we can do whatever computation we want, just with some very limited IO.

C code can be compiled to run within a PDF using an old version of Emscripten that targets [asm.js](https://en.wikipedia.org/wiki/Asm.js) instead of WebAssembly. With this, I can compile a modified version of the TinyEMU RISC-V emulator to asm.js, which can be run within the PDF. For the input and output, I reused the same display code that I used for DoomPDF. It works by using a separate text field for each row of pixels in the screen, whose contents are set to various ASCII characters. For inputs, there is a virtual keyboard implemented with a bunch of buttons, and a text box you can type in to send keystrokes to the VM.

The largest problem here is with the emulator's performance. For example, the Linux kernel takes about 30-60 seconds to boot up within the PDF, which over 100x slower than normal. Unfortunately, there's no way to fix this, since the version of V8 that Chrome's PDF engine uses has its [JIT compiler disabled](https://source.chromium.org/chromium/_/pdfium/pdfium/+/012fe571c9fe430da68dbcd2f5ba21758db0ae15:fpdfsdk/fpdf_view.cpp;l=1211-1214;drc=b69783fd189976dd4625c7dcd9c07921b94d4a3c;bpv=0;bpt=0), destroying its performance.

For the root filesystem, there are both 64 and 32 bit versions possible. The default is a 32 bit buildroot system (which was prebuilt and taken from the original TinyEMU examples), and also a 64 bit Alpine Linux system. The 64 bit emulator is about twice as slow however, so it's normally not used. 

## Build Instructions

Clone this repository and run the following commands:
```
git clone git@github.com:tcavalcante443/linuxsvg.git
cd ~/linuxsvg
export BITS=32
mkdir -p build out build/files

sudo apt update && sudo apt install -y libc6-dev

chmod +x init build/root/sbin/init 2>/dev/null || true

gcc tinyemu/build_filelist.c tinyemu/fs_utils.c tinyemu/cutils.c -o build/build_files

rm -rf build/files/root
mkdir -p build/files/root
sudo ./build/build_files build/root build/files/root
sudo chown -R "$USER:$USER" build/files

BBL=$(find . -maxdepth 4 -name "bbl${BITS}.bin" 2>/dev/null | head -n 1)
KRN=$(find . -maxdepth 4 -name "kernel-riscv${BITS}.bin" 2>/dev/null | head -n 1)
EMU=$(find . -maxdepth 4 -name "riscvemu${BITS}.js" 2>/dev/null | head -n 1)

cp "vm_${BITS}.cfg" "$BBL" "$KRN" build/files/

python3 embed_files.py file_template.js build/files/ build/files.js
cat build/pako.min.js build/files.js pdflinux.js "$EMU" > out/compiled.js
python3 gen_svg.py out/compiled.js out/linux.svg

python3 - << 'EOF'
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
EOF

cp out/linux.svg /mnt/c/Users/Public/linux.svg
ls -lh build/build_files build/files/root build/files.js out/compiled.js out/linux.svg /mnt/c/Users/Public/linux.svg
fimmm
# Garante permissão de execução no script init do rootfs
chmod +x build/root/sbin/init 2>/dev/null || true
```
If you want to build the 64 bit rather than 32 bit version, edit `build.sh` and change the `BITS="32"` line.

The `build.sh` script will download Emscripten `1.39.20` automatically. You must be on Linux to build this. 

The generated files will be in the `out/` directory. Then you can run `(cd out; python3 -m http.server)` to serve the files on a web server.

## Credits

This project was made by [@ading2210](https://github.com/ading2210/).

The RISC-V emulator is forked from [TinyEMU](https://bellard.org/tinyemu/), which was written by [Fabrice Bellard](https://bellard.org/).

## License

This repository is licensed under the GNU GPL v3.

```
ading2210/linuxpdf - Linux running inside a PDF file
Copyright (C) 2025 ading2210

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
```
