#!/usr/bin/env python3
"""
Disassemble unpac routines in SLPS_034.08 around 0x001D50.
"""

import struct

with open("extracted/SLPS_034.08", "rb") as f:
    f.seek(0x001C00)
    data = f.read(0x400)

# MIPS instructions
for i in range(0, len(data), 4):
    instr = struct.unpack_from('<I', data, i)[0]
    addr = 0x80010000 + 0x001C00 + i - 0x800  # PS1 load address is 0x80010000 (after 0x800 header)
    
    # Try reading as string if printable
    bytes4 = data[i:i+4]
    if all(32 <= b <= 126 for b in bytes4):
        print(f"0x{0x001C00+i:06X} [RAM: 0x{addr:08X}]: '{bytes4.decode()}' (String)")
    else:
        print(f"0x{0x001C00+i:06X} [RAM: 0x{addr:08X}]: {instr:08X}")
