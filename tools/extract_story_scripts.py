#!/usr/bin/env python3
"""
Story Mode & Dialogue Extractor for One Piece Grand Battle 2.
Extracts dialogue scripts and text events from story files (001-050).
"""

import os
import sys
import csv
from pathlib import Path

def extract_story_dialogues(out_csv="extracted/story_dialogues.csv"):
    files = sorted(Path("extracted/apf_unpacked").glob("file_0*.bin"))
    dialogue_records = []
    
    print(f"Scanning {len(files)} story script files for Japanese dialogue...")
    
    for f in files:
        with open(f, "rb") as fp:
            data = fp.read()
            
        pos = 0
        while pos < len(data) - 4:
            # Look for Shift-JIS text sequences (full-width punctuation, hiragana, katakana, kanji)
            # Full-width punctuation: 0x81 0x41 (comma), 0x81 0x42 (period), 0x81 0x5B (dash), 0x81 0x49 (!)
            # Hiragana/Katakana: 0x82 0x9F - 0x82 0xF1, 0x83 0x40 - 0x83 0x96
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
                    # Filter out garbage
                    if any(c for c in text if ord(c) > 0x3000):
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
            
    print(f"Extracted {len(dialogue_records)} dialogue/script strings!")
    
    with open(out_csv, "w", newline="", encoding="utf-8-sig") as csv_f:
        writer = csv.DictWriter(csv_f, fieldnames=["subfile", "offset", "length", "original_jp", "english_translation"])
        writer.writeheader()
        writer.writerows(dialogue_records)
        
    print(f"Saved story dialogues to '{out_csv}'!")
    
    # Print sample
    print("\n=== Sample Extracted Dialogue Lines ===")
    for r in dialogue_records[:20]:
        print(f"[{r['subfile']} @ {r['offset']}] {r['original_jp']}")

if __name__ == "__main__":
    extract_story_dialogues()
