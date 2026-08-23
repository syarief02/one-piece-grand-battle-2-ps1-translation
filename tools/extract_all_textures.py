#!/usr/bin/env python3
"""
Batch extract all TIM graphics from all 404 unpacked APF files.
"""

import os
import sys
from pathlib import Path
from tim_tool import extract_all_tims_from_file

def batch_extract():
    out_dir = "extracted/textures"
    os.makedirs(out_dir, exist_ok=True)
    
    files = sorted(Path("extracted/apf_unpacked").glob("file_*.bin"))
    total_images = 0
    
    print(f"Scanning {len(files)} files for TIM textures...")
    for f in files:
        c = extract_all_tims_from_file(str(f), out_dir)
        if c > 0:
            print(f"  [{f.name}] -> Extracted {c} image(s)")
            total_images += c
            
    print(f"\n=======================================================")
    print(f"Successfully extracted {total_images} PNG textures to '{out_dir}/'!")
    print(f"=======================================================")

if __name__ == "__main__":
    batch_extract()
