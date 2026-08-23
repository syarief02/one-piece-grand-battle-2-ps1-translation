#!/usr/bin/env python3
"""
Scan OP2.DAT subfiles for TIM textures.
"""

import os
from pathlib import Path
from tim_tool import decode_tim
from ganbarion_lz import decompress_ganbarion_lz

def scan_op2():
    out_dir = "extracted/op2_textures"
    os.makedirs(out_dir, exist_ok=True)
    
    files = sorted(Path("extracted/op2_unpacked").glob("subfile_*.bin"))
    print(f"Scanning {len(files)} subfiles in OP2.DAT...")
    
    count = 0
    for f in files:
        with open(f, "rb") as fp:
            data = fp.read()
            
        decomp = decompress_ganbarion_lz(data)
        
        pos = 0
        while pos < len(decomp) - 32:
            if decomp[pos:pos+4] == b'\x10\x00\x00\x00':
                img, meta = decode_tim(decomp, pos)
                if img:
                    out_png = os.path.join(out_dir, f"{f.stem}_tim_{count:03d}_{img.size[0]}x{img.size[1]}.png")
                    img.save(out_png)
                    print(f"  Found TIM in {f.name} at 0x{pos:08X}: {img.size[0]}x{img.size[1]}")
                    count += 1
                    pos += meta["total_size"]
                    continue
            pos += 4
            
    print(f"Total extracted from OP2.DAT: {count}")

if __name__ == "__main__":
    scan_op2()
