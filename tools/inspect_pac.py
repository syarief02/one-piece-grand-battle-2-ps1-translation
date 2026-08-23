#!/usr/bin/env python3
"""
PAC / Archive Extractor for Ganbarion One Piece PS1 engine.
Inspects OP.APF and extracts individual .pac, .nex, and data files.
"""

import os
import sys
import struct
from pathlib import Path


def inspect_pac_archive(data, output_dir="extracted/pac_files"):
    """
    Search for PAC archives and extract them.
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # Check for known PAC magic or patterns
    print("Scanning OP.APF for PAC structures and embedded assets...")
    
    # Let's inspect the APF table
    # In APF_v2.0, let's look at the offsets table starting around 0x800 or sector 1
    # Let's dump the sector 0 and 1 of OP.APF
    
    with open("extracted/OP.APF", "rb") as f:
        apf_data = f.read(65536)
    
    print("=== APF FIRST 512 BYTES ===")
    for i in range(0, 512, 16):
        hex_str = " ".join(f"{b:02X}" for b in apf_data[i:i+16])
        asc_str = "".join(chr(b) if 32 <= b <= 126 else "." for b in apf_data[i:i+16])
        print(f"{i:04X}: {hex_str:<48} | {asc_str}")

if __name__ == "__main__":
    inspect_pac_archive(b"")
