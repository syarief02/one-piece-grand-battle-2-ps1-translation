#!/usr/bin/env python3
"""
Correlate PAC filenames with unpacked subfiles in extracted/apf_unpacked.
"""

import os
import struct
from pathlib import Path

def identify_pacs():
    files = sorted(Path("extracted/apf_unpacked").glob("file_*.bin"))
    print(f"Analyzing {len(files)} subfiles...\n")
    
    for i, f in enumerate(files):
        with open(f, "rb") as fp:
            head = fp.read(64)
            
        # Check if first 4 bytes are an entry count or sub-table
        val0 = struct.unpack_from('<I', head, 0)[0]
        val1 = struct.unpack_from('<I', head, 4)[0]
        
        # Check for strings in first 512 bytes
        with open(f, "rb") as fp:
            data = fp.read(2048)
            
        ascii_chars = [chr(b) for b in data if 32 <= b <= 126]
        text_preview = "".join(ascii_chars[:24])
        
        # Look for TIM headers
        tim_count = 0
        p = 0
        while p < len(data) - 4:
            if data[p:p+4] == b'\x10\x00\x00\x00':
                tim_count += 1
            p += 4
            
        if tim_count > 0 or any(kw in data for kw in [b'menu', b'MENU', b'title', b'TITLE', b'select', b'SELECT', b'option', b'OPTION']):
            print(f"Subfile {i:03d} [{f.name}] ({os.path.getsize(f):,} bytes): TIMs={tim_count} | Text: '{text_preview}'")

if __name__ == "__main__":
    identify_pacs()
