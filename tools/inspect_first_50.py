#!/usr/bin/env python3
"""
Inspect subfiles 000 to 050 in extracted/apf_unpacked.
"""

import os
from pathlib import Path

for i in range(50):
    fpath = list(Path("extracted/apf_unpacked").glob(f"file_{i:03d}_*.bin"))
    if fpath:
        f = fpath[0]
        with open(f, "rb") as fp:
            data = fp.read()
            
        magic = data[:8]
        size = len(data)
        
        # Look for any text in file
        chars = [chr(b) for b in data if 32 <= b <= 126]
        preview = "".join(chars[:40])
        
        # Search for Japanese characters
        has_jp = any(b > 0x80 for b in data[:1000])
        
        print(f"Subfile {i:03d} ({size:,} B) Magic={magic.hex(' ')} | '{preview}'")
