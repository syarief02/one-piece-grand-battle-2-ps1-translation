#!/usr/bin/env python3
"""
Inspect real decompressed story dialogue strings.
"""

import csv

with open("extracted/story_dialogues_decompressed.csv", "r", encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)
    rows = list(reader)

print(f"Total real story script rows: {len(rows)}\n")

for r in rows[:40]:
    ascii_jp = ascii(r['original_jp'])
    print(f"  {r['subfile']} [{r['offset']}]: {ascii_jp}")
