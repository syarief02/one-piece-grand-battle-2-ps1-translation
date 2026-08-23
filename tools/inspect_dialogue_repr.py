#!/usr/bin/env python3
"""
Inspect Japanese character strings in story_dialogues.csv.
"""

import csv

with open("extracted/story_dialogues.csv", "r", encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)
    rows = list(reader)

print(f"Total rows: {len(rows)}")
for r in rows[:30]:
    raw_repr = ascii(r['original_jp'])
    print(f"  {r['subfile']} [{r['offset']}]: {raw_repr}")
