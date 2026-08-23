#!/usr/bin/env python3
"""
Inspect all graphical textures (TIM format) in the game files.
TIM is the standard Sony PlayStation image format.
Magic byte: 0x10 0x00 0x00 0x00 (Version 0, ID 0x10)
"""

import os
import sys
import struct
from pathlib import Path

def find_tim_files(data, filename_prefix=""):
    """
    Search for TIM image headers in binary data.
    TIM header:
    - 0x00: 0x10 0x00 0x00 0x00 (Magic)
    - 0x04: Flags (0x08 = 4-bit, 0x09 = 8-bit, 0x02 = 16-bit, 0x03 = 24-bit)
    """
    tims = []
    pos = 0
    while pos < len(data) - 32:
        if data[pos:pos+4] == b'\x10\x00\x00\x00':
            flags = struct.unpack_from('<I', data, pos+4)[0]
            bpp_flag = flags & 0x07
            has_clut = (flags & 0x08) != 0
            
            # Validate plausible flags
            if bpp_flag in (0, 1, 2, 3):
                # Try to parse TIM length
                try:
                    offset = pos + 8
                    clut_size = 0
                    if has_clut:
                        clut_len = struct.unpack_from('<I', data, offset)[0]
                        clut_size = clut_len
                        offset += clut_len
                    
                    img_len = struct.unpack_from('<I', data, offset)[0]
                    total_tim_len = (offset + img_len) - pos
                    
                    if 32 < total_tim_len < 1024 * 1024 * 4 and pos + total_tim_len <= len(data):
                        tims.append((pos, total_tim_len, bpp_flag, has_clut))
                        pos += total_tim_len
                        continue
                except:
                    pass
        pos += 4
    return tims

def main():
    print("=== Scanning extracted assets for TIM Image Textures ===")
    
    # 1. Check unpacked APF files
    apf_files = sorted(Path("extracted/apf_unpacked").glob("file_*.bin"))
    total_tims = 0
    
    for f in apf_files:
        with open(f, "rb") as fp:
            data = fp.read()
        tims = find_tim_files(data, f.name)
        if tims:
            total_tims += len(tims)
            print(f"[{f.name}] contains {len(tims)} TIM texture(s):")
            for tpos, tlen, bpp, clut in tims[:3]:
                bpp_name = ["4-bit", "8-bit", "16-bit", "24-bit"][bpp]
                print(f"   Offset 0x{tpos:06X}: {tlen:,} bytes, {bpp_name}, CLUT={clut}")
                
    print(f"\nTotal TIM textures found in APF: {total_tims}")

if __name__ == "__main__":
    main()
