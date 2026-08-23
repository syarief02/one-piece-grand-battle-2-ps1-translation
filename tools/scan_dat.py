#!/usr/bin/env python3
"""
Quick scan of OP.DAT for character names (full file).
"""
import sys
import struct

names = {
    'ルフィ (Luffy)': b'\x83\x8b\x83\x74\x83\x42',
    'ゾロ (Zoro)': b'\x83\x5a\x83\x8d',
    'ナミ (Nami)': b'\x83\x69\x83\x7e',
    'ウソップ (Usopp)': b'\x83\x45\x83\x5c\x83\x62\x83\x76',
    'サンジ (Sanji)': b'\x83\x54\x83\x93\x83\x57',
    'チョッパー (Chopper)': b'\x83\x60\x83\x87\x83\x62\x83\x70\x81\x5b',
    'グランドバトル (Grand Battle)': b'\x83\x4f\x83\x89\x83\x93\x83\x68\x83\x6f\x83\x67\x83\x8b',
    'バトル (Battle)': b'\x83\x6f\x83\x67\x83\x8b',
    'モード (Mode)': b'\x83\x82\x81\x5b\x83\x68',
    'オプション (Option)': b'\x83\x49\x83\x76\x83\x56\x83\x87\x83\x93',
    'ストーリー (Story)': b'\x83\x58\x83\x67\x81\x5b\x83\x8a\x81\x5b',
}

for filepath in ['extracted/OP.DAT', 'extracted/OP2.DAT']:
    print(f"\n=== Scanning {filepath} (FULL) ===")
    with open(filepath, 'rb') as f:
        # Read in chunks to handle large files
        chunk_size = 64 * 1024 * 1024  # 64MB chunks
        chunk_idx = 0
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            base_offset = chunk_idx * chunk_size
            
            for name, pattern in names.items():
                start = 0
                while True:
                    pos = chunk.find(pattern, start)
                    if pos == -1:
                        break
                    abs_pos = base_offset + pos
                    # Get context
                    ctx_start = max(0, pos - 10)
                    ctx_end = min(len(chunk), pos + len(pattern) + 30)
                    ctx = chunk[ctx_start:ctx_end]
                    try:
                        decoded = ctx.decode('shift_jis', errors='replace')
                    except:
                        decoded = ctx.hex(' ')
                    print(f"  {name} at 0x{abs_pos:08X}: {decoded}")
                    start = pos + 1
            
            chunk_idx += 1
    
    print(f"  Scan complete for {filepath}")
