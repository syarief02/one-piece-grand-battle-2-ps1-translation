#!/usr/bin/env python3
"""
Comprehensive APF archive scanner for One Piece Grand Battle 2.
Parses the APF_v2.0 header and scans entire file for all game text.
"""
import sys
import struct
import os

def parse_apf_header(data):
    """Parse the APF_v2.0 archive header."""
    magic = data[:8].decode('ascii', errors='replace')
    print(f"Magic: {magic}")
    
    # Parse header fields
    # APF_v2.0 + some header data
    # Offset 8: seems to be some count or size
    val_08 = struct.unpack_from('<I', data, 8)[0]
    val_0c = struct.unpack_from('<I', data, 12)[0]
    val_10 = struct.unpack_from('<I', data, 16)[0]
    val_14 = struct.unpack_from('<I', data, 20)[0]
    val_18 = struct.unpack_from('<I', data, 24)[0]
    val_1c = struct.unpack_from('<I', data, 28)[0]
    
    print(f"Header fields:")
    print(f"  Offset 0x08: {val_08} (0x{val_08:08X})")
    print(f"  Offset 0x0C: {val_0c} (0x{val_0c:08X})")
    print(f"  Offset 0x10: {val_10} (0x{val_10:08X}) = {val_10 * 2048} bytes as sectors")
    print(f"  Offset 0x14: {val_14} (0x{val_14:08X})")
    print(f"  Offset 0x18: {val_18} (0x{val_18:08X})")
    print(f"  Offset 0x1C: {val_1c} (0x{val_1c:08X})")
    
    # Look for a file table / directory structure
    print("\nSearching for file entry table...")
    # Try to find entries starting after the header
    # Common format: offset (4 bytes) + size (4 bytes) for each entry
    
    # Check if there's a count at offset 0x08 that could be number of files
    possible_count = val_08
    if 1 < possible_count < 10000:
        print(f"  Possible file count: {possible_count}")
        # Try reading entries starting at various offsets
        for table_start in [0x40, 0x80, 0x100, 0x200]:
            if table_start + possible_count * 8 <= len(data):
                entries = []
                valid = True
                for i in range(min(possible_count, 20)):
                    entry_offset = struct.unpack_from('<I', data, table_start + i * 8)[0]
                    entry_size = struct.unpack_from('<I', data, table_start + i * 8 + 4)[0]
                    if entry_offset > len(data) or entry_size > len(data):
                        valid = False
                        break
                    entries.append((entry_offset, entry_size))
                
                if valid and entries:
                    print(f"  Trying table at 0x{table_start:04X} (8-byte entries):")
                    for i, (off, sz) in enumerate(entries):
                        print(f"    Entry {i}: offset=0x{off:08X}, size=0x{sz:08X} ({sz:,} bytes)")


def find_all_sjis_text_blocks(data, min_length=6):
    """Find substantial blocks of Shift-JIS text in the file."""
    blocks = []
    i = 0
    length = len(data)
    
    while i < length:
        start = i
        raw = bytearray()
        char_count = 0
        jp_chars = 0
        
        while i < length:
            b1 = data[i]
            # Double-byte Shift-JIS (full-width Japanese characters)
            if i + 1 < length and ((0x81 <= b1 <= 0x9F) or (0xE0 <= b1 <= 0xEF)):
                b2 = data[i + 1]
                if (0x40 <= b2 <= 0x7E) or (0x80 <= b2 <= 0xFC):
                    raw.append(b1)
                    raw.append(b2)
                    char_count += 1
                    jp_chars += 1
                    i += 2
                    continue
            # Single-byte printable ASCII
            if 0x20 <= b1 <= 0x7E:
                raw.append(b1)
                char_count += 1
                i += 1
                continue
            # Half-width katakana
            if 0xA1 <= b1 <= 0xDF:
                raw.append(b1)
                char_count += 1
                jp_chars += 1
                i += 1
                continue
            # Newline
            if b1 in (0x0A, 0x0D):
                raw.append(b1)
                i += 1
                continue
            # Null terminator - check if there's more text nearby
            if b1 == 0x00 and char_count > 0:
                break
            break
        
        # We want substantial text blocks with actual Japanese chars
        if char_count >= min_length and jp_chars >= 2:
            try:
                decoded = raw.decode('shift_jis', errors='replace')
                blocks.append((start, len(raw), decoded, jp_chars))
            except:
                pass
        
        if i == start:
            i += 1
    
    return blocks


