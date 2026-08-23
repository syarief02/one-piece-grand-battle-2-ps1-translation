#!/usr/bin/env python3
"""
PS1 ISO Filesystem Extractor
Extracts files from a MODE2/2352 PS1 disc image.
"""

import os
import sys
import struct
from pathlib import Path


def read_sector(f, sector_num, mode='mode2'):
    """Read a single sector from the disc image."""
    sector_size = 2352
    f.seek(sector_num * sector_size)
    raw = f.read(sector_size)
    
    if len(raw) < sector_size:
        return None
    
    if mode == 'mode2':
        # Mode 2 Form 1: 12 sync + 4 header + 8 subheader + 2048 data + 4 EDC + 276 ECC
        # Mode 2 Form 2: 12 sync + 4 header + 8 subheader + 2328 data + 4 EDC
        # Try Form 1 first (most common for data)
        data = raw[24:24+2048]  # Skip sync(12) + header(4) + subheader(8)
        return data
    elif mode == 'mode1':
        data = raw[16:16+2048]  # Skip sync(12) + header(4)
        return data
    
    return raw


def read_sectors(f, start_sector, count, mode='mode2'):
    """Read multiple consecutive sectors."""
    data = bytearray()
    for i in range(count):
        sector_data = read_sector(f, start_sector + i, mode)
        if sector_data:
            data.extend(sector_data)
    return bytes(data)


def parse_directory_record(data, offset):
    """Parse a single ISO 9660 directory record."""
    if offset >= len(data):
        return None, 0
    
    record_len = data[offset]
    if record_len == 0:
        return None, 0
    
    if offset + record_len > len(data):
        return None, 0
    
    record = data[offset:offset + record_len]
    
    ext_attr_len = record[1]
    extent_lba = struct.unpack_from('<I', record, 2)[0]
    data_length = struct.unpack_from('<I', record, 10)[0]
    flags = record[25]
    name_len = record[32]
    
    if name_len > 0 and 33 + name_len <= len(record):
        name = record[33:33 + name_len]
        try:
            name_str = name.decode('ascii', errors='replace')
        except:
            name_str = name.hex()
    else:
        name_str = ''
    
    is_directory = (flags & 0x02) != 0
    
    # Clean up name
    if name_str == '\x00':
        name_str = '.'
    elif name_str == '\x01':
        name_str = '..'
    else:
        # Remove version number (;1)
        if ';' in name_str:
            name_str = name_str.split(';')[0]
    
    return {
        'name': name_str,
        'extent_lba': extent_lba,
        'data_length': data_length,
        'is_directory': is_directory,
        'flags': flags
    }, record_len


def list_directory(f, lba, size, mode='mode2'):
    """List all entries in a directory."""
    sectors_needed = (size + 2047) // 2048
    data = read_sectors(f, lba, sectors_needed, mode)
    
    entries = []
    offset = 0
    
    while offset < len(data) and offset < size:
        record, record_len = parse_directory_record(data, offset)
        
        if record is None or record_len == 0:
            # Try next sector boundary
            next_sector = ((offset // 2048) + 1) * 2048
            if next_sector <= offset:
                break
            offset = next_sector
            continue
        
        if record['name'] not in ('.', '..'):
            entries.append(record)
        
        offset += record_len
    
    return entries


def extract_file(f, entry, output_path, mode='mode2'):
    """Extract a single file from the disc image."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    sectors_needed = (entry['data_length'] + 2047) // 2048
    data = read_sectors(f, entry['extent_lba'], sectors_needed, mode)
    
    # Trim to actual file size
    data = data[:entry['data_length']]
    
    with open(output_path, 'wb') as out:
        out.write(data)
    
    return len(data)


def extract_directory(f, lba, size, output_dir, path_prefix='', mode='mode2'):
    """Recursively extract a directory."""
    entries = list_directory(f, lba, size, mode)
    
    all_files = []
    
    for entry in entries:
        name = entry['name']
        full_path = f"{path_prefix}/{name}" if path_prefix else name
        output_path = os.path.join(output_dir, full_path)
        
        if entry['is_directory']:
            print(f"  [DIR]  {full_path}/")
            os.makedirs(output_path, exist_ok=True)
            sub_files = extract_directory(f, entry['extent_lba'], entry['data_length'], output_dir, full_path, mode)
            all_files.extend(sub_files)
        else:
            size_kb = entry['data_length'] / 1024
            print(f"  [FILE] {full_path} ({size_kb:.1f} KB, LBA={entry['extent_lba']})")
            try:
                extracted_size = extract_file(f, entry, output_path, mode)
                all_files.append({
                    'path': full_path,
                    'size': entry['data_length'],
                    'lba': entry['extent_lba']
                })
            except Exception as e:
                print(f"    ERROR: {e}")
    
    return all_files


def find_pvd(f, mode='mode2'):
    """Find the Primary Volume Descriptor."""
    # PVD is typically at sector 16
    for sector in range(16, 20):
        data = read_sector(f, sector, mode)
        if data and len(data) >= 6:
            # Check for PVD signature: type=1, 'CD001'
            if data[0] == 1 and data[1:6] == b'CD001':
                return sector, data
    return None, None


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Extract PS1 disc image filesystem')
    parser.add_argument('input', help='Input BIN file')
    parser.add_argument('-o', '--output', default='extracted', help='Output directory')
    parser.add_argument('--list-only', action='store_true', help='Only list files, do not extract')
    args = parser.parse_args()
    
    bin_path = args.input
    output_dir = args.output
    
    print(f"Opening {bin_path}...")
    
    with open(bin_path, 'rb') as f:
        # Find Primary Volume Descriptor
        pvd_sector, pvd_data = find_pvd(f)
        
        if pvd_data is None:
            print("ERROR: Could not find Primary Volume Descriptor!")
            print("Trying to dump raw sector 16 for debugging...")
            data = read_sector(f, 16)
            if data:
                print(f"  First 32 bytes: {data[:32].hex()}")
                print(f"  ASCII: {data[:32]}")
            sys.exit(1)
        
        print(f"Found PVD at sector {pvd_sector}")
        
        # Parse PVD
        system_id = pvd_data[8:40].decode('ascii', errors='replace').strip()
        volume_id = pvd_data[40:72].decode('ascii', errors='replace').strip()
        
        # Root directory record starts at offset 156 in PVD
        root_record = pvd_data[156:190]
        root_lba = struct.unpack_from('<I', root_record, 2)[0]
        root_size = struct.unpack_from('<I', root_record, 10)[0]
        
        print(f"System ID: {system_id}")
        print(f"Volume ID: {volume_id}")
        print(f"Root directory at LBA {root_lba}, size {root_size}")
        print()
        
        if args.list_only:
            print("Directory listing:")
            extract_directory(f, root_lba, root_size, output_dir, mode='mode2')
        else:
            print(f"Extracting to {output_dir}/...")
            os.makedirs(output_dir, exist_ok=True)
            files = extract_directory(f, root_lba, root_size, output_dir, mode='mode2')
            print(f"\nExtracted {len(files)} files.")
            
            # Write file list
            with open(os.path.join(output_dir, '_filelist.txt'), 'w') as fl:
                for f_info in files:
                    fl.write(f"{f_info['path']}\t{f_info['size']}\tLBA={f_info['lba']}\n")


if __name__ == '__main__':
    main()
