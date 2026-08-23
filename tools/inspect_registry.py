#!/usr/bin/env python3
"""
Inspect the global file registry table in OP.APF at offset 0x4000 - 0x6000.
"""

import struct

with open("extracted/OP.APF", "rb") as f:
    f.seek(0x4000)
    data = f.read(0x4000)
    
print("=== OP.APF GLOBAL FILE REGISTRY TABLE ===")
pos = 0
while pos < len(data) - 16:
    if 32 <= data[pos] <= 126:
        st = pos
        while pos < len(data) and (32 <= data[pos] <= 126 or data[pos] in (0x2E, 0x2F, 0x5F, 0x25, 0x64, 0x73)):
            pos += 1
        name = data[st:pos].decode('ascii', errors='replace')
        if len(name) >= 3 and ("." in name or "/" in name or "%" in name):
            # Inspect 16 bytes before and after
            abs_pos = 0x4000 + st
            after_bytes = data[pos:pos+16]
            print(f"0x{abs_pos:06X}: {name:<32} | After: {after_bytes[:8].hex(' ')}")
    pos += 1
