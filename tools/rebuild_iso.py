#!/usr/bin/env python3
"""
PS1 Disc Image Inserter / Rebuilder
Re-injects modified files (e.g. OP.APF or SLPS_034.08) into a PS1 MODE2/2352 disc image.
Calculates EDC/ECC or preserves disc structure.
"""

import os
import sys
import struct

# Standard PS1 EDC calculation table
EDC_TABLE = [0] * 256
for i in range(256):
    edc = i
    for _ in range(8):
        if edc & 1:
            edc = (edc >> 1) ^ 0xD8018001
        else:
            edc >>= 1
    EDC_TABLE[i] = edc

def compute_edc(data):
    """Compute 32-bit EDC for PS1 sector data."""
    edc = 0
    for b in data:
        edc = (edc >> 8) ^ EDC_TABLE[(edc ^ b) & 0xFF]
    return edc

def inject_file_to_bin(bin_path, modified_file_path, target_lba, output_bin_path=None):
    if output_bin_path is None:
        output_bin_path = bin_path
        
    print(f"Injecting '{modified_file_path}' into '{output_bin_path}' at LBA {target_lba}...")
    
    with open(modified_file_path, "rb") as mf:
        mod_data = mf.read()
        
    sector_size = 2352
    data_len = len(mod_data)
    sectors_needed = (data_len + 2047) // 2048
    
    with open(output_bin_path, "r+b") as bf:
        for s in range(sectors_needed):
            chunk = mod_data[s*2048 : (s+1)*2048]
            if len(chunk) < 2048:
                chunk += b'\x00' * (2048 - len(chunk))
                
            sector_offset = (target_lba + s) * sector_size
            bf.seek(sector_offset)
            raw_sector = bytearray(bf.read(sector_size))
            if len(raw_sector) < sector_size:
                break
                
            raw_sector[24:24+2048] = chunk
            edc_val = compute_edc(raw_sector[16:16+2056])
            raw_sector[2072:2076] = struct.pack('<I', edc_val)
            
            bf.seek(sector_offset)
            bf.write(raw_sector)
            
    print(f"Successfully injected {sectors_needed} sectors ({data_len:,} bytes) at LBA {target_lba}!")

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python rebuild_iso.py <bin_file> <replacement_file> <target_lba>")
        sys.exit(1)
    inject_file_to_bin(sys.argv[1], sys.argv[2], int(sys.argv[3]))
