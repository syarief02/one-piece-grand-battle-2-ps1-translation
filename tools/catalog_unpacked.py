#!/usr/bin/env python3
"""
Catalog and scan all unpacked subfiles for text and data structures.
"""

import os
import sys
import csv
from pathlib import Path


def scan_unpacked():
    files = sorted(Path("extracted/apf_unpacked").glob("file_*.bin")) + sorted(Path("extracted/apf_unpacked").glob("file_*.tim"))
    results = []
    
    # Target keywords to identify files
    keywords = {
        "Menu/System": [b'\x83\x6f\x83\x67\x83\x8b', b'\x83\x82\x81\x5b\x83\x68', b'\x83\x49\x83\x76\x83\x56\x83\x87\x83\x93', b'OPTIONS', b'TREASURE', b'GRAND BATTLE'],
        "Characters": [b'\x83\x8b\x83\x74\x83\x42', b'\x83\x5a\x83\x8d', b'\x83\x69\x83\x7e', b'\x83\x45\x83\x5c\x83\x62\x83\x76', b'\x83\x54\x83\x93\x83\x57'],
        "Story/Text": [b'\x95\x4b\x8e\x45', b'\x8e\x9f', b'\x81\x41', b'\x81\x42', b'\x81\x5b']
    }
    
    summary_rows = []
    
    for fpath in files:
        with open(fpath, "rb") as f:
            data = f.read()
            
        tags = []
        text_samples = []
        
        # Check keywords
        for category, kw_list in keywords.items():
            for kw in kw_list:
                if kw in data:
                    tags.append(category)
                    break
                    
        # Check for strings
        curr = bytearray()
        found_strings = []
        for b in data:
            if 0x20 <= b <= 0x7E or (0xA1 <= b <= 0xDF):
                curr.append(b)
            elif b in (0x0A, 0x0D):
                curr.append(b)
            else:
                if len(curr) >= 4:
                    try:
                        s = curr.decode('shift_jis', errors='replace').strip()
                        if len(s) >= 4 and any(c.isalnum() for c in s):
                            found_strings.append(s)
                    except:
                        pass
                curr = bytearray()
                
        if tags or found_strings:
            summary_rows.append({
                "file": fpath.name,
                "size": len(data),
                "tags": ", ".join(set(tags)),
                "strings_count": len(found_strings),
                "sample": " | ".join(found_strings[:6])
            })
            
    print(f"Scanned {len(files)} files. Found {len(summary_rows)} files with text/keywords.")
    print("-" * 80)
    for row in summary_rows[:25]:
        print(f"[{row['file']}] ({row['size']}B) [{row['tags']}] - Strings: {row['strings_count']}")
        if row['sample']:
            print(f"   Sample: {row['sample'][:120]}")
            
    # Write summary CSV
    with open("extracted/apf_unpacked/_text_inventory.csv", "w", newline="", encoding="utf-8-sig") as out_csv:
        writer = csv.DictWriter(out_csv, fieldnames=["file", "size", "tags", "strings_count", "sample"])
        writer.writeheader()
        writer.writerows(summary_rows)

if __name__ == "__main__":
    scan_unpacked()
