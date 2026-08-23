#!/usr/bin/env python3
"""
Delta Patch Generator (xdelta / binary diff)
Generates a binary patch comparing clean game BIN with translated BIN.
"""

import os
import sys
import struct

def make_simple_diff_patch(orig_bin, mod_bin, patch_out="build/grand_battle_2_en.patch"):
    print(f"Creating binary diff patch between '{orig_bin}' and '{mod_bin}'...")
    
    diff_records = []
    chunk_size = 65536
    
    with open(orig_bin, "rb") as f_orig, open(mod_bin, "rb") as f_mod:
        offset = 0
        while True:
            b_orig = f_orig.read(chunk_size)
            b_mod = f_mod.read(chunk_size)
            
            if not b_orig or not b_mod:
                break
                
            if b_orig != b_mod:
                for i in range(min(len(b_orig), len(b_mod))):
                    if b_orig[i] != b_mod[i]:
                        diff_records.append((offset + i, b_mod[i]))
                        
            offset += len(b_orig)
            
    print(f"Found {len(diff_records):,} modified byte(s).")
    
    # Write custom patch format: Magic (4) + Count (4) + [Offset (4) + Byte (1)] * Count
    os.makedirs(os.path.dirname(patch_out), exist_ok=True)
    with open(patch_out, "wb") as pf:
        pf.write(b'OP2P')  # Magic: One Piece 2 Patch
        pf.write(struct.pack('<I', len(diff_records)))
        for off, val in diff_records:
            pf.write(struct.pack('<IB', off, val))
            
    print(f"Saved lightweight binary patch to '{patch_out}' ({os.path.getsize(patch_out):,} bytes)!")

def apply_simple_diff_patch(orig_bin, patch_file, out_bin):
    print(f"Applying patch '{patch_file}' to '{orig_bin}' -> '{out_bin}'...")
    import shutil
    shutil.copyfile(orig_bin, out_bin)
    
    with open(patch_file, "rb") as pf:
        magic = pf.read(4)
        if magic != b'OP2P':
            raise ValueError("Invalid patch format!")
        count = struct.unpack('<I', pf.read(4))[0]
        
        with open(out_bin, "r+b") as out_f:
            for _ in range(count):
                off, val = struct.unpack('<IB', pf.read(5))
                out_f.seek(off)
                out_f.write(bytes([val]))
                
    print(f"Successfully applied {count:,} byte modifications to '{out_bin}'!")

if __name__ == "__main__":
    if len(sys.argv) > 3 and sys.argv[1] == "apply":
        apply_simple_diff_patch(sys.argv[2], sys.argv[3], sys.argv[4])
    else:
        make_simple_diff_patch("grand_battle_2.bin", "build/grand_battle_2_en.bin")
