#!/usr/bin/env python3
"""
Full APF_v2.0 Extractor for One Piece Grand Battle 2.
Extracts all 404 subfiles/assets from OP.APF using sector LBA index table.
"""

import os
import sys
import struct


def extract_apf(apf_path="extracted/OP.APF", out_dir="extracted/apf_unpacked"):
    os.makedirs(out_dir, exist_ok=True)
    
    with open(apf_path, "rb") as f:
        header = f.read(2048)
        magic = header[:8].decode('ascii', errors='replace')
        num_entries = struct.unpack_from('<I', header, 8)[0]
        total_sectors = struct.unpack_from('<I', header, 16)[0]
        
        print(f"APF Format: {magic}")
        print(f"Total Subfiles: {num_entries}")
        print(f"Total Sectors: {total_sectors} ({total_sectors * 2048:,} bytes)")
        
        # Read the sector table at offset 0x800 (sector 1)
        f.seek(0x800)
        table_bytes = f.read(num_entries * 4)
        lba_list = [struct.unpack_from('<I', table_bytes, i * 4)[0] for i in range(num_entries)]
        
        # Append end sector
        lba_list.append(total_sectors)
        
        extracted_files = []
        
        for i in range(num_entries):
            start_lba = lba_list[i]
            next_lba = lba_list[i + 1]
            sector_count = next_lba - start_lba
            byte_len = sector_count * 2048
            
            f.seek(start_lba * 2048)
            data = f.read(byte_len)
            
            # Detect file type by magic bytes
            ext = "bin"
            if len(data) >= 4:
                magic_4 = data[:4]
                if magic_4 == b'pGXP' or magic_4 == b'PXG\x00' or magic_4[:3] == b'PAC':
                    ext = "pac"
                elif magic_4 == b'TIM\x00' or (data[0] == 0x10 and data[1] == 0x00 and data[2] == 0x00 and data[3] == 0x00):
                    ext = "tim"
                elif magic_4 == b'VABp' or magic_4 == b'pBAV':
                    ext = "vab"
                elif magic_4 == b'SEQp':
                    ext = "seq"
                elif magic_4 == b'PS-X':
                    ext = "exe"
            
            filename = f"file_{i:03d}_LBA_{start_lba:05d}.{ext}"
            filepath = os.path.join(out_dir, filename)
            
            with open(filepath, "wb") as out_f:
                out_f.write(data)
                
            extracted_files.append((filename, start_lba, sector_count, byte_len, data[:16].hex()))
        
        print(f"\nSuccessfully unpacked {len(extracted_files)} files to '{out_dir}/'!")
        
        # Write inventory manifest
        manifest_path = os.path.join(out_dir, "_apf_manifest.txt")
        with open(manifest_path, "w", encoding="utf-8") as mf:
            mf.write(f"Index\tFilename\tStart_LBA\tSectors\tBytes\tFirst_16_Bytes\n")
            for i, (fn, lba, cnt, blen, hex_head) in enumerate(extracted_files):
                mf.write(f"{i:03d}\t{fn}\t{lba}\t{cnt}\t{blen}\t{hex_head}\n")
                
        print(f"Manifest written to: {manifest_path}")

if __name__ == "__main__":
    extract_apf()
