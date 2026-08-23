# One Piece: Grand Battle! 2 (PS1) - English Translation Project & Toolchain

[![Platform: PS1](https://img.shields.io/badge/Platform-PlayStation%201-blue.svg)](https://en.wikipedia.org/wiki/PlayStation_(console))
[![Language: Python 3](https://img.shields.io/badge/Tools-Python%203-green.svg)](https://www.python.org/)
[![Status: Reverse-Engineering & Patch Framework](https://img.shields.io/badge/Status-Framework%20Complete-orange.svg)]()

A complete reverse-engineering suite, asset extraction/repacking pipeline, text table scanner, and patch generator for translating **From TV Animation One Piece: Grand Battle! 2** (PS1, Japan exclusive, `SLPS-034.08`, Ganbarion / Bandai 2002) into English.

---

## 📖 Table of Contents
1. [Project Overview](#project-overview)
2. [Disc & Engine Architecture](#disc--engine-architecture)
3. [Reverse Engineering Discoveries](#reverse-engineering-discoveries)
4. [Toolchain & Workflow](#toolchain--workflow)
5. [What Has Been Done](#what-has-been-done)
6. [What Needs To Be Done (Roadmap)](#what-needs-to-be-done-roadmap)
7. [How to Build & Apply the Patch](#how-to-build--apply-the-patch)
8. [File Structure](#file-structure)
9. [Contributing / Continuing the Project](#contributing--continuing-the-project)

---

## 🏴‍☠️ Project Overview

*From TV Animation One Piece: Grand Battle! 2* is a beloved 3D fighting game developed by **Ganbarion** and published by **Bandai** on the Sony PlayStation in 2002. It was released exclusively in Japan.

For over two decades, no full English translation patch was created due to Ganbarion's proprietary container (`APF_v2.0` / `.pac`), compressed font tilesets, and pointer tables. This project provides the complete, working tooling infrastructure to unpack, translate, repack, and build patched PS1 ROMs.

---

## 💿 Disc & Engine Architecture

### Disc Layout (MODE2 / 2352 Form 1 & Form 2)
| Disc File | Size | LBA Start | Function / Format |
|---|---|---|---|
| `SLPS_034.08` | 284 KB | LBA 23 | Main PS1 MIPS executable (Game kernel, debug symbols, overlay loader) |
| `OP.APF` | 94.2 MB | LBA 165 | **APF_v2.0 Container**: 404 packed subfiles (`.pac`, character movesets, menu text, models, TIM graphics) |
| `OP2.DAT` | 122.8 MB | LBA 48372 | Secondary game data archive |
| `OP.DAT` | 272.0 MB | LBA 111220 | Primary graphical assets, stages, sound banks |
| `STR/*.STR` | Various | LBA 250501+ | PSX FMV CD-XA streaming video tracks (25 cinematic files) |
| `SYSTEM.CNF` | 64 B | LBA 48371 | Boot config (`BOOT = cdrom:\SLPS_034.08;1`, `STACK = 801FFF00`) |

---

## 🔬 Reverse Engineering Discoveries

### 1. `APF_v2.0` Container Structure
`OP.APF` is Ganbarion's master archive container.
- **Magic**: `APF_v2.0` (8 bytes) at offset `0x0000`.
- **Header Fields**:
  - `0x08`: Subfile count (UInt32 LE) = `404` (`0x00000194`).
  - `0x0C`: Group count (UInt32 LE) = `22` (`0x00000016`).
  - `0x10`: Total sectors (UInt32 LE) = `19000` (`0x00004A38`).
- **LBA Index Table**: Begins at sector 1 (`0x0800`).
  - Contains 404 32-bit little-endian sector offsets.
  - Data subfiles begin at LBA `1704` (`0x00354000`).
  - Each subfile length = `(LBA[i+1] - LBA[i]) * 2048` bytes.

### 2. Internal Subfiles & Character Move Data
- Found uncompressed Shift-JIS character data in `file_104` to `file_210` (`title/chrdata/c%03d.pac`):
  - Character attack names (e.g. `火炎星` Fire Star, `ゴムゴム` Gomu Gomu, `必殺` Special).
  - Story dialogue buffers and ending credits scripts (`event/ending/EdSys.pac`).
  - Menu text buffers (`TOPMENU2`, `OPTIONS2`, `TREASURE MODE`).

---

## 🛠️ Toolchain & Workflow

All tools are located in [`tools/`](file:///c:/Users/User/OneDrive/Desktop/one%20piece%20ps1%20rom/tools):

1. **`extract_iso.py`**: Extracts the ISO 9660 filesystem from a raw PS1 `BIN/CUE` disc image into loose files.
2. **`unpack_apf.py`**: Unpacks all 404 subfiles from `OP.APF` using the LBA sector lookup table into [`extracted/apf_unpacked/`](file:///c:/Users/User/OneDrive/Desktop/one%20piece%20ps1%20rom/extracted/apf_unpacked).
3. **`scan_text.py` & `catalog_unpacked.py`**: Scans all subfiles and executables for Shift-JIS / ASCII strings, generating inventory CSV tables.
4. **`patch_strings.py`**: Performs memory-safe text replacement with length boundary checks and null padding to preserve pointer tables.
5. **`repack_apf.py`**: Rebuilds the `OP.APF` container, recalculates sector tables, and pads boundaries.
6. **`rebuild_iso.py`**: Injects modified files (`SLPS_034.08`, `OP.APF`) into the PS1 `BIN` and recalculates 32-bit EDC checksums over Mode 2 Form 1 sectors.
7. **`build_patch.py`**: Automated pipeline runner that executes the entire workflow from loose translations to a playable English PS1 `.bin/.cue` ROM.
8. **`create_patch.py`**: Generates and applies lightweight `.patch` files for distribution.

---

## ✅ What Has Been Done

- [x] Converted original `.chd` to raw `.bin/.cue` image with `chdman`.
- [x] Extracted ISO 9660 filesystem (`SLPS_034.08`, `OP.APF`, `OP.DAT`, `OP2.DAT`, `SYSTEM.CNF`, `STR/`).
- [x] Reverse-engineered the `APF_v2.0` archive format and LBA sector index table.
- [x] Unpacked all 404 internal assets from `OP.APF`.
- [x] Built Shift-JIS text scanning and string cataloging tools.
- [x] Located character move descriptions, menu identifiers, and system strings.
- [x] Built the `repack_apf.py` container compiler.
- [x] Built the `rebuild_iso.py` PS1 disc image injector with EDC checksum generation.
- [x] Built the master `build_patch.py` pipeline.
- [x] Built lightweight binary delta patch generator (`create_patch.py`).
- [x] Verified end-to-end building of `build/grand_battle_2_en.bin` & `build/grand_battle_2_en.cue`.

---

## 🎯 What Needs To Be Done (Roadmap)

Anyone taking over or contributing can tackle the following milestones:

### Phase 1: Text Translation Expansion
- [ ] Expand dictionary entries in `tools/patch_strings.py` to cover all character move names.
- [ ] Translate all menu options (`OPTIONS2/OPT_MENU.C` and `TOPMENU2/TOP_MENU.C`).
- [ ] Translate Grand Battle story mode dialogues located in `file_001` through `file_030`.

### Phase 2: Font Tile Modification (Optional for Variable Width Font)
- [ ] Locate font tileset TIM graphics within `file_000` - `file_020`.
- [ ] Modify font textures to ensure full Latin / ASCII character set rendering.

### Phase 3: Release & Distribution
- [ ] Generate standard `xdelta` or `PPF` patch files for community emulators (DuckStation, PCSX-Redux, Beetle PSX).
- [ ] Publish patch on ROMhacking.net / GitHub releases.

---

## 🚀 How to Build & Apply the Patch

### Prerequisites
- Python 3.8+
- Clean original Japanese ROM (`From TV Animation One Piece - Grand Battle 2 (Japan)`) in `.bin/.cue` or `.chd` format.

### Step 1: Extract Disc Assets (First time only)
```powershell
python tools/extract_iso.py grand_battle_2.bin -o extracted
python tools/unpack_apf.py
```

### Step 2: Build the English Patched ROM
```powershell
python tools/build_patch.py
```
This produces `build/grand_battle_2_en.bin` and `build/grand_battle_2_en.cue`.

### Step 3: Create a Shareable Delta Patch
```powershell
python tools/create_patch.py
```
This produces `build/grand_battle_2_en.patch`.

---

## 📂 File Structure

```
├── build/                      # Build output folder
│   └── grand_battle_2_en.patch # Lightweight binary patch file
├── extracted/                  # Extracted disc files & manifests
│   ├── apf_unpacked/           # 404 unpacked APF subfiles
│   │   ├── _apf_manifest.txt   # File inventory with sector LBA offsets
│   │   └── _text_inventory.csv # Text string scan inventory
│   ├── SLPS_034.08             # PS1 executable
│   ├── SYSTEM.CNF              # Disc configuration
│   └── exe_strings.csv         # Shift-JIS & ASCII dump
├── tools/                      # Reverse engineering & patch toolchain
│   ├── build_patch.py          # Master automated build pipeline
│   ├── extract_iso.py          # PS1 MODE2/2352 ISO filesystem extractor
│   ├── unpack_apf.py           # APF_v2.0 archive unpacker
│   ├── repack_apf.py           # APF_v2.0 archive repacker
│   ├── rebuild_iso.py          # PS1 disc image injector with EDC checksums
│   ├── patch_strings.py        # Safe text replacement engine
│   ├── create_patch.py         # Delta patch generator & applier
│   ├── scan_text.py            # Shift-JIS string scanner
│   ├── catalog_unpacked.py     # Subfile string classifier
│   └── analyze_regions.py      # Memory region inspector
├── PROJECT_LOG.md              # Chronological engineering log
├── README.md                   # This documentation
└── .gitignore                  # Git ignore rules for large disc binaries
```

---

## 🤝 Contributing / Continuing the Project

If you want to contribute:
1. Fork this repository.
2. Edit `tools/patch_strings.py` or the CSV files in `extracted/` to add new translations.
3. Test your build using `python tools/build_patch.py` and run `build/grand_battle_2_en.cue` in DuckStation / ePSXe.
4. Submit a Pull Request!
