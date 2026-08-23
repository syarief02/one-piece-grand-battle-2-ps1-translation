#!/usr/bin/env python3
"""
Inspect file index table for OP2.DAT and OP.DAT.
"""

import struct

def check_table(filepath):
    with open(filepath, "rb") as f:
        head = f.read(65536)
        
    num_files = struct.unpack_from('<I', head, 4)[0]
    print(f"\n{filepath} (Claimed file count: {num_files})")
    
    # Check sector 1 (offset 0x800 = 2048) or offset 0x20, 0x40, etc.
    for table_offset in [0x10, 0x20, 0x40, 0x80, 0x800, 0x1000]:
        first_vals = [struct.unpack_from('<I', head, table_offset + i*4)[0] for i in range(min(num_files, 8))]
        non_zeros = [v for v in first_vals if v > 0]
        if non_zeros:
            print(f"  Candidate table at 0x{table_offset:04X}:")
            for i, v in enumerate(first_vals):
                print(f"     [{i}]: {v} (0x{v:08X}) -> Sector {v} ({v*2048:,} bytes)")

if __name__ == "__main__":
    check_table("extracted/OP2.DAT")
    check_table("extracted/OP.DAT")
