#!/usr/bin/env python3
"""
Deep binary scanner for One Piece Grand Battle 2 data files.
Searches for known One Piece character names and game text in Shift-JIS encoding.
Also analyzes file structure (headers, magic bytes, compression signatures).
"""
import sys
import struct

def find_pattern(data, pattern, name, max_results=20):
    """Find all occurrences of a byte pattern."""
    results = []
    start = 0
    while True:
        pos = data.find(pattern, start)
        if pos == -1 or len(results) >= max_results:
            break
        # Get surrounding context
        ctx_start = max(0, pos - 8)
        ctx_end = min(len(data), pos + len(pattern) + 16)
        context_hex = data[ctx_start:ctx_end].hex(' ')
        results.append((pos, context_hex))
        start = pos + 1
    return results

def analyze_file_header(data, filename):
    """Analyze the first few bytes to identify file type."""
    print(f"\n{'='*70}")
    print(f"File: {filename}")
    print(f"Size: {len(data):,} bytes ({len(data)/1024/1024:.1f} MB)")
    print(f"First 64 bytes (hex): {data[:64].hex(' ')}")
    
    # Try to decode first 64 bytes as ASCII
    ascii_preview = ''.join(chr(b) if 32 <= b <= 126 else '.' for b in data[:64])
    print(f"First 64 bytes (ASCII): {ascii_preview}")
    
    # Check for common PS1/archive signatures
    magic = data[:4]
    if magic == b'\x00\x00\x00\x00':
        print("Header: Starts with null bytes (may be offset table or custom format)")
    elif magic[:2] == b'PK':
        print("Header: ZIP archive")
    elif magic == b'RIFF':
        print("Header: RIFF container")
    
    # Check for LZ compression markers
    # Common PS1 LZ compression: first 4 bytes = decompressed size
    decomp_size = struct.unpack_from('<I', data, 0)[0]
    print(f"First 4 bytes as uint32 (LE): {decomp_size} (0x{decomp_size:08X})")
    
    # Sample every 2048 bytes (PS1 sector size) and check for sub-file headers
    print("\nSampling sector-aligned positions for sub-file headers:")
    sector_headers = {}
    for offset in range(0, min(len(data), 1024*1024*10), 2048):  # Sample first 10MB
        header = data[offset:offset+4]
        if header not in sector_headers:
            sector_headers[header] = []
        if len(sector_headers[header]) < 3:
            sector_headers[header].append(offset)
    
    # Show most common headers
    by_count = sorted(sector_headers.items(), key=lambda x: -len(x[1]))
    for header, positions in by_count[:10]:
        pos_str = ', '.join(f'0x{p:08X}' for p in positions[:3])
        header_hex = header.hex(' ')
        print(f"  {header_hex} at {pos_str} (and more)")

def main():
    import os
    
    # Character names in Shift-JIS
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
    }
    
    # Common game menu text in Shift-JIS
    menu_items = {
        'バトル (Battle)': b'\x83\x6f\x83\x67\x83\x8b',
        'モード (Mode)': b'\x83\x82\x81\x5b\x83\x68',
        'オプション (Option)': b'\x83\x49\x83\x76\x83\x56\x83\x87\x83\x93',
        'ストーリー (Story)': b'\x83\x58\x83\x67\x81\x5b\x83\x8a\x81\x5b',
        'トレーニング (Training)': b'\x83\x67\x83\x8c\x81\x5b\x83\x6a\x83\x93\x83\x4f',
        'グランドバトル (Grand Battle)': b'\x83\x4f\x83\x89\x83\x93\x83\x68\x83\x6f\x83\x67\x83\x8b',
        '必殺技 (Special Move)': b'\x95\x4b\x8e\x45\x8b\x5a',
        '攻撃 (Attack)': b'\x8d\x55\x8c\x82',
        '防御 (Defense)': b'\x96\x68\x8c\xe4',
        'ゲーム (Game)': b'\x83\x51\x81\x5b\x83\x80',
    }
    
    files_to_scan = [
        ('extracted/SLPS_034.08', True),     # Full scan
        ('extracted/OP2.DAT', True),          # Full scan (smaller)
        ('extracted/OP.DAT', False),           # Sample scan (large file)
        ('extracted/OP.APF', False),           # Sample scan
    ]
    
    for filepath, full_scan in files_to_scan:
        if not os.path.exists(filepath):
            print(f"SKIP: {filepath} not found")
            continue
        
        with open(filepath, 'rb') as f:
            if full_scan:
                data = f.read()
            else:
                data = f.read(50 * 1024 * 1024)  # Read first 50MB for analysis
        
        analyze_file_header(data, filepath)
        
        # Search for character names
        print(f"\n--- Character names in {os.path.basename(filepath)} ---")
        found_any = False
        for name, pattern in names.items():
            results = find_pattern(data, pattern, name)
            if results:
                found_any = True
                print(f"\n  {name}: {len(results)} occurrence(s)")
                for pos, ctx in results[:5]:
                    print(f"    0x{pos:08X}: {ctx}")
        
        if not found_any:
            print("  No character names found!")
        
        # Search for menu text
        print(f"\n--- Menu/game text in {os.path.basename(filepath)} ---")
        found_menu = False
        for label, pattern in menu_items.items():
            results = find_pattern(data, pattern, label)
            if results:
                found_menu = True
                print(f"\n  {label}: {len(results)} occurrence(s)")
                for pos, ctx in results[:3]:
                    print(f"    0x{pos:08X}: {ctx}")
        
        if not found_menu:
            print("  No menu text found!")
        
        print()
        del data  # Free memory

if __name__ == '__main__':
    main()
