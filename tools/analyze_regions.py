#!/usr/bin/env python3
"""
Targeted analysis of known text regions in OP.APF.
Extracts and decodes text from areas where we found character names and menu data.
"""
import sys
import struct

def hex_dump(data, offset, length=256):
    """Pretty hex dump with Shift-JIS decode attempt."""
    end = min(offset + length, len(data))
    chunk = data[offset:end]
    
    for i in range(0, len(chunk), 16):
        line = chunk[i:i+16]
        hex_part = ' '.join(f'{b:02X}' for b in line)
        ascii_part = ''.join(chr(b) if 32 <= b <= 126 else '.' for b in line)
        print(f"  {offset+i:08X}: {hex_part:<48s} {ascii_part}")

def decode_sjis_region(data, start, length):
    """Decode a region as Shift-JIS, handling null terminators."""
    region = data[start:start+length]
    # Split on null bytes to find individual strings
    strings = []
    current = bytearray()
    for b in region:
        if b == 0x00:
            if current:
                try:
                    decoded = bytes(current).decode('shift_jis', errors='replace')
                    if len(decoded.strip()) >= 2:
                        strings.append(decoded.strip())
                except:
                    pass
                current = bytearray()
        else:
            current.append(b)
    if current:
        try:
            decoded = bytes(current).decode('shift_jis', errors='replace')
            if len(decoded.strip()) >= 2:
                strings.append(decoded.strip())
        except:
            pass
    return strings

def main():
    filepath = 'extracted/OP.APF'
    with open(filepath, 'rb') as f:
        data = f.read()
    
    print(f"Loaded {len(data):,} bytes\n")
    
    # === ANALYZE APF HEADER AND FILE TABLE ===
    print("="*70)
    print("APF HEADER ANALYSIS")
    print("="*70)
    
    # APF_v2.0 header
    magic = data[:8]
    num_entries = struct.unpack_from('<I', data, 8)[0]  # 404
    field_0c = struct.unpack_from('<I', data, 12)[0]    # 22
    field_10 = struct.unpack_from('<I', data, 16)[0]    # 19000
    
    print(f"Magic: {magic}")
    print(f"Number of entries: {num_entries}")
    print(f"Field 0x0C (groups?): {field_0c}")
    print(f"Field 0x10 (total sectors?): {field_10}")
    
    # Look for the file table - it should contain sector offsets
    # Try reading from after the header padding
    # The header seems padded with zeros to 0x1000
    print(f"\nLooking for file table starting positions...")
    
    # Read raw data around 0x1000 region
    for table_start in [0x20, 0x40, 0x80, 0x800, 0x1000, 0x1800, 0x2000]:
        # Read first few entries as 4-byte values
        vals = []
        for i in range(10):
            v = struct.unpack_from('<I', data, table_start + i * 4)[0]
            vals.append(v)
        non_zero = [v for v in vals if v > 0]
        if non_zero:
            print(f"\n  At 0x{table_start:04X}: {', '.join(f'0x{v:08X}' for v in vals[:10])}")
    
    # === EXAMINE PROG ENTRIES ===
    print("\n" + "="*70)
    print("PROG TABLE (at 0x0004C5A8)")
    print("="*70)
    hex_dump(data, 0x0004C598, 128)
    
    # === EXAMINE MENU AREA ===
    print("\n" + "="*70)
    print("MENU AREA (at 0x00094014)")
    print("="*70)
    hex_dump(data, 0x00094000, 512)
    
    # Decode strings in MENU area
    print("\nDecoded SJIS strings in MENU area (0x93F00 - 0x95000):")
    strings = decode_sjis_region(data, 0x93F00, 0x2000)
    for s in strings:
        if any(ord(c) > 0x7F for c in s) or len(s) >= 3:
            print(f"  {s}")
    
    # === EXAMINE MSG AREA ===
    print("\n" + "="*70)
    print("MSG AREA (at 0x0009AEC5)")
    print("="*70)
    hex_dump(data, 0x0009AEB0, 256)
    
    print("\nDecoded SJIS strings in MSG area (0x9AE00 - 0x9C000):")
    strings = decode_sjis_region(data, 0x9AE00, 0x2000)
    for s in strings:
        if any(ord(c) > 0x7F for c in s) or len(s) >= 3:
            print(f"  {s}")
    
    # === EXAMINE Grand Battle text area ===
    print("\n" + "="*70)
    print("GRAND BATTLE TEXT (at 0x000CC39C)")
    print("="*70)
    hex_dump(data, 0x000CC380, 512)
    
    print("\nDecoded SJIS strings near Grand Battle text:")
    strings = decode_sjis_region(data, 0x000CC000, 0x2000)
    for s in strings:
        if any(ord(c) > 0x7F for c in s) or len(s) >= 3:
            print(f"  {s}")
    
    # === EXAMINE USOPP area ===
    print("\n" + "="*70)
    print("USOPP / CHARACTER DATA (at 0x033EE0F6)")
    print("="*70)
    hex_dump(data, 0x033EE0E0, 512)
    
    print("\nDecoded SJIS strings near Usopp data:")
    strings = decode_sjis_region(data, 0x033EE000, 0x1000)
    for s in strings:
        if any(ord(c) > 0x7F for c in s) or len(s) >= 3:
            print(f"  {s}")
    
    # === EXAMINE Miss Doublefinger area ===
    print("\n" + "="*70)
    print("MISS DOUBLEFINGER DATA (at 0x01F0863E)")
    print("="*70)
    hex_dump(data, 0x01F08620, 512)
    
    print("\nDecoded SJIS strings near Miss Doublefinger data:")
    strings = decode_sjis_region(data, 0x01F08600, 0x1000)
    for s in strings:
        if any(ord(c) > 0x7F for c in s) or len(s) >= 3:
            print(f"  {s}")
    
    # === LOOK FOR THE SECOND GRAND BATTLE TEXT COPY ===
    print("\n" + "="*70)
    print("SECOND GRAND BATTLE COPY (at 0x03136AB8)")
    print("="*70)
    hex_dump(data, 0x03136AA0, 512)
    
    print("\nDecoded SJIS strings:")
    strings = decode_sjis_region(data, 0x03136A00, 0x2000)
    for s in strings:
        if any(ord(c) > 0x7F for c in s) or len(s) >= 3:
            print(f"  {s}")

if __name__ == '__main__':
    main()
