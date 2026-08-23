#!/usr/bin/env python3
"""
Find PAC filenames and their offsets inside APF assets.
"""

import os
from pathlib import Path

target_pac_names = [
    b"title/title_bg.pac",
    b"title/topmenu.pac",
    b"title/option.pac",
    b"title/tre_menu.pac",
    b"title/treasure.pac",
    b"title/opening.pac",
    b"title/title_op.pac",
    b"title/charmes.pac",
    b"title/opthelp.pac",
    b"event/ending/EdSys.pac",
    b"event/Ending/Staff.pac"
]

def search_pacs():
    files = sorted(Path("extracted/apf_unpacked").glob("file_*.bin"))
    print(f"Scanning {len(files)} files for PAC file references...\n")
    
    for f in files:
        with open(f, "rb") as fp:
            data = fp.read()
            
        for pac_name in target_pac_names:
            pos = data.find(pac_name)
            if pos != -1:
                print(f"Found '{pac_name.decode()}' in {f.name} at offset 0x{pos:06X}")
                # Print surrounding bytes
                start = max(0, pos - 16)
                end = min(len(data), pos + len(pac_name) + 32)
                ctx = data[start:end]
                print(f"   Context: {ctx.hex(' ')}")

if __name__ == "__main__":
    search_pacs()
