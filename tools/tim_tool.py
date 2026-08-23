#!/usr/bin/env python3
"""
PlayStation 1 TIM Texture Converter & Inserter
Decodes PS1 .TIM files to .PNG and encodes .PNG images back into .TIM format.
Supports 4-bit (16 colors), 8-bit (256 colors), 16-bit (BGR555), and 24-bit RGB.
"""

import os
import sys
import struct
from PIL import Image

def bgr555_to_rgb888(val):
    r = (val & 0x1F) << 3
    g = ((val >> 5) & 0x1F) << 3
    b = ((val >> 10) & 0x1F) << 3
    a = 255 if (val != 0) else 0  # 0x0000 is often transparent in PS1
    return (r, g, b, a)

def rgb888_to_bgr555(r, g, b, a=255):
    if a < 128:
        return 0x0000
    r5 = (r >> 3) & 0x1F
    g5 = (g >> 3) & 0x1F
    b5 = (b >> 3) & 0x1F
    stp = 0x8000 if (r5 != 0 or g5 != 0 or b5 != 0) else 0
    return (b5 << 10) | (g5 << 5) | r5 | stp

def decode_tim(data, offset=0):
    """Decode raw bytes into a PIL Image and metadata."""
    try:
        if offset + 32 > len(data) or data[offset:offset+4] != b'\x10\x00\x00\x00':
            return None, None
            
        flags = struct.unpack_from('<I', data, offset+4)[0]
        bpp_mode = flags & 0x07
        has_clut = (flags & 0x08) != 0
        
        if bpp_mode not in (0, 1, 2, 3):
            return None, None
            
        pos = offset + 8
        palette = []
        clut_x, clut_y, clut_w, clut_h = 0, 0, 0, 0
        
        if has_clut:
            if pos + 12 > len(data):
                return None, None
            clut_len = struct.unpack_from('<I', data, pos)[0]
            if pos + clut_len > len(data):
                return None, None
            clut_x, clut_y, clut_w, clut_h = struct.unpack_from('<HHHH', data, pos+4)
            num_colors = clut_w * clut_h
            
            color_pos = pos + 12
            for i in range(num_colors):
                if color_pos + i*2 + 2 > len(data):
                    break
                c_val = struct.unpack_from('<H', data, color_pos + i*2)[0]
                palette.append(bgr555_to_rgb888(c_val))
            pos += clut_len
            
        if pos + 12 > len(data):
            return None, None
            
        img_len = struct.unpack_from('<I', data, pos)[0]
        if pos + img_len > len(data) or img_len <= 12:
            return None, None
            
        img_x, img_y, img_w, img_h = struct.unpack_from('<HHHH', data, pos+4)
        img_data = data[pos+12 : pos+img_len]
        
        if img_w == 0 or img_h == 0:
            return None, None
            
        total_tim_size = (pos + img_len) - offset
        
        # Calculate dimensions in pixels
        if bpp_mode == 0:  # 4-bit (16 colors)
            width = img_w * 4
            height = img_h
            img = Image.new("RGBA", (width, height))
            pixels = img.load()
            
            p_idx = 0
            for y in range(height):
                for x in range(0, width, 2):
                    if p_idx < len(img_data):
                        b = img_data[p_idx]
                        p1 = b & 0x0F
                        p2 = (b >> 4) & 0x0F
                        
                        c1 = palette[p1] if p1 < len(palette) else (0,0,0,0)
                        c2 = palette[p2] if p2 < len(palette) else (0,0,0,0)
                        
                        pixels[x, y] = c1
                        if x + 1 < width:
                            pixels[x+1, y] = c2
                        p_idx += 1
                        
        elif bpp_mode == 1:  # 8-bit (256 colors)
            width = img_w * 2
            height = img_h
            img = Image.new("RGBA", (width, height))
            pixels = img.load()
            
            p_idx = 0
            for y in range(height):
                for x in range(width):
                    if p_idx < len(img_data):
                        idx = img_data[p_idx]
                        c = palette[idx] if idx < len(palette) else (0,0,0,0)
                        pixels[x, y] = c
                        p_idx += 1
                        
        elif bpp_mode == 2:  # 16-bit direct BGR555
            width = img_w
            height = img_h
            img = Image.new("RGBA", (width, height))
            pixels = img.load()
            
            p_idx = 0
            for y in range(height):
                for x in range(width):
                    if p_idx + 2 <= len(img_data):
                        val = struct.unpack_from('<H', img_data, p_idx)[0]
                        pixels[x, y] = bgr555_to_rgb888(val)
                        p_idx += 2
                        
        elif bpp_mode == 3:  # 24-bit direct RGB
            width = (img_w * 2) // 3
            height = img_h
            img = Image.new("RGBA", (width, height))
            pixels = img.load()
            
            p_idx = 0
            for y in range(height):
                for x in range(width):
                    if p_idx + 3 <= len(img_data):
                        r = img_data[p_idx]
                        g = img_data[p_idx+1]
                        b = img_data[p_idx+2]
                        pixels[x, y] = (r, g, b, 255)
                        p_idx += 3
        else:
            return None, None
            
        meta = {
            "bpp_mode": bpp_mode,
            "has_clut": has_clut,
            "clut_x": clut_x, "clut_y": clut_y, "clut_w": clut_w, "clut_h": clut_h,
            "img_x": img_x, "img_y": img_y, "img_w": img_w, "img_h": img_h,
            "total_size": total_tim_size,
            "palette": palette
        }
        return img, meta
    except Exception:
        return None, None

def extract_all_tims_from_file(bin_path, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    with open(bin_path, "rb") as f:
        data = f.read()
        
    count = 0
    pos = 0
    while pos < len(data) - 32:
        if data[pos:pos+4] == b'\x10\x00\x00\x00':
            img, meta = decode_tim(data, pos)
            if img:
                out_png = os.path.join(out_dir, f"{os.path.basename(bin_path)}_tim_{count:03d}_off_{pos:08X}.png")
                try:
                    img.save(out_png)
                    count += 1
                    pos += meta["total_size"]
                    continue
                except:
                    pass
        pos += 4
    return count

if __name__ == "__main__":
    if len(sys.argv) > 2:
        extract_all_tims_from_file(sys.argv[1], sys.argv[2])
    else:
        print("Usage: python tim_tool.py <input_bin> <output_dir>")
