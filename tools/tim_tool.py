#!/usr/bin/env python3
"""
PlayStation 1 TIM Texture Converter with Strict PS1 VRAM Validation.
PlayStation VRAM is strictly 1024x512 16-bit words.
"""

import os
import sys
import struct
from PIL import Image

def bgr555_to_rgb888(val):
    r = (val & 0x1F) << 3
    g = ((val >> 5) & 0x1F) << 3
    b = ((val >> 10) & 0x1F) << 3
    a = 255 if (val != 0) else 0
    return (r, g, b, a)

def decode_tim(data, offset=0):
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
            if clut_len <= 12 or pos + clut_len > len(data):
                return None, None
            clut_x, clut_y, clut_w, clut_h = struct.unpack_from('<HHHH', data, pos+4)
            
            # VRAM CLUT validation: max 256 colors wide, max 512 high
            if clut_w == 0 or clut_w > 256 or clut_h == 0 or clut_h > 512 or clut_x > 1024 or clut_y > 512:
                return None, None
                
            num_colors = clut_w * clut_h
            if 12 + num_colors * 2 != clut_len:
                return None, None
                
            color_pos = pos + 12
            for i in range(num_colors):
                c_val = struct.unpack_from('<H', data, color_pos + i*2)[0]
                palette.append(bgr555_to_rgb888(c_val))
            pos += clut_len
            
        if pos + 12 > len(data):
            return None, None
            
        img_len = struct.unpack_from('<I', data, pos)[0]
        if img_len <= 12 or pos + img_len > len(data):
            return None, None
            
        img_x, img_y, img_w, img_h = struct.unpack_from('<HHHH', data, pos+4)
        
        # Strict PS1 VRAM dimensions check:
        # VRAM is 1024 words wide by 512 lines high
        if img_w == 0 or img_w > 1024 or img_h == 0 or img_h > 512 or img_x > 1024 or img_y > 512:
            return None, None
            
        expected_img_data_len = img_w * img_h * 2
        if 12 + expected_img_data_len != img_len:
            return None, None
            
        img_data = data[pos+12 : pos+img_len]
        total_tim_size = (pos + img_len) - offset
        
        # Calculate pixel dimensions
        if bpp_mode == 0:  # 4-bit (16 colors)
            width = img_w * 4
            height = img_h
            img = Image.new("RGBA", (width, height))
            pixels = img.load()
            
            p_idx = 0
            for y in range(height):
                for x in range(0, width, 2):
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
                out_png = os.path.join(out_dir, f"{os.path.basename(bin_path)}_tim_{count:03d}_off_{pos:08X}_{img.size[0]}x{img.size[1]}.png")
                try:
                    img.save(out_png)
                    count += 1
                    pos += meta["total_size"]
                    continue
                except:
                    pass
        pos += 4
    return count
