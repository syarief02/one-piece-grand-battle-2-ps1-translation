# Project Log & Technical Engineering Record

**Project**: One Piece Grand Battle 2 (PS1) English Translation & ROM Hacking  
**Target Game**: *From TV Animation One Piece: Grand Battle! 2 (Japan)* (`SLPS-034.08`)  
**Publisher / Developer**: Bandai / Ganbarion (2002)

---

## 📅 Chronological Development Log

### Phase 1: Environment Setup & Disc Extraction
- Located `chdman.exe` in `C:\Users\User\OneDrive\Desktop\namDHC_v200\chdman.exe`.
- Decompressed `From TV Animation One Piece - Grand Battle 2 (Japan).chd` to `grand_battle_2.bin` (733,687,584 bytes) and `grand_battle_2.cue`.
- Disc layout confirmed:
  - Track 1: Data track (MODE2/2352 Form 1 & Form 2)
  - Track 2: Audio track
- Built `tools/extract_iso.py` to parse ISO 9660 filesystem records from sector 16 (Primary Volume Descriptor).
- Extracted 31 files into `extracted/`:
  - `SLPS_034.08` (290,816 bytes)
  - `OP.APF` (98,724,136 bytes)
  - `OP.DAT` (285,245,440 bytes)
  - `OP2.DAT` (128,712,704 bytes)
  - `SYSTEM.CNF`
  - `STR/01.STR` to `STR/25.STR` (PSX CD-XA video files)

### Phase 2: Binary Scanning & Reverse Engineering
- Built `tools/scan_text.py` and `tools/deep_scan.py` to scan for Shift-JIS strings and known Japanese character names (Luffy, Zoro, Nami, Usopp, Sanji, Chopper, etc.).
- **Crucial finding**: Character names and move data were found inside `OP.APF` (`APF_v2.0` container format), whereas `SLPS_034.08` contained engine debug symbols and C source filenames (`gpuman.h`, `LP_MODEL.C`, `DISPBMP.C`, `TOP_MENU.C`, `OPT_MENU.C`, `TRE_MENU.C`).
- Decoded the `APF_v2.0` archive format:
  - Offset `0x00`: ASCII `APF_v2.0`
  - Offset `0x08`: 32-bit UInt `404` (number of subfiles)
  - Offset `0x10`: 32-bit UInt `19000` (total sector count = 38,912,000 bytes)
  - Offset `0x800` (Sector 1): Sector LBA lookup table (404 32-bit little-endian entries).
  - First subfile data begins at LBA `1704` (`0x00354000`).

### Phase 3: Archive Unpacking & Subfile Cataloging
- Built `tools/unpack_apf.py`: Successfully extracted all 404 assets into `extracted/apf_unpacked/`.
- Built `tools/catalog_unpacked.py`: Cataloged all subfiles, generating `_apf_manifest.txt` and `_text_inventory.csv`.
- Identified key subfiles containing text strings:
  - `file_001` - `file_030`: Menu/Story buffers with Shift-JIS text.
  - `file_104` - `file_210`: Character moveset and special attack text tables (`必殺`, `火炎星`, `ゴムゴム`).

### Phase 4: Patching & Disc Rebuilding Toolchain
- Built `tools/patch_strings.py`: Implemented length-bounded string replacement with null-byte padding to prevent pointer corruption.
- Built `tools/repack_apf.py`: Implemented full `APF_v2.0` container rebuild, preserving the preamble and updating LBA sector tables.
- Built `tools/rebuild_iso.py`: Implemented Mode 2 Form 1 sector injection and 32-bit EDC (Error Detection Code) recalculation.
- Built `tools/build_patch.py`: End-to-end automated pipeline builder that generates `build/grand_battle_2_en.bin` and `build/grand_battle_2_en.cue`.
- Built `tools/create_patch.py`: Created lightweight binary delta patch generator producing `build/grand_battle_2_en.patch`.

---

## 📝 Technical Notes & Offsets

### PS1 ISO LBA Allocation
| Asset | LBA Offset | Sector Count |
|---|---|---|
| `SLPS_034.08` | 23 | 142 |
| `OP.APF` | 165 | 48,206 |
| `SYSTEM.CNF` | 48,371 | 1 |
| `OP2.DAT` | 48,372 | 62,848 |
| `OP.DAT` | 111,220 | 139,280 |
| `STR/01.STR` | 250,501 | 2,170 |

---

## 📌 Next Steps for Future Contributors
1. Add more string mappings in `DEFAULT_TRANSLATIONS` in `tools/patch_strings.py`.
2. Inspect `file_000` through `file_020` in `extracted/apf_unpacked/` to extract and document font TIM texture maps.
3. Test builds on DuckStation emulator with CD-XA audio playback enabled.
