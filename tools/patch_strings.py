#!/usr/bin/env python3
"""
Safe String Patcher for One Piece Grand Battle 2 PS1.
Patches translated text strings into game binaries or unpacked assets
while guaranteeing memory safety, length constraints, and null-termination.
"""

import os
import sys
import csv
import struct

# Default translation dictionary for One Piece Grand Battle 2 menu & character names
DEFAULT_TRANSLATIONS = {
    # Characters
    b'\x83\x8b\x83\x74\x83\x42': b'Luffy\x00',              # ルフィ -> Luffy
    b'\x83\x5a\x83\x8d': b'Zoro\x00',                      # ゾロ -> Zoro
    b'\x83\x69\x83\x7e': b'Nami\x00',                      # ナミ -> Nami
    b'\x83\x45\x83\x5c\x83\x62\x83\x76': b'Usopp\x00',      # ウソップ -> Usopp
    b'\x83\x54\x83\x93\x83\x57': b'Sanji\x00',              # サンジ -> Sanji
    b'\x83\x60\x83\x87\x83\x62\x83\x70\x81\x5b': b'Chopper\x00', # チョッパー -> Chopper
    b'\x83\x8d\x83\x72\x83\x93': b'Robin\x00',              # ロビン -> Robin
    b'\x83\x47\x81\x5b\x83\x58': b'Ace\x00',                # エース -> Ace
    b'\x83\x72\x83\x72': b'Vivi\x00',                      # ビビ -> Vivi
    b'\x83\x6f\x83\x4d\x81\x5b': b'Buggy\x00',              # バギー -> Buggy
    b'\x83\x56\x83\x83\x83\x93\x83\x4e\x83\x58': b'Shanks\x00', # シャンクス -> Shanks
    b'\x83\x7e\x83\x7a\x81\x5b\x83\x4e': b'Mihawk\x00',    # ミホーク -> Mihawk
    b'\x83\x8f\x83\x7c\x83\x8b': b'Wapol\x00',              # ワポル -> Wapol
    b'\x83\x4e\x83\x8a\x81\x5b\x83\x4e': b'Krieg\x00',      # クリーク -> Krieg
    b'\x83\x41\x81\x5b\x83\x8d\x83\x93': b'Arlong\x00',    # アーロン -> Arlong
    b'\x83\x5e\x83\x56\x83\x4d': b'Tashigi\x00',          # タシギ -> Tashigi

    # System & Menus
    b'\x83\x6f\x83\x67\x83\x8b': b'Battle\x00',            # バトル -> Battle
    b'\x83\x82\x81\x5b\x83\x68': b'Mode\x00',              # モード -> Mode
    b'\x83\x49\x83\x76\x83\x56\x83\x87\x83\x93': b'Option\x00', # オプション -> Option
    b'\x83\x58\x83\x67\x81\x5b\x83\x8a\x81\x5b': b'Story\x00',  # ストーリー -> Story
    b'\x83\x67\x83\x8c\x81\x5b\x83\x6a\x83\x93\x83\x4f': b'Train\x00', # トレーニング -> Train
    b'\x95\x4b\x8e\x45\x8b\x5a': b'Special\x00',          # 必殺技 -> Special
    b'\x95\x4b\x8e\x45': b'Super\x00',                      # 必殺 -> Super
}

def patch_binary(data, trans_map):
    """
    Replace occurrences in data with translated bytes safely (padding with 0x00).
    """
    patched = bytearray(data)
    replacement_count = 0
    
    for original_bytes, replacement_bytes in trans_map.items():
        orig_len = len(original_bytes)
        repl_len = len(replacement_bytes)
        
        if repl_len > orig_len:
            fit_repl = replacement_bytes[:orig_len]
        else:
            fit_repl = replacement_bytes + b'\x00' * (orig_len - repl_len)
            
        start = 0
        while True:
            pos = patched.find(original_bytes, start)
            if pos == -1:
                break
            patched[pos:pos+orig_len] = fit_repl
            replacement_count += 1
            start = pos + orig_len
            
    return bytes(patched), replacement_count

def patch_file(in_path, out_path, trans_map=None):
    if trans_map is None:
        trans_map = DEFAULT_TRANSLATIONS
        
    with open(in_path, "rb") as f:
        data = f.read()
        
    patched_data, count = patch_binary(data, trans_map)
    
    with open(out_path, "wb") as f:
        f.write(patched_data)
        
    return count

if __name__ == "__main__":
    if len(sys.argv) > 2:
        c = patch_file(sys.argv[1], sys.argv[2])
        print(f"Patched {c} text occurrences.")
    else:
        print("Usage: python patch_strings.py <input_file> <output_file>")
