#!/usr/bin/env python3
"""
Inspect how topmenu.pac and option.pac are loaded in sector 410 of OP.APF.
"""

import struct

with open("extracted/OP.APF", "rb") as f:
    f.seek(410 * 2048)
    sec410 = f.read(5 * 2048)

pos = sec410.find(b"title/topmenu.pac")
print(f"'title/topmenu.pac' offset in sector 410: 0x{pos:04X} (abs: 0x{410*2048+pos:08X})")

# Look at 64 bytes before and after
st = max(0, pos - 32)
en = min(len(sec410), pos + len(b"title/topmenu.pac") + 64)
print("Bytes:")
print(sec410[st:en].hex(' '))

# Look for functions referencing this address
addr_in_ram = 0x8007CE84 # Estimate RAM address
print(f"\nSearching for pointers or references to topmenu...")
