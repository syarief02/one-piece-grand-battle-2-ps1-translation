#!/usr/bin/env python3
"""
Decompressed Story Mode & Dialogue Extractor for One Piece Grand Battle 2.
Decompresses story subfiles (000-050) using Ganbarion LZSS and extracts real dialogues.
"""

import os
import sys
import csv
from pathlib import Path
from ganbarion_lz import decompress_ganbarion_lz

def extract_story_dialogues(out_csv="extracted/story_dialogues_decompressed.csv"):
    files = sorted(Path("extracted/apf_unpacked").glob("file_0*.bin"))
    dialogue_records = []
    
    print(f"Decompressing and scanning {len(files)} story script files...")
    
    for f in files:
        with open(f, "rb") as fp:
            raw_data = fp.read()
            
        data = decompress_ganbarion_lz(raw_data)
        
        pos = 0
        while pos < len(data) - 4:
            start = pos
            raw = bytearray()
            jp_char_count = 0
            
            while pos < len(data):
                b1 = data[pos]
                if pos + 1 < len(data) and ((0x81 <= b1 <= 0x9F) or (0xE0 <= b1 <= 0xEF)):
                    b2 = data[pos + 1]
                    if (0x40 <= b2 <= 0x7E) or (0x80 <= b2 <= 0xFC):
                        raw.append(b1)
                        raw.append(b2)
                        jp_char_count += 1
                        pos += 2
                        continue
                if 0x20 <= b1 <= 0x7E:
                    raw.append(b1)
                    pos += 1
                    continue
                if b1 in (0x0A, 0x0D):
                    raw.append(b1)
                    pos += 1
                    continue
                break
                
            if jp_char_count >= 2 and len(raw) >= 4:
                try:
                    text = raw.decode('shift_jis', errors='replace').strip()
                    # Real Japanese dialogue contains common Hiragana/Katakana ranges
                    has_hiragana_katakana = any(0x3040 <= ord(c) <= 0x30FF for c in text)
                    if has_hiragana_katakana:
                        dialogue_records.append({
                            "subfile": f.name,
                            "offset": f"0x{start:06X}",
                            "length": len(raw),
                            "original_jp": text,
                            "english_translation": ""
                        })
                except:
                    pass
            pos += 1
            
    print(f"Extracted {len(dialogue_records):,} real dialogue/script strings!")
    
    with open(out_csv, "w", newline="", encoding="utf-8-sig") as csv_f:
        writer = csv.DictWriter(csv_f, fieldnames=["subfile", "offset", "length", "original_jp", "english_translation"])
        writer.writeheader()
        writer.writerows(dialogue_records)
        
    print(f"Saved decompressed story dialogues to '{out_csv}'!")

if __name__ == "__main__":
    extract_story_dialogues()
