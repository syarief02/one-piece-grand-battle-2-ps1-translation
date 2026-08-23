#!/usr/bin/env python3
"""
Examine OP.DAT table structure around record 500-540.
"""

import struct

with open("extracted/OP.DAT", "rb") as f:
    head = f.read(2048)
    num_files = struct.unpack_from('<I', head, 4)[0]
    
    f.seek(0x800)
    table_raw = f.read(num_files * 16)
    
    print(f"Total claimed entries in header: {num_files}")
    for i in range(520, min(num_files, 535)):
        rec = table_raw[i*16 : (i+1)*16]
        val0, val1, val2, val3 = struct.unpack('<IIII', rec)
        print(f"Record {i:04d}: val0={val0} (0x{val0:08X}), val1={val1} (0x{val1:08X}), val2={val2} (0x{val2:08X}), val3={val3} (0x{val3:08X})")
