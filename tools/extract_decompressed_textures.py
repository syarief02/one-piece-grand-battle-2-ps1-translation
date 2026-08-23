#!/usr/bin/env python3
"""
Batch decompress all APF files and extract all previously compressed TIM textures.
"""

import os
import sys
from pathlib import Path
from ganbarion_lz import decompress_ganbarion_lz
from tim_tool import decode_tim

def extract_all_decompressed_textures():
    out_dir = "extracted/textures_decompressed"
    os.makedirs(out_dir, exist_ok=True)
    
    files = sorted(Path("extracted/apf_unpacked").glob("file_*.bin"))
    total_extracted = 0
    
    print(f"Decompressing and extracting textures from {len(files)} files...")
    
    for f in files:
        with open(f, "rb") as fp:
            data = fp.read()
            
        decomp = decompress_ganbarion_lz(data)
        
        # Scan for TIM textures in decompressed stream
        pos = 0
        file_tim_count = 0
        while pos < len(decomp) - 32:
            if decomp[pos:pos+4] == b'\x10\x00\x00\x00':
                img, meta = decode_tim(decomp, pos)
                if img and img.size[0] > 0 and img.size[1] > 0:
                    out_name = f"{f.stem}_tim_{file_tim_count:03d}_off_{pos:08X}_{img.size[0]}x{img.size[1]}.png"
                    out_path = os.path.join(out_dir, out_name)
                    try:
                        img.save(out_path)
                        file_tim_count += 1
                        total_extracted += 1
                        pos += meta["total_size"]
                        continue
                    except:
                        pass
            pos += 4
            
        if file_tim_count > 0:
            print(f"  [{f.name}] -> Extracted {file_tim_count} TIM texture(s)!")
            
    print(f"\n=======================================================")
    print(f"Extracted {total_extracted} total decompressed textures to '{out_dir}/'!")
    print(f"=======================================================")

if __name__ == "__main__":
    extract_all_decompressed_textures()
