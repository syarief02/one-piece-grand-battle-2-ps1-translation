#!/usr/bin/env python3
"""
Directly scan OP.DAT sectors for TIM textures using the internal table.
"""

import os
import struct
from tim_tool import decode_tim
from ganbarion_lz import decompress_ganbarion_lz

def scan_op_dat_tims():
    out_dir = "extracted/op_textures"
    os.makedirs(out_dir, exist_ok=True)
    
    with open("extracted/OP.DAT", "rb") as f:
        head = f.read(2048)
        num_files = struct.unpack_from('<I', head, 4)[0]
        print(f"Scanning {num_files} subfiles in OP.DAT...")
        
        f.seek(0x800)
        table_raw = f.read(num_files * 16)
        
        found_total = 0
        for i in range(num_files):
            rec = table_raw[i*16 : (i+1)*16]
            if len(rec) < 16:
                break
            val0, val1, val2, val3 = struct.unpack('<IIII', rec)
            
            # Read first 10 sectors (or sector_cnt) of each subfile
            sector_lba = val1
            sector_cnt = min(val0, 64)
            
            if sector_lba * 2048 >= os.path.getsize("extracted/OP.DAT"):
                continue
                
            f.seek(sector_lba * 2048)
            raw = f.read(sector_cnt * 2048)
            
            # Try raw & decompressed
            for test_data, is_decomp in [(raw, False), (decompress_ganbarion_lz(raw), True)]:
                pos = 0
                while pos < len(test_data) - 32:
                    if test_data[pos:pos+4] == b'\x10\x00\x00\x00':
                        img, meta = decode_tim(test_data, pos)
                        if img:
                            out_name = f"op_sub_{i:04d}_tim_{found_total:03d}_{img.size[0]}x{img.size[1]}.png"
                            img.save(os.path.join(out_dir, out_name))
                            print(f"  [{i:04d}] Found TIM at LBA {sector_lba}: {img.size[0]}x{img.size[1]} (decomp={is_decomp})")
                            found_total += 1
                            pos += meta["total_size"]
                            continue
                    pos += 4
                    
    print(f"\nTotal TIM textures discovered in OP.DAT: {found_total}")

if __name__ == "__main__":
    scan_op_dat_tims()
