#!/usr/bin/env python3
"""
Inspect PNG textures in extracted/textures to find menu banners and UI elements.
"""

import os
from pathlib import Path
from PIL import Image

def analyze_textures():
    pngs = sorted(Path("extracted/textures").glob("*.png"))
    print(f"Found {len(pngs)} PNG textures.\n")
    
    for p in pngs:
        with Image.open(p) as img:
            # Check bounding box of non-transparent pixels
            bbox = img.getbbox()
            # Count non-transparent pixels
            extrema = img.getextrema()
            print(f"File: {p.name}")
            print(f"  Size: {img.size[0]}x{img.size[1]} | BBox: {bbox}")
            # Check unique colors count
            colors = img.getcolors(maxcolors=256)
            num_colors = len(colors) if colors else ">256"
            print(f"  Colors: {num_colors}\n")

if __name__ == "__main__":
    analyze_textures()
