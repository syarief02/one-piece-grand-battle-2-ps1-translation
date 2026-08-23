#!/usr/bin/env python3
"""
Master Translation Patch Pipeline Builder for One Piece Grand Battle 2 (PS1).
Patches SLPS executable, all 6 OP.APF program overlays (O2KTOP, O2KOPT, O2KTRE),
and all 404 unpacked subfiles, then builds a full English BIN/CUE and CHD disc image.
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

# Add tools directory to path
tools_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(tools_dir))

from patch_strings import DEFAULT_TRANSLATIONS, patch_file, patch_binary
from repack_apf import repack_apf
from rebuild_iso import inject_file_to_bin

def run_pipeline():
    print("==========================================================")
    print("  ONE PIECE GRAND BATTLE 2 - PS1 ENGLISH PATCH PIPELINE   ")
    print("==========================================================")
    
    os.makedirs("build", exist_ok=True)
    
    # 1. Patch Main PS1 Executable (SLPS_034.08)
    print("\n[Step 1/5] Patching Main PS1 Executable (SLPS_034.08)...")
    c1 = patch_file("extracted/SLPS_034.08", "build/SLPS_034.08", DEFAULT_TRANSLATIONS)
    print(f"Patched {c1} occurrences in SLPS.")
    
    # 2. Patch Unpacked APF subfiles
    print("\n[Step 2/5] Patching APF Archive Subfiles (404 assets)...")
    unpacked_files = list(Path("extracted/apf_unpacked").glob("file_*.bin"))
    total_apf_patches = 0
    for uf in unpacked_files:
        count = patch_file(str(uf), str(uf), DEFAULT_TRANSLATIONS)
        total_apf_patches += count
    print(f"Total APF subfile text replacements applied: {total_apf_patches}")
    
    # 3. Repack OP.APF (with overlay patching for O2KTOP, O2KOPT, O2KTRE)
    print("\n[Step 3/5] Repacking OP.APF (with Preamble Overlays)...")
    repack_apf("extracted/apf_unpacked", "build/OP.APF", "extracted/OP.APF")
    
    # 4. Generate English Disc Image (grand_battle_2_en.bin)
    print("\n[Step 4/5] Generating English Disc Image (grand_battle_2_en.bin)...")
    src_bin = "grand_battle_2.bin"
    dest_bin = "build/grand_battle_2_en.bin"
    
    if not os.path.exists(dest_bin):
        print(f"Copying clean BIN to '{dest_bin}'...")
        shutil.copyfile(src_bin, dest_bin)
        
    # Inject patched SLPS (LBA 23)
    inject_file_to_bin(dest_bin, "build/SLPS_034.08", 23)
    
    # Inject patched OP.APF (LBA 165)
    inject_file_to_bin(dest_bin, "build/OP.APF", 165)
    
    # Create CUE sheet
    cue_content = """FILE "grand_battle_2_en.bin" BINARY
  TRACK 01 MODE2/2352
    INDEX 01 00:00:00
  TRACK 02 AUDIO
    INDEX 00 68:47:54
    INDEX 01 68:49:54
"""
    with open("build/grand_battle_2_en.cue", "w") as cue_f:
        cue_f.write(cue_content)
        
    # 5. Compile single compressed CHD format
    print("\n[Step 5/5] Compiling single lossless CHD ROM image...")
    chdman_path = r"C:\Users\User\OneDrive\Desktop\namDHC_v200\chdman.exe"
    out_chd = r"build\One Piece - Grand Battle 2 (English Patched).chd"
    
    if os.path.exists(chdman_path):
        cmd = [chdman_path, "createcd", "-i", "build/grand_battle_2_en.cue", "-o", out_chd, "--force"]
        print(f"Running chdman: {' '.join(cmd)}")
        subprocess.run(cmd, check=True)
    else:
        print("chdman.exe not found; skipping CHD conversion.")
        
    print("\n==========================================================")
    print("PATCH BUILD SUCCESSFUL!")
    print(f"Patched ROMs:")
    print(f"  1. CHD: build/One Piece - Grand Battle 2 (English Patched).chd")
    print(f"  2. BIN/CUE: build/grand_battle_2_en.cue & build/grand_battle_2_en.bin")
    print("==========================================================")

if __name__ == "__main__":
    run_pipeline()
