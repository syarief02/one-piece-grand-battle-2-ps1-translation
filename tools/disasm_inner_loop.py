#!/usr/bin/env python3
"""
Disassemble the core decompression loop at 0x8003278C (offset 0x022F8C).
"""

import struct

with open("extracted/SLPS_034.08", "rb") as f:
    f.seek(0x022F8C)
    data = f.read(0x180)

print("=== Core Decompression Loop (0x8003278C) ===")
for i in range(0, len(data), 4):
    instr = struct.unpack_from('<I', data, i)[0]
    addr = 0x8003278C + i
    
    # Simple decode
    op = (instr >> 26) & 0x3F
    rs = (instr >> 21) & 0x1F
    rt = (instr >> 16) & 0x1F
    rd = (instr >> 11) & 0x1F
    funct = instr & 0x3F
    imm = instr & 0xFFFF
    
    print(f"0x{addr:08X}: {instr:08X} (op={op:02d}, rs={rs:02d}, rt={rt:02d}, rd={rd:02d}, imm=0x{imm:04X})")
