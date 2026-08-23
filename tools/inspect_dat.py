#!/usr/bin/env python3
"""
Inspect OP.DAT and OP2.DAT container structure.
Header starts with 'DAT\x00'
"""

import os
import sys
import struct

def inspect_dat(filepath):
    print(f"\n=======================================================")
    print(f"  Inspecting {filepath} ({os.path.getsize(filepath):,} bytes)")
    print(f"=======================================================")
    
    with open(filepath, "rb") as f:
        head = f.read(2048)
        
    magic = head[:4]
    print(f"Magic: {magic}")
    
    # Read the first 32 32-bit integers
    ints = [struct.unpack_from('<I', head, i*4)[0] for i in range(16)]
    for i, val in enumerate(ints):
        print(f"  Int[{i:02d}] (offset 0x{i*4:02X}): {val} (0x{val:08X})")

if __name__ == "__main__":
    inspect_dat("extracted/OP2.DAT")
    inspect_dat("extracted/OP.DAT")
