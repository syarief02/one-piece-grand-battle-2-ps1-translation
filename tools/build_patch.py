#!/usr/bin/env python3
"""
Full Translation Patch Pipeline Builder
Automates text patching, APF repacking, and ISO injection to produce a patched PS1 ROM.
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

# Add tools directory to path
tools_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(tools_dir))

from patch_strings import DEFAULT_TRANSLATIONS, patch_file
from repack_apf import repack_apf
from rebuild_iso import inject_file_to_bin

def run_pipeline():
    print("==========================================================")
    print("  ONE PIECE GRAND BATTLE 2 - PS1 ENGLISH PATCH PIPELINE   ")
    print("==========================================================")
    
    os.makedirs("build", exist_ok=True)
    
    # 1. Patch SLPS Executable
    print("\n[Step 1/4] Patching Main PS1 Executable (SLPS_034.08)...")
    c1 = patch_file("extracted/SLPS_034.08", "build/SLPS_034.08", DEFAULT_TRANSLATIONS)
    print(f"Patched {c1} occurrences in SLPS.")
    
    # 2. Patch Unpacked APF subfiles
    print("\n[Step 2/4] Patching APF Archive Subfiles...")
    unpacked_files = list(Path("extracted/apf_unpacked").glob("file_*.bin"))
    total_apf_patches = 0
    for uf in unpacked_files:
        count = patch_file(str(uf), str(uf), DEFAULT_TRANSLATIONS)
        total_apf_patches += count
    print(f"Total APF text replacements applied: {total_apf_patches}")
    
    # 3. Repack OP.APF
    print("\n[Step 3/4] Repacking OP.APF...")
    repack_apf("extracted/apf_unpacked", "build/OP.APF", "extracted/OP.APF")
    
    # 4. Create Patched BIN
    print("\n[Step 4/4] Generating English Disc Image (grand_battle_2_en.bin)...")
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
        
    print("\n==========================================================")
    print("PATCH BUILD SUCCESSFUL!")
    print(f"Patched ROM: build/grand_battle_2_en.cue & build/grand_battle_2_en.bin")
    print("==========================================================")

if __name__ == "__main__":
    run_pipeline()
