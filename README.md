## Build Instructions

Clone this repository and run the following commands:
```
git clone git@github.com:tcavalcante443/linuxsvg.git
cd ~/linuxsvg
python3 -m venv .venv
source .venv/bin/activate
pip3 install -r requirements.txt
chmod +x build_svg.sh
sudo ./build_svg.sh

## Credits

This project was based in linuxPDF by [@ading2210](https://github.com/ading2210/).

The RISC-V emulator is forked from [TinyEMU](https://bellard.org/tinyemu/), which was written by [Fabrice Bellard](https://bellard.org/).

## License

This repository is licensed under the GNU GPL v3.

```
tcavalcante443/linuxsvg - Linux running inside a SVG file
Copyright (C) 2026 tcavalcante443

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
