#!/usr/bin/env python3
"""
Inspect extracted PNG textures.
"""

from pathlib import Path
from PIL import Image

def summarize_pngs():
    pngs = sorted(Path("extracted/textures").glob("*.png"))
    print(f"Total extracted PNGs: {len(pngs)}\n")
    for p in pngs:
        with Image.open(p) as img:
            print(f"{p.name:<60} | {img.size[0]}x{img.size[1]} | Mode: {img.mode}")

if __name__ == "__main__":
    summarize_pngs()
