#!/usr/bin/env python3
"""
PS1 ROM Text Scanner for One Piece Grand Battle 2
Scans BIN files for Shift-JIS encoded text strings and dumps them for translation.
"""

import os
import sys
import csv
import struct
import codecs
import argparse
from pathlib import Path


def is_valid_sjis_char(b1, b2=None):
    """Check if byte(s) form a valid Shift-JIS character."""
    if b2 is None:
        return (0x20 <= b1 <= 0x7E) or (0xA1 <= b1 <= 0xDF)
    else:
        return ((0x81 <= b1 <= 0x9F) or (0xE0 <= b1 <= 0xEF)) and \
               ((0x40 <= b2 <= 0x7E) or (0x80 <= b2 <= 0xFC))


def extract_sjis_strings(data, min_length=3):
    """Extract Shift-JIS encoded strings from binary data."""
    strings = []
    i = 0
    length = len(data)
    
    while i < length:
        start = i
        raw = bytearray()
        char_count = 0
        
        while i < length:
            b1 = data[i]
            if i + 1 < length and ((0x81 <= b1 <= 0x9F) or (0xE0 <= b1 <= 0xEF)):
                b2 = data[i + 1]
                if (0x40 <= b2 <= 0x7E) or (0x80 <= b2 <= 0xFC):
                    raw.append(b1)
                    raw.append(b2)
                    char_count += 1
                    i += 2
                    continue
            if 0x20 <= b1 <= 0x7E:
                raw.append(b1)
                char_count += 1
                i += 1
                continue
            if 0xA1 <= b1 <= 0xDF:
                raw.append(b1)
                char_count += 1
                i += 1
                continue
            if b1 in (0x0A, 0x0D):
                raw.append(b1)
                i += 1
                continue
            break
        
        if char_count >= min_length and len(raw) > 0:
            try:
                decoded = raw.decode('shift_jis', errors='replace')
                printable_ratio = sum(1 for c in decoded if c.isprintable() or c in '\n\r') / len(decoded)
                if printable_ratio > 0.7:
                    strings.append((start, bytes(raw), decoded))
            except Exception:
                pass
        
        if i == start:
            i += 1
    
    return strings


def extract_ascii_strings(data, min_length=4):
    """Extract pure ASCII strings from binary data."""
    strings = []
    i = 0
    length = len(data)
    
    while i < length:
        start = i
        raw = bytearray()
        
        while i < length:
            b = data[i]
            if 0x20 <= b <= 0x7E:
                raw.append(b)
                i += 1
            elif b in (0x0A, 0x0D) and len(raw) > 0:
                raw.append(b)
                i += 1
            else:
                break
        
        if len(raw) >= min_length:
            decoded = raw.decode('ascii', errors='replace').strip()
            if len(decoded) >= min_length:
                strings.append((start, bytes(raw), decoded))
        
        if i == start:
            i += 1
    
    return strings


def scan_file(filepath, min_length=3):
    """Scan a single file for text strings."""
    with open(filepath, 'rb') as f:
        data = f.read()
    
    print(f"  Scanning {filepath} ({len(data):,} bytes)...")
    
    sjis_strings = extract_sjis_strings(data, min_length=min_length)
    ascii_strings = extract_ascii_strings(data, min_length=max(min_length, 4))
    
    all_strings = []
    sjis_offsets = set()
    for offset, raw, decoded in sjis_strings:
        sjis_offsets.update(range(offset, offset + len(raw)))
        all_strings.append((offset, raw, decoded, 'SJIS'))
    
    for offset, raw, decoded in ascii_strings:
        ascii_range = set(range(offset, offset + len(raw)))
        if not ascii_range & sjis_offsets:
            all_strings.append((offset, raw, decoded, 'ASCII'))
    
    all_strings.sort(key=lambda x: x[0])
    return all_strings


def categorize_string(text):
    """Attempt to categorize a string based on its content."""
    text_lower = text.lower().strip()
    
    if any(k in text_lower for k in ['menu', 'select', 'mode', 'option', 'start', 'exit', 'continue', 'save', 'load']):
        return 'MENU'
    if any(k in text_lower for k in ['attack', 'defense', 'power', 'speed', 'health', 'hp', 'mp']):
        return 'GAMEPLAY'
    if any(k in text_lower for k in ['.tim', '.vab', '.seq', '.dat', '.bin', '.exe']):
        return 'FILENAME'
    if text_lower.startswith('slps') or text_lower.startswith('scps'):
        return 'SYSTEM'
    
    has_japanese = any(ord(c) > 0x7F for c in text)
    if has_japanese:
        return 'JAPANESE_TEXT'
    
    return 'OTHER'


def main():
    parser = argparse.ArgumentParser(description='Scan PS1 ROM files for text strings')
    parser.add_argument('input', help='Input file or directory to scan')
    parser.add_argument('-o', '--output', default='extracted_strings.csv', help='Output CSV file')
    parser.add_argument('-m', '--min-length', type=int, default=3, help='Minimum string length')
    parser.add_argument('--ascii-only', action='store_true', help='Only extract ASCII strings')
    args = parser.parse_args()
    
    input_path = Path(args.input)
    all_results = []
    
    if input_path.is_file():
        files = [input_path]
    elif input_path.is_dir():
        files = sorted(input_path.rglob('*'))
        files = [f for f in files if f.is_file()]
    else:
        print(f"Error: {input_path} not found")
        sys.exit(1)
    
    print(f"Scanning {len(files)} file(s)...")
    
    for filepath in files:
        try:
            strings = scan_file(str(filepath), args.min_length)
            for offset, raw, decoded, encoding in strings:
                if args.ascii_only and encoding != 'ASCII':
                    continue
                category = categorize_string(decoded)
                all_results.append({
                    'file': str(filepath.relative_to(input_path) if input_path.is_dir() else filepath.name),
                    'offset': f'0x{offset:08X}',
                    'encoding': encoding,
                    'category': category,
                    'original': decoded,
                    'translation': '',
                    'raw_hex': raw.hex()
                })
        except Exception as e:
            print(f"  Error scanning {filepath}: {e}")
    
    if all_results:
        with open(args.output, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=['file', 'offset', 'encoding', 'category', 'original', 'translation', 'raw_hex'])
            writer.writeheader()
            writer.writerows(all_results)
        
        print(f"\nExtracted {len(all_results)} strings to {args.output}")
        
        categories = {}
        for r in all_results:
            cat = r['category']
            categories[cat] = categories.get(cat, 0) + 1
        print("\nCategory breakdown:")
        for cat, count in sorted(categories.items()):
            print(f"  {cat}: {count}")
    else:
        print("\nNo strings found.")


if __name__ == '__main__':
    main()
