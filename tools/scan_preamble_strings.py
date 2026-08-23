#!/usr/bin/env python3
"""
Scan preamble overlay sectors 400 to 450 in OP.APF for menu and option strings.
"""

import os

with open("extracted/OP.APF", "rb") as f:
    preamble = f.read(1704 * 2048)

print("=== Scanning Preamble Overlay Sectors for Text Strings ===")
pos = 0
found_strings = []

while pos < len(preamble) - 4:
    start = pos
    raw = bytearray()
    
    while pos < len(preamble):
        b = preamble[pos]
        # Shift-JIS or ASCII
        if 0x20 <= b <= 0x7E:
            raw.append(b)
            pos += 1
            continue
        elif pos + 1 < len(preamble) and ((0x81 <= b <= 0x9F) or (0xE0 <= b <= 0xEF)):
            b2 = preamble[pos+1]
            if (0x40 <= b2 <= 0x7E) or (0x80 <= b2 <= 0xFC):
                raw.append(b)
                raw.append(b2)
                pos += 2
                continue
        break
        
    if len(raw) >= 4:
        try:
            text = raw.decode('shift_jis', errors='replace').strip()
            if any(ord(c) > 0x7F for c in text) or any(kw in text.lower() for kw in ['mode', 'option', 'battle', 'select', 'grand', 'story', 'time']):
                found_strings.append((start, start // 2048, text))
        except:
            pass
    pos += 1

print(f"Found {len(found_strings)} menu/mode strings in OP.APF preamble:\n")
for off, sec, s in found_strings[:40]:
    clean_s = ''.join(c if 32 <= ord(c) <= 126 or ord(c) > 0x3000 else '?' for c in s)
    print(f"  Sector {sec:04d} (0x{off:08X}): {clean_s}")
