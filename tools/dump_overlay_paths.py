#!/usr/bin/env python3
"""
Dump all PAC and asset paths from the overlay tables in OP.APF.
"""

import os
import struct

def dump_overlay_paths():
    with open("extracted/OP.APF", "rb") as f:
        preamble = f.read(1704 * 2048)
        
    pos = 0
    all_paths = []
    while pos < len(preamble) - 4:
        # Check for path strings like "title/", "event/", "battle/", etc.
        for prefix in [b"title/", b"event/", b"battle/", b"select/", b"sound/", b"menu/"]:
            if preamble[pos:pos+len(prefix)] == prefix:
                # Read string until null terminator
                end = preamble.find(b"\x00", pos)
                if end != -1 and (end - pos) < 64:
                    path_str = preamble[pos:end].decode('ascii', errors='replace')
                    all_paths.append((pos, pos // 2048, path_str))
                    pos = end
                    break
        pos += 1
        
    print(f"Found {len(all_paths)} internal asset paths in OP.APF overlays:\n")
    for bpos, sector, path in all_paths:
        clean_path = ''.join(c if 32 <= ord(c) <= 126 else '?' for c in path)
        print(f"  Sector {sector:04d} (0x{bpos:08X}): {clean_path}")

if __name__ == "__main__":
    dump_overlay_paths()
