#!/usr/bin/env python3
"""
Extractor for OP.DAT and OP2.DAT subfiles.
"""

import os
import sys
import struct
from pathlib import Path

def unpack_dat(dat_path, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    with open(dat_path, "rb") as f:
        head = f.read(2048)
        num_files = struct.unpack_from('<I', head, 4)[0]
        print(f"Unpacking {dat_path} ({num_files} subfiles)...")
        
        # Read 16-byte table from offset 0x800
        f.seek(0x800)
        table_raw = f.read(num_files * 16)
        
        for i in range(num_files):
            rec = table_raw[i*16 : (i+1)*16]
            if len(rec) < 16:
                break
            val0, val1, val2, val3 = struct.unpack('<IIII', rec)
            
            # The sector offset is val1, and sector count is val0
            # Let's verify
            sector_cnt = val0
            sector_lba = val1
            
            # Read data
            f.seek(sector_lba * 2048)
            data = f.read(sector_cnt * 2048)
            
            out_file = os.path.join(out_dir, f"subfile_{i:04d}_LBA_{sector_lba:06d}.bin")
            with open(out_file, "wb") as out_f:
                out_f.write(data)
                
    print(f"Extracted {num_files} files to '{out_dir}/'!")

if __name__ == "__main__":
    unpack_dat("extracted/OP2.DAT", "extracted/op2_unpacked")
