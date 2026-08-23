#!/usr/bin/env python3
"""
Inspect the 8 menu options in sector 410 of OP.APF.
"""

import struct

with open("extracted/OP.APF", "rb") as f:
    f.seek(410 * 2048)
    sec410 = f.read(5 * 2048)

# In sector 410, base RAM address is around 0x8007CD00 or similar
# Let's find string offsets relative to sector 410 start
pointers = [
    0x8007CE88, 0x8007CEAC, 0x8007CEB8, 0x8007CF2C,
    0x8007CF3C, 0x8007CF5C, 0x8007CF7C, 0x8007CF88
]

# Calculate offset difference: 0x8007CE88 vs 0x000CD284
# Let's inspect all strings around sector 410 + 0x000 to +0x800
print("=== Sector 410 Menu Strings ===")
for p in range(0, 0x800, 1):
    # Try reading null-terminated string
    if sec410[p] in (0x81, 0x82, 0x83, 0x84, 0x88, 0x89, 0x8A, 0x8B, 0x8C, 0x8D, 0x8E, 0x8F, 0x90, 0x91, 0x92, 0x93, 0x94, 0x95, 0x96, 0x97, 0x98):
        # Shift-JIS string
        end = sec410.find(b'\x00', p)
        if end != -1 and 2 <= (end - p) <= 64:
            try:
                sjis = sec410[p:end].decode('shift_jis', errors='replace')
                print(f"  Offset 0x{p:04X} (abs 0x{410*2048+p:08X}): '{sjis}' (len={end-p})")
            except:
                pass

