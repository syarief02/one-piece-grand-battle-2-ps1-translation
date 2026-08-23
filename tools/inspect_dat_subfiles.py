#!/usr/bin/env python3
"""
Inspect entries from OP2.DAT and OP.DAT.
"""

import struct

def inspect_dat_subfiles(filepath):
    print(f"\n=======================================================")
    print(f"  Unpacking & Analyzing Subfiles in {filepath}")
    print(f"=======================================================")
    
    with open(filepath, "rb") as f:
        head = f.read(2048)
        num_files = struct.unpack_from('<I', head, 4)[0]
        
        # Read 16-byte records from offset 0x800
        f.seek(0x800)
        records_raw = f.read(num_files * 16)
        
        for i in range(min(num_files, 15)):
            rec = records_raw[i*16 : (i+1)*16]
            if len(rec) < 16:
                break
            val0, val1, val2, val3 = struct.unpack('<IIII', rec)
            
            # Let's inspect data at LBA val1 or val0
            # Let's see which one is sector offset
            for candidate_lba in [val0, val1]:
                if candidate_lba * 2048 < os.path.getsize(filepath):
                    f.seek(candidate_lba * 2048)
                    sample = f.read(32)
                    print(f"Entry {i:02d}: Record=({val0}, {val1}, {val2}, {val3})")
                    print(f"   At LBA {candidate_lba} (0x{candidate_lba*2048:08X}): {sample[:16].hex(' ')} | {sample[:16]}")
                    break

if __name__ == "__main__":
    import os
    inspect_dat_subfiles("extracted/OP2.DAT")
