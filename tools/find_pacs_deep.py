#!/usr/bin/env python3
"""
Find where PAC archives are stored in OP.APF and OP.DAT.
Searches for pac file content signatures.
"""

import os
import struct

def search_pac_containers():
    print("Searching for PAC file contents and headers across all files...")
    
    # In Ganbarion games, a PAC archive usually starts with:
    # - Number of files (UInt32) or 'pGXP' / 'PAC' / 'PXG\x00' or an offset table
    
    # Let's search in OP.APF, OP.DAT, and OP2.DAT
    # Let's look for known strings in topmenu.pac:
    # "topmenu", "TOP_MENU", "grand", "event", "option", "training"
    
    with open("extracted/OP.APF", "rb") as f:
        apf = f.read()
        
    print(f"OP.APF loaded ({len(apf):,} bytes)")
    
    # Search for "topmenu.pac"
    pos = apf.find(b"topmenu.pac")
    print(f"'topmenu.pac' string at 0x{pos:08X} in OP.APF")
    
    # Let's inspect the memory/code around pos
    # In sector 410 (offset 0x000CD284)
    # Right after 'topmenu.pac', there is:
    # 00 00 00 00 00 00 00 88 ce 07 80 ac ce 07 80 ...
    
    # Let's inspect the entire table of files in sector 410
    sec410 = apf[410*2048 : 415*2048]
    print(f"\n=== Sector 410-414 strings ===")
    p = 0
    while p < len(sec410):
        # find ascii string >= 4 chars
        if 32 <= sec410[p] <= 126:
            st = p
            while p < len(sec410) and (32 <= sec410[p] <= 126 or sec410[p] in (0x2E, 0x2F, 0x5F)):
                p += 1
            s = sec410[st:p].decode('ascii', errors='replace')
            if len(s) >= 4 and ("pac" in s or "nex" in s or "STR" in s or "c" in s):
                abs_off = 410*2048 + st
                print(f"  0x{abs_off:08X}: {s}")
        p += 1

if __name__ == "__main__":
    search_pac_containers()
