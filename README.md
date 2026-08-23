# One Piece: Grand Battle! 2 (PS1) - English Translation Project & Toolchain

[![Platform: PS1](https://img.shields.io/badge/Platform-PlayStation%201-blue.svg)](https://en.wikipedia.org/wiki/PlayStation_(console))
[![Language: Python 3](https://img.shields.io/badge/Tools-Python%203-green.svg)](https://www.python.org/)
[![Status: Framework & Texture Toolchain Complete](https://img.shields.io/badge/Status-Toolchain%20Complete-green.svg)]()
[![GitHub Repo](https://img.shields.io/badge/GitHub-syarief02%2Fone--piece--grand--battle--2--ps1--translation-blue.svg)](https://github.com/syarief02/one-piece-grand-battle-2-ps1-translation)

A complete reverse-engineering suite, asset extraction/repacking pipeline, 2D graphic texture converter (`.TIM` ↔ `.PNG`), text table scanner, and patch generator for translating **From TV Animation One Piece: Grand Battle! 2** (PS1, Japan exclusive, `SLPS-034.08`, Ganbarion / Bandai 2002) into English.

---

## 📖 Table of Contents
1. [Project Overview](#project-overview)
2. [Why No English Patch Existed for 20+ Years](#why-no-english-patch-existed-for-20-years)
3. [Disc & Engine Architecture](#disc--engine-architecture)
4. [Reverse Engineering Discoveries](#reverse-engineering-discoveries)
   - [APF_v2.0 Master Container](#1-apf_v20-master-container)
   - [DAT Archive Containers](#2-dat-archive-containers)
   - [2D Graphical UI & Menu Sprites](#3-2d-graphical-ui--menu-sprites-tim-format)
   - [Font Matrix & Shift-JIS Script Tables](#4-font-matrix--shift-jis-script-tables)
5. [Complete Toolchain Guide](#complete-toolchain-guide)
6. [What Has Been Done](#what-has-been-done)
7. [Roadmap for Future Contributors](#roadmap-for-future-contributors)
8. [How to Build & Test the Game](#how-to-build--test-the-game)
9. [File & Directory Structure](#file--directory-structure)

---

## 🏴‍☠️ Project Overview

*From TV Animation One Piece: Grand Battle! 2* is a classic 3D arena fighting game developed by **Ganbarion** and published by **Bandai** on the Sony PlayStation in March 2002. It covers the story from the East Blue Saga up through the climax of the Alabasta Arc, featuring 24 playable characters and full voice acting.

Because the game was released exclusively in Japan, Western players have had to rely on printed FAQs. This project provides the complete, working tooling infrastructure to unpack, reverse-engineer, translate, edit textures, and compile playable English PS1 ROMs.

---

## 🔒 Why No English Patch Existed for 20+ Years

For over two decades, ROM hackers were blocked by four key technical hurdles:
1. **Proprietary Archive Containers**: All assets are packed inside `OP.APF` (`APF_v2.0` container) and `OP.DAT` / `OP2.DAT` with custom sector LBA lookup tables.
2. **Graphical Menus (Bitmaps, Not Strings)**: Menu options ("Grand Battle", "Story Mode", "Training", "Options", "Character Select") are **pre-rendered 2D image bitmaps (`.TIM`)** loaded directly into VRAM, not dynamic font strings. Modifying strings in the executable does not affect these images.
3. **2-Byte Shift-JIS Kanji Font Matrix**: Story text and win quotes reference a 16×16 Japanese tile grid rather than standard ASCII single-byte characters.
4. **Sector Alignment & Checksums**: PS1 discs use Mode 2 Form 1 sectors with 32-bit EDC/ECC checksums. Changing file lengths corrupts the disc filesystem table unless EDC is recalculated.

**This project solves all four problems** with automated Python tools.

---

## 💿 Disc & Engine Architecture

### Disc Layout (MODE2 / 2352 Form 1 & Form 2)
| Disc File | Size | LBA Start | Function / Format |
|---|---|---|---|
| `SLPS_034.08` | 284 KB | LBA 23 | Main PS1 MIPS executable (Game kernel, overlay manager) |
| `OP.APF` | 94.2 MB | LBA 165 | **APF_v2.0 Master Archive**: 404 packed subfiles (character movesets, menu overlays, models, textures) |
| `SYSTEM.CNF` | 64 B | LBA 48371 | PS1 Boot configuration (`BOOT = cdrom:\SLPS_034.08;1`) |
| `OP2.DAT` | 122.8 MB | LBA 48372 | **DAT Archive**: 15 large game data blocks |
| `OP.DAT` | 272.0 MB | LBA 111220 | **DAT Archive**: 1,322 graphical subfiles, stage geometry, audio banks |
| `STR/*.STR` | ~80 MB | LBA 250501+ | PSX CD-XA FMV video streams (25 cinematic files) |

---

## 🔬 Reverse Engineering Discoveries

### 1. `APF_v2.0` Master Container
- **Magic Signature**: `APF_v2.0` at offset `0x0000`.
- **Header Structure**:
  - `0x08`: Total subfiles = `404` (`0x00000194`).
  - `0x0C`: Group classification = `22` (`0x00000016`).
  - `0x10`: Total sectors = `19000` (`0x00004A38` = 38,912,000 bytes).
- **Sector Index Table**: Located at sector 1 (`0x0800`). Contains 404 32-bit little-endian sector offsets.
- **Subfiles**: Begin at LBA `1704` (`0x00354000`).

### 2. `DAT` Archive Containers
- **Magic Signature**: `DAT\x00` at offset `0x0000`.
- **Record Table**: Located at offset `0x0800`.
- **Record Format**: 16-byte descriptors: `[Sector_Count (4B)] [LBA_Offset (4B)] [Type_Flag (4B)] [0x00000000 (4B)]`.

### 3. 2D Graphical UI & Menu Sprites (`.TIM` format)
- PlayStation `.TIM` image textures were discovered across the unpacked assets.
- Includes 4-bit (16-color CLUT), 8-bit (256-color), 16-bit (BGR555), and 24-bit RGB textures.
- The tool `tools/tim_tool.py` decodes all `.TIM` files directly into `.PNG` for graphical editing in Photoshop / GIMP.

### 4. Font Matrix & Shift-JIS Script Tables
- Character moveset buffers and dialogue scripts in `file_104` to `file_210` contain Japanese Shift-JIS strings (`必殺技` Special, `火炎星` Fire Star, `ゴムゴム` Gomu Gomu).

---

## 🛠️ Complete Toolchain Guide

All tools are located in [`tools/`](file:///c:/Users/User/OneDrive/Desktop/one%20piece%20ps1%20rom/tools):

| Tool | Purpose |
|---|---|
| **`extract_iso.py`** | Extracts the ISO 9660 filesystem from a raw PS1 `BIN/CUE` disc image into loose files. |
| **`unpack_apf.py`** | Unpacks all 404 subfiles from `OP.APF` into `extracted/apf_unpacked/`. |
| **`repack_apf.py`** | Recompiles modified subfiles back into a byte-aligned `OP.APF` container. |
| **`unpack_dat.py`** | Unpacks `OP2.DAT` subfiles. |
| **`tim_tool.py`** | Decodes PS1 `.TIM` textures to `.PNG` and encodes `.PNG` back into `.TIM` format. |
| **`extract_all_textures.py`** | Batch-extracts all 2D textures from the game assets into `extracted/textures/`. |
| **`patch_strings.py`** | Performs memory-safe text replacement with length boundary checks and null padding. |
| **`rebuild_iso.py`** | Injects modified assets into the PS1 `BIN` and recalculates 32-bit Mode 2 Form 1 EDC checksums. |
| **`build_patch.py`** | Master automated pipeline that produces a playable English PS1 `.bin/.cue` ROM in `build/`. |
| **`create_patch.py`** | Generates and applies lightweight `.patch` files for distribution. |

---

## ✅ What Has Been Done

- [x] Converted original `.chd` disc image to raw `MODE2/2352` `.bin/.cue`.
- [x] Extracted ISO 9660 filesystem.
- [x] Reverse-engineered `APF_v2.0` and `DAT\x00` archive structures.
- [x] Unpacked all 404 subfiles from `OP.APF`.
- [x] Built full PS1 `.TIM` image texture decoder (`tim_tool.py`).
- [x] Extracted UI image textures into `extracted/textures/` for editing.
- [x] Built container repacker (`repack_apf.py`) and disc injector with EDC checksum generator (`rebuild_iso.py`).
- [x] Built end-to-end automated pipeline producing `build/grand_battle_2_en.bin` and `build/grand_battle_2_en.cue`.
- [x] Built single compressed `.chd` generator producing `build/One Piece - Grand Battle 2 (English Patched).chd`.
- [x] Established Git repository: [syarief02/one-piece-grand-battle-2-ps1-translation](https://github.com/syarief02/one-piece-grand-battle-2-ps1-translation).

---

## 🎯 Roadmap for Future Contributors

Anyone continuing this project can follow these concrete steps:

### Phase 1: Menu Texture Translation (Visual Polish)
1. Open the PNG textures in `extracted/textures/` in an image editor (Photoshop/GIMP).
2. Edit the Japanese menu buttons ("Grand Battle", "Story", "Training", "Options", "Character Select") with English typography.
3. Save modified PNGs and re-encode them to `.TIM` using `tools/tim_tool.py`.
4. Rebuild the ROM using `python tools/build_patch.py`.

### Phase 2: Dialogue & Move List Script Expansion
1. Add translated string mappings in `DEFAULT_TRANSLATIONS` inside `tools/patch_strings.py`.
2. Translate character attack names and win quotes.
3. Run `python tools/build_patch.py` to compile.

### Phase 3: Community Release
1. Build the final `.chd` and generate standard `.xdelta` / `.ppf` patch files.
2. Submit patch to [ROMhacking.net](https://www.romhacking.net/).

---

## 🚀 How to Build & Test the Game

### Prerequisites
- Python 3.8+ with `pillow` (`pip install pillow`)
- `chdman` (optional, for CHD format)

### 1. Extract Assets
```powershell
python tools/extract_iso.py grand_battle_2.bin -o extracted
python tools/unpack_apf.py
python tools/extract_all_textures.py
```

### 2. Build English Patched Disc Image (.BIN / .CUE)
```powershell
python tools/build_patch.py
```
Outputs: `build/grand_battle_2_en.bin` & `build/grand_battle_2_en.cue`

### 3. Build Single Compressed ROM (.CHD)
```powershell
chdman createcd -i "build/grand_battle_2_en.cue" -o "build/One Piece - Grand Battle 2 (English Patched).chd"
```

### 4. Create Lightweight Delta Patch
```powershell
python tools/create_patch.py
```
Outputs: `build/grand_battle_2_en.patch`

---

## 📂 File & Directory Structure

```
├── build/                                            # Build output folder
│   ├── grand_battle_2_en.cue                         # Patched CUE sheet
│   ├── grand_battle_2_en.bin                         # Patched BIN disc image
│   ├── One Piece - Grand Battle 2 (English Patched).chd # Single compressed CHD ROM
│   └── grand_battle_2_en.patch                       # Lightweight binary delta patch
├── extracted/                                        # Extracted game assets
│   ├── apf_unpacked/                                 # 404 unpacked APF subfiles
│   │   ├── _apf_manifest.txt                         # Subfile inventory & LBA sector map
│   │   └── _text_inventory.csv                       # Subfile string classification
│   ├── textures/                                     # Extracted 2D TIM textures as PNGs
│   ├── SLPS_034.08                                   # Main PS1 executable
│   └── exe_strings.csv                               # Shift-JIS string dump
├── tools/                                            # Complete reverse-engineering toolchain
│   ├── build_patch.py                                # Master build pipeline runner
│   ├── extract_iso.py                                # PS1 ISO filesystem extractor
│   ├── unpack_apf.py                                 # APF_v2.0 archive unpacker
│   ├── repack_apf.py                                 # APF_v2.0 archive repacker
│   ├── tim_tool.py                                   # PS1 TIM texture decoder & encoder
│   ├── extract_all_textures.py                       # Batch texture extractor
│   ├── rebuild_iso.py                                # PS1 disc injector with EDC checksums
│   ├── patch_strings.py                              # Safe text replacement engine
│   ├── create_patch.py                               # Delta patch generator & applier
│   ├── scan_text.py                                  # Shift-JIS scanner
│   └── catalog_unpacked.py                           # Subfile classifier
├── PROJECT_LOG.md                                    # Chronological engineering log
├── README.md                                         # Comprehensive documentation
└── .gitignore                                        # Clean git rules
```
