# Project Log & Technical Engineering Record

**Project**: One Piece Grand Battle 2 (PS1) English Translation & ROM Hacking  
**Target Game**: *From TV Animation One Piece: Grand Battle! 2 (Japan)* (`SLPS-034.08`)  
**Publisher / Developer**: Bandai / Ganbarion (March 2002)  
**Repository**: [https://github.com/syarief02/one-piece-grand-battle-2-ps1-translation](https://github.com/syarief02/one-piece-grand-battle-2-ps1-translation)

---

## 📅 Chronological Development Log

### Phase 1: Environment Setup & Disc Extraction
- Located `chdman.exe` and converted `From TV Animation One Piece - Grand Battle 2 (Japan).chd` to raw `grand_battle_2.bin` (733,687,584 bytes) and `grand_battle_2.cue`.
- Disc layout:
  - Track 1: Data track (MODE2/2352 Form 1 & Form 2)
  - Track 2: Audio track
- Built `tools/extract_iso.py` to parse ISO 9660 filesystem records from sector 16 (Primary Volume Descriptor).
- Extracted 31 files into `extracted/`: `SLPS_034.08`, `OP.APF`, `OP.DAT`, `OP2.DAT`, `SYSTEM.CNF`, `STR/01.STR` to `STR/25.STR`.

### Phase 2: Binary Scanning & Archive Reverse Engineering
- Built `tools/scan_text.py` and `tools/deep_scan.py` to scan for Shift-JIS strings.
- Discovered and decoded the `APF_v2.0` archive format:
  - Header: `APF_v2.0`, `404` subfiles, `19000` total sectors.
  - Sector index table at `0x0800` (sector 1) with 404 32-bit little-endian sector offsets.
  - First subfile data begins at LBA `1704` (`0x00354000`).
- Discovered `DAT\x00` archive containers in `OP.DAT` (1,322 subfiles) and `OP2.DAT` (15 subfiles) using 16-byte record tables.

### Phase 3: Archive Unpacking & Subfile Cataloging
- Built `tools/unpack_apf.py`: Unpacked all 404 assets into `extracted/apf_unpacked/`.
- Built `tools/catalog_unpacked.py`: Cataloged all subfiles into `_apf_manifest.txt` and `_text_inventory.csv`.
- Located character moveset text tables in `file_104` to `file_210` (`必殺技`, `火炎星`, `ゴムゴム`).

### Phase 4: Patching & Disc Rebuilding Toolchain
- Built `tools/patch_strings.py`: Safe length-bounded string replacement with null padding.
- Built `tools/repack_apf.py`: Recompiles `OP.APF` container preserving sector alignment and LBA tables.
- Built `tools/rebuild_iso.py`: Injects modified files and recalculates 32-bit Mode 2 Form 1 EDC checksums.
- Built `tools/build_patch.py`: End-to-end automated pipeline producing `build/grand_battle_2_en.bin` and `build/grand_battle_2_en.cue`.
- Built `tools/create_patch.py`: Generates lightweight binary delta patch `build/grand_battle_2_en.patch`.
- Built single compressed `.chd` ROM: `build/One Piece - Grand Battle 2 (English Patched).chd`.

### Phase 5: Graphical Texture & UI Reverse Engineering
- Analyzed why initial ROM displayed Japanese menus: discovered that title screens and menu options ("Grand Battle", "Story Mode", "Training", "Option", "Character Select") are **pre-rendered 2D `.TIM` image bitmaps** drawn directly into VRAM, not rendered via font strings.
- Built `tools/tim_tool.py`: Decodes PlayStation 1 `.TIM` images (4-bit CLUT, 8-bit, 16-bit BGR555, 24-bit RGB) to `.PNG` and encodes `.PNG` back to `.TIM`.
- Built `tools/extract_all_textures.py`: Extracted 2D UI texture sheets to `extracted/textures/` for graphical translation in image editors.

---

## 📝 Technical Notes & Offsets

### PS1 Disc LBA Sector Map
| Asset | LBA Sector | Sector Count | Byte Size |
|---|---|---|---|
| `SLPS_034.08` | 23 | 142 | 290,816 B |
| `OP.APF` | 165 | 48,206 | 98,724,136 B |
| `SYSTEM.CNF` | 48,371 | 1 | 64 B |
| `OP2.DAT` | 48,372 | 62,848 | 128,712,704 B |
| `OP.DAT` | 111,220 | 139,280 | 285,245,440 B |
| `STR/01.STR` | 250,501 | 2,170 | 4,550,656 B |

---

## 📌 Contributor Instructions for Adding Translations

1. **Menu Textures**:
   - Edit the PNG images in `extracted/textures/` using Photoshop or GIMP.
   - Run `python tools/tim_tool.py` to re-encode them.
2. **Text / Dialogue**:
   - Add new entries to `DEFAULT_TRANSLATIONS` in `tools/patch_strings.py`.
3. **Build**:
   - Run `python tools/build_patch.py` to produce updated `.bin/.cue` and `.chd` files.