def main():
    filepath = 'extracted/OP.APF'
    print(f"Loading {filepath}...")
    
    with open(filepath, 'rb') as f:
        data = f.read()
    
    print(f"Loaded {len(data):,} bytes ({len(data)/1024/1024:.1f} MB)")
    print()
    
    # Parse header
    parse_apf_header(data)
    print()
    
    # Comprehensive character name search
    names = {
        'ルフィ (Luffy)': b'\x83\x8b\x83\x74\x83\x42',
        'ゾロ (Zoro)': b'\x83\x5a\x83\x8d',
        'ナミ (Nami)': b'\x83\x69\x83\x7e',
        'ウソップ (Usopp)': b'\x83\x45\x83\x5c\x83\x62\x83\x76',
        'サンジ (Sanji)': b'\x83\x54\x83\x93\x83\x57',
        'チョッパー (Chopper)': b'\x83\x60\x83\x87\x83\x62\x83\x70\x81\x5b',
        'ロビン (Robin)': b'\x83\x8d\x83\x72\x83\x93',
        'エース (Ace)': b'\x83\x47\x81\x5b\x83\x58',
        'クロコダイル (Crocodile)': b'\x83\x4e\x83\x8d\x83\x52\x83\x5f\x83\x43\x83\x8b',
        'ビビ (Vivi)': b'\x83\x72\x83\x72',
        'スモーカー (Smoker)': b'\x83\x58\x83\x82\x81\x5b\x83\x4a\x81\x5b',
        'バギー (Buggy)': b'\x83\x6f\x83\x4d\x81\x5b',
        'アルビダ (Alvida)': b'\x83\x41\x83\x8b\x83\x72\x83\x5f',
        'シャンクス (Shanks)': b'\x83\x56\x83\x83\x83\x93\x83\x4e\x83\x58',
        'ミホーク (Mihawk)': b'\x83\x7e\x83\x7a\x81\x5b\x83\x4e',
        'ワポル (Wapol)': b'\x83\x8f\x83\x7c\x83\x8b',
        'クリーク (Krieg)': b'\x83\x4e\x83\x8a\x81\x5b\x83\x4e',
        'アーロン (Arlong)': b'\x83\x41\x81\x5b\x83\x8d\x83\x93',
        'ボン・クレー (Bon Clay)': b'\x83\x7b\x83\x93\x81\x45\x83\x4e\x83\x8c\x81\x5b',
        'タシギ (Tashigi)': b'\x83\x5e\x83\x56\x83\x4d',
        'Mr.2': b'\x82\x6c\x82\x92\x81\x44\x82\x51',
    }
    
    print("=== FULL FILE Character Name Search ===")
    name_locations = {}
    for name, pattern in names.items():
        offsets = []
        start = 0
        while True:
            pos = data.find(pattern, start)
            if pos == -1:
                break
            offsets.append(pos)
            start = pos + 1
        if offsets:
            name_locations[name] = offsets
            print(f"  {name}: {len(offsets)} occurrence(s)")
            for pos in offsets[:5]:
                # Extract surrounding context as text
                ctx_start = max(0, pos - 20)
                ctx_end = min(len(data), pos + len(pattern) + 40)
                ctx_bytes = data[ctx_start:ctx_end]
                try:
                    ctx_text = ctx_bytes.decode('shift_jis', errors='replace')
                except:
                    ctx_text = ctx_bytes.hex(' ')
                print(f"    0x{pos:08X}: ...{ctx_text}...")
        else:
            print(f"  {name}: NOT FOUND")
    
    # Find text blocks in the areas where we found character names
    print("\n=== Scanning for ALL text blocks (6+ meaningful chars with Japanese) ===")
    text_blocks = find_all_sjis_text_blocks(data, min_length=6)
    
    # Filter to most interesting ones (longer blocks)
    interesting = [b for b in text_blocks if b[1] >= 10]
    interesting.sort(key=lambda x: -x[1])  # Sort by length, longest first
    
    print(f"Found {len(text_blocks)} text blocks total, {len(interesting)} with 10+ bytes")
    print("\nTop 100 longest text blocks:")
    for offset, raw_len, decoded, jp_count in interesting[:100]:
        # Truncate for display
        display = decoded[:120].replace('\n', '\\n').replace('\r', '\\r')
        print(f"  0x{offset:08X} [{raw_len:5d} bytes, {jp_count:3d} JP chars]: {display}")
    
    # Also search for program text (PROG, menu items, etc.)
    print("\n=== Searching for program/overlay identifiers ===")
    prog_patterns = [
        (b'PROG', 'PROG'),
        (b'MENU', 'MENU'),
        (b'FONT', 'FONT'),
        (b'TEXT', 'TEXT'),
        (b'MSG', 'MSG'),
        (b'STR', 'STR'),
        (b'TBL', 'TBL'),
        (b'.TIM', '.TIM'),
        (b'.VAB', '.VAB'),
        (b'.VH', '.VH'),
        (b'.VB', '.VB'),
    ]
    
    for pattern, label in prog_patterns:
        count = 0
        start = 0
        first_offsets = []
        while True:
            pos = data.find(pattern, start)
            if pos == -1:
                break
            count += 1
            if len(first_offsets) < 5:
                first_offsets.append(pos)
            start = pos + 1
        if count > 0:
            locs = ', '.join(f'0x{p:08X}' for p in first_offsets)
            print(f"  {label}: {count} occurrences. First at: {locs}")

if __name__ == '__main__':
    main()
