#!/usr/bin/env python3
"""
Scan all extracted PNGs to find menu button textures.
"""

from pathlib import Path
from PIL import Image

pngs = sorted(Path("extracted/textures").glob("*.png")) + sorted(Path("extracted/textures_decompressed").glob("*.png"))
print(f"Total textures to scan: {len(pngs)}\n")

for p in pngs:
    with Image.open(p) as img:
        w, h = img.size
        # Filter for typical menu button / banner dimensions: width between 64 and 512, height between 16 and 256
        if (64 <= w <= 512 and 16 <= h <= 256) or (32 <= w <= 64 and 32 <= h <= 64):
            print(f"{p.name:<65} | {w}x{h} | Mode={img.mode}")
