#!/usr/bin/env python3
"""
Unpack all 1322 subfiles from OP.DAT.
"""

import os
import sys
import struct
from pathlib import Path

def unpack_op_dat():
    dat_path = "extracted/OP.DAT"
    out_dir = "extracted/op_unpacked"
    os.makedirs(out_dir, exist_ok=True)
    
    with open(dat_path, "rb") as f:
        head = f.read(2048)
        num_files = struct.unpack_from('<I', head, 4)[0]
        print(f"Unpacking {dat_path} ({num_files} subfiles)...")
        
        # In OP.DAT, table starts at 0x800 and continues
        f.seek(0x800)
        table_raw = f.read(num_files * 16)
        
        manifest = []
        for i in range(num_files):
            rec = table_raw[i*16 : (i+1)*16]
            if len(rec) < 16:
                break
            val0, val1, val2, val3 = struct.unpack('<IIII', rec)
            
            sector_cnt = val0
            sector_lba = val1
            
            f.seek(sector_lba * 2048)
            data = f.read(sector_cnt * 2048)
            
            out_name = f"op_subfile_{i:04d}_LBA_{sector_lba:06d}.bin"
            out_file = os.path.join(out_dir, out_name)
            with open(out_file, "wb") as out_f:
                out_f.write(data)
                
            manifest.append((i, out_name, sector_lba, sector_cnt, len(data), val2))
            
    print(f"Extracted {len(manifest)} files to '{out_dir}/'!")
    
    with open(os.path.join(out_dir, "_manifest.txt"), "w") as mf:
        mf.write("Index\tFilename\tLBA\tSectors\tBytes\tType_Flag\n")
        for m in manifest:
            mf.write(f"{m[0]:04d}\t{m[1]}\t{m[2]}\t{m[3]}\t{m[4]}\t{m[5]}\n")

if __name__ == "__main__":
    unpack_op_dat()
