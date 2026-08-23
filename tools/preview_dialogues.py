#!/usr/bin/env python3
"""
Preview sample extracted story dialogues.
"""

import csv

with open("extracted/story_dialogues.csv", "r", encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)
    rows = list(reader)

print(f"Total extracted script rows: {len(rows):,}\n")

# Filter out very short or junk strings to show real dialogue
meaningful = [r for r in rows if len(r["original_jp"]) >= 6]
print(f"Meaningful dialogue lines (>= 6 chars): {len(meaningful):,}\n")

for r in meaningful[:35]:
    # Clean non-ascii for safe console printing
    safe_jp = r['original_jp'][:50]
    print(f"[{r['subfile']} @ {r['offset']}] {safe_jp}")
