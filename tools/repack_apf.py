#!/usr/bin/env python3
"""
APF_v2.0 Repacker for One Piece Grand Battle 2.
Takes files from 'extracted/apf_unpacked/' and repacks them into a new OP.APF.
"""

import os
import sys
import struct
from pathlib import Path

def repack_apf(in_dir="extracted/apf_unpacked", out_path="extracted/OP.APF.rebuilt", original_apf="extracted/OP.APF"):
    print(f"Repacking APF archive from '{in_dir}' -> '{out_path}'...")
    
    with open(original_apf, "rb") as f:
        orig_header = bytearray(f.read(2048))
        num_entries = struct.unpack_from('<I', orig_header, 8)[0]
        
    print(f"Preserving original header with {num_entries} entries.")
    
    manifest_path = os.path.join(in_dir, "_apf_manifest.txt")
    file_list = []
    
    if os.path.exists(manifest_path):
        with open(manifest_path, "r", encoding="utf-8") as mf:
            lines = mf.readlines()[1:]
            for line in lines:
                parts = line.strip().split("\t")
                if len(parts) >= 2:
                    file_list.append(parts[1])
    else:
        file_list = [f.name for f in sorted(Path(in_dir).glob("file_*.*")) if not f.name.startswith("_")]

    print(f"Found {len(file_list)} subfiles to repack.")
    
    with open(original_apf, "rb") as f:
        original_preamble = f.read(1704 * 2048)
        
    with open(out_path, "wb") as out_f:
        out_f.write(original_preamble)
        
        current_lba = 1704
        lba_offsets = []
        
        for i, fname in enumerate(file_list):
            fpath = os.path.join(in_dir, fname)
            with open(fpath, "rb") as sub_f:
                content = sub_f.read()
                
            pad_len = (2048 - (len(content) % 2048)) % 2048
            if pad_len > 0:
                content += b'\x00' * pad_len
                
            sector_count = len(content) // 2048
            lba_offsets.append(current_lba)
            
            out_f.write(content)
            current_lba += sector_count
            
        total_sectors = current_lba
        
        out_f.seek(0x800)
        for lba in lba_offsets:
            out_f.write(struct.pack('<I', lba))
            
        out_f.seek(0x10)
        out_f.write(struct.pack('<I', total_sectors))
        
    print(f"Repack complete! New APF size: {os.path.getsize(out_path):,} bytes, Total Sectors: {total_sectors}")

if __name__ == "__main__":
    repack_apf()
