#!/usr/bin/env python3
"""
Inspect decompressor routine in OP.APF around ./UNPAC.C (0x00755C).
"""

import struct

with open("extracted/OP.APF", "rb") as f:
    f.seek(0x007400)
    data = f.read(0x1000)

print("=== Disassembling around UNPAC.C ===")
for i in range(0, len(data), 4):
    instr = struct.unpack_from('<I', data, i)[0]
    op = (instr >> 26) & 0x3F
    rs = (instr >> 21) & 0x1F
    rt = (instr >> 16) & 0x1F
    rd = (instr >> 11) & 0x1F
    funct = instr & 0x3F
    imm = instr & 0xFFFF
    
    abs_addr = 0x007400 + i
    # Look for branch or load/store instructions
    # Check if it references magic bytes or decompression loop
    if i % 64 == 0:
        print(f"\n0x{abs_addr:06X}:")
    print(f"  {abs_addr:06X}: {instr:08X} (op={op:02d}, funct={funct:02d})")
    if i > 256:
        break
