#!/usr/bin/env python3
"""
Search for UNPAC in SLPS_034.08.
"""

with open("extracted/SLPS_034.08", "rb") as f:
    exe = f.read()

for term in [b"UNPAC", b"unpac", b"op_unpac", b"APF", b"DAT"]:
    pos = 0
    while True:
        pos = exe.find(term, pos)
        if pos == -1:
            break
        print(f"Found '{term.decode()}' in SLPS at 0x{pos:06X}")
        pos += len(term)
