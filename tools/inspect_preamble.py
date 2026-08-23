#!/usr/bin/env python3
"""
Inspect the preamble (first 3.48 MB) of OP.APF to discover overlays, PROG sections, and tables.
"""

import os
import struct

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

def inspect_preamble():
    with open("extracted/OP.APF", "rb") as f:
        preamble = f.read(1704 * 2048)
        
    print(f"Preamble size: {len(preamble):,} bytes")
    
    for pac in target_pac_names:
        pos = 0
        while True:
            pos = preamble.find(pac, pos)
            if pos == -1:
                break
            sector = pos // 2048
            sec_off = pos % 2048
            print(f"Found '{pac.decode()}' at byte 0x{pos:08X} (Sector {sector}, offset 0x{sec_off:03X})")
            
            # Print 32 bytes around
            st = max(0, pos - 16)
            en = min(len(preamble), pos + len(pac) + 16)
            print(f"   Context: {preamble[st:en].hex(' ')}")
            pos += len(pac)

if __name__ == "__main__":
    inspect_preamble()
