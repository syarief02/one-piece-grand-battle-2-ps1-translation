#!/usr/bin/env python3
"""
Find callers of UNPAC in SLPS_034.08.
"""

import struct

with open("extracted/SLPS_034.08", "rb") as f:
    exe = f.read()

# Header is 0x800 bytes, load address is 0x80010000
# Code starts at offset 0x800

print(f"SLPS size: {len(exe)} bytes")

# Search for jal instructions (op=3) or lui/ori loading address of UNPAC
# String "UNPAC_Open()" is at RAM address 0x80011568
str_addr = 0x80011568
hi = (str_addr >> 16) + (1 if (str_addr & 0x8000) else 0)
lo = str_addr & 0xFFFF

print(f"Searching for references to UNPAC_Open string (0x{str_addr:08X}: hi=0x{hi:04X}, lo=0x{lo:04X})...")

for i in range(0x800, len(exe)-4, 4):
    instr = struct.unpack_from('<I', exe, i)[0]
    op = (instr >> 26) & 0x3F
    imm = instr & 0xFFFF
    
    if imm == lo:
        print(f"  Reference at offset 0x{i:06X} [RAM: 0x{0x80010000 + i - 0x800:08X}]: {instr:08X}")
