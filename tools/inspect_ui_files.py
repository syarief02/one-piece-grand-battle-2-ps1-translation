#!/usr/bin/env python3
"""
Inspect UI and Font files (file_380 to file_404) in extracted/apf_unpacked.
"""

import os
from pathlib import Path
from PIL import Image
from tim_tool import decode_tim

def inspect_ui():
    out_dir = "extracted/ui_inspection"
    os.makedirs(out_dir, exist_ok=True)
    
    for i in range(380, 404):
        fpath = list(Path("extracted/apf_unpacked").glob(f"file_{i:03d}_*.bin"))
        if not fpath:
            continue
        f = fpath[0]
        with open(f, "rb") as fp:
            data = fp.read()
            
        print(f"File {i:03d} [{f.name}]: {len(data):,} bytes")
        
        # Scan for all TIM textures
        pos = 0
        tim_idx = 0
        while pos < len(data) - 32:
            if data[pos:pos+4] == b'\x10\x00\x00\x00':
                img, meta = decode_tim(data, pos)
                if img:
                    out_png = os.path.join(out_dir, f"ui_{i:03d}_tim_{tim_idx:02d}_{img.size[0]}x{img.size[1]}.png")
                    img.save(out_png)
                    print(f"   -> Found TIM {tim_idx}: {img.size[0]}x{img.size[1]} | BPP={meta['bpp_mode']}")
                    tim_idx += 1
                    pos += meta["total_size"]
                    continue
            pos += 4

if __name__ == "__main__":
    inspect_ui()
