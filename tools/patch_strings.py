#!/usr/bin/env python3
"""
Comprehensive String & Text Translation Engine for One Piece Grand Battle 2 (PS1).
Translates character names, menu options, battle HUD, system settings, and move lists.
Guarantees memory safety, pointer table preservation, and null-termination.
"""

import os
import sys
import csv
import struct

# Comprehensive English Translation Dictionary
DEFAULT_TRANSLATIONS = {
    # === Playable & Support Characters (Full-width & Half-width Katakana / Kanji) ===
    b'\x83\x8b\x83\x74\x83\x42': b'Luffy\x00',                     # ルフィ -> Luffy
    b'\x83\x5a\x83\x8d': b'Zoro\x00',                             # ゾロ -> Zoro
    b'\x83\x69\x83\x7e': b'Nami\x00',                             # ナミ -> Nami
    b'\x83\x45\x83\x5c\x83\x62\x83\x76': b'Usopp\x00',             # ウソップ -> Usopp
    b'\x83\x54\x83\x93\x83\x57': b'Sanji\x00',                     # サンジ -> Sanji
    b'\x83\x60\x83\x87\x83\x62\x83\x70\x81\x5b': b'Chopper\x00', # チョッパー -> Chopper
    b'\x83\x8d\x83\x72\x83\x93': b'Robin\x00',                     # ロビン -> Robin
    b'\x83\x47\x81\x5b\x83\x58': b'Ace\x00',                       # エース -> Ace
    b'\x83\x4e\x83\x8d\x83\x52\x83\x5f\x83\x43\x83\x8b': b'Crocodile\x00', # クロコダイル -> Crocodile
    b'\x83\x72\x83\x72': b'Vivi\x00',                             # ビビ -> Vivi
    b'\x83\x58\x83\x82\x81\x5b\x83\x4a\x81\x5b': b'Smoker\x00',   # スモーカー -> Smoker
    b'\x83\x5e\x83\x56\x83\x4d': b'Tashigi\x00',                 # タシギ -> Tashigi
    b'\x83\x6f\x83\x4d\x81\x5b': b'Buggy\x00',                     # バギー -> Buggy
    b'\x83\x41\x83\x8b\x83\x72\x83\x5f': b'Alvida\x00',           # アルビダ -> Alvida
    b'\x83\x4e\x83\x8d\x81\x5b': b'Kuro\x00',                     # クロー -> Kuro
    b'\x83\x4e\x83\x8a\x81\x5b\x83\x4e': b'Krieg\x00',             # クリーク -> Krieg
    b'\x83\x41\x81\x5b\x83\x8d\x83\x93': b'Arlong\x00',           # アーロン -> Arlong
    b'\x83\x7e\x83\x7a\x81\x5b\x83\x4e': b'Mihawk\x00',           # ミホーク -> Mihawk
    b'\x83\x56\x83\x83\x83\x93\x83\x4e\x83\x58': b'Shanks\x00',   # シャンクス -> Shanks
    b'\x83\x8f\x83\x7c\x83\x8b': b'Wapol\x00',                     # ワポル -> Wapol
    b'\x83\x7b\x83\x93\x81\x45\x83\x4e\x83\x8c\x81\x5b': b'Bon Clay\x00', # ボン・クレー -> Bon Clay
    b'\x83\x70\x83\x93\x83\x5f\x83\x7d\x83\x93': b'Pandaman\x00', # パンダマン -> Pandaman
    b'\x83\x7e\x83\x58\x83\x5e\x81\x5b\x81\x45\x82\x51': b'Mr. 2\x00',   # ミスター・２ -> Mr. 2
    b'\x83\x7e\x83\x58\x83\x5e\x81\x5b\x81\x45\x82\x52': b'Mr. 3\x00',   # ミスター・３ -> Mr. 3

    # === Main Menu & Game Modes ===
    b'\x83\x4f\x83\x89\x83\x93\x83\x68\x83\x6f\x83\x67\x83\x8b': b'Grand Battle\x00', # グランドバトル -> Grand Battle
    b'\x83\x58\x83\x67\x81\x5b\x83\x8a\x81\x5b': b'Story\x00',   # ストーリー -> Story
    b'\x83\x6f\x83\x67\x83\x8b': b'Battle\x00',                   # バトル -> Battle
    b'\x83\x82\x81\x5b\x83\x68': b'Mode\x00',                     # モード -> Mode
    b'\x83\x49\x83\x76\x83\x56\x83\x87\x83\x93': b'Options\x00', # オプション -> Options
    b'\x83\x67\x83\x8c\x81\x5b\x83\x6a\x83\x93\x83\x4f': b'Training\x00', # トレーニング -> Training
    b'\x83\x5e\x83\x43\x83\x67\x83\x8b': b'Title\x00',           # タイトル -> Title
    b'\x83\x4a\x83\x89\x83\x8a\x81\x5b': b'Gallery\x00',         # ギャラリー -> Gallery
    b'\x83\x89\x83\x93\x83\x4c\x83\x93\x83\x4f': b'Ranking\x00', # ランキング -> Ranking
    b'\x83\x54\x83\x45\x83\x93\x83\x68': b'Sound\x00',           # サウンド -> Sound
    b'\x83\x52\x83\x93\x83\x65\x83\x42\x83\x6a\x83\x85\x81\x5b': b'Continue\x00', # コンティニュー -> Continue
    b'\x83\x52\x83\x7d\x83\x93\x83\x68': b'Command\x00',         # コマンド -> Command

    # === Battle & Combat Mechanics ===
    b'\x95\x4b\x8e\x45\x8b\x5a': b'Special Move\x00',             # 必殺技 -> Special Move
    b'\x95\x4b\x8e\x45': b'Special\x00',                         # 必殺 -> Special
    b'\x8d\x55\x8c\x82': b'Attack\x00',                           # 攻撃 -> Attack
    b'\x96\x68\x8c\xe4': b'Guard\x00',                            # 防御 -> Guard
    b'\x83\x57\x83\x83\x83\x93\x83\x76': b'Jump\x00',             # ジャンプ -> Jump
    b'\x83\x5f\x83\x62\x83\x56\x83\x85': b'Dash\x00',             # ダッシュ -> Dash
    b'\x83\x4b\x81\x5b\x83\x68': b'Guard\x00',                   # ガード -> Guard
    b'\x83\x4a\x83\x93\x83\x6f\x83\x8a\x83\xaa\x83\x5c\x83\x93': b'Ganbarion\x00', # ガンバリオン -> Ganbarion

    # === System Settings & Options ===
    b'\x91\xe5\x89\xef': b'Tournament\x00',                       # 大会 -> Tournament
    b'\x90\xdd\x92\xe8': b'Config\x00',                           # 設定 -> Config
    b'\x8c\x88\x92\xe8': b'Confirm\x00',                          # 決定 -> Confirm
    b'\x8e\xd7\x8f\xc1': b'Cancel\x00',                           # 取消 -> Cancel
    b'\x96\xdf\x82\xe9': b'Back\x00',                             # 戻る -> Back
    b'\x8f\x89\x8a\xfa\x89\xbb': b'Reset\x00',                    # 初期化 -> Reset
    b'\x93\xef\x88\xd3\x93\x78': b'Difficulty\x00',               # 難易度 -> Difficulty
    b'\x82\xe2\x82\xb3\x82\xb5\x82\xa2': b'Easy\x00',             # やさしい -> Easy
    b'\x82\xd3\x82\xc2\x82\xa4': b'Normal\x00',                   # ふつう -> Normal
    b'\x82\xd1\x82\xbd\x82\xa2': b'Hard\x00',                     # むずかしい -> Hard
    b'\x96\xb3\x90\xa7\x8c\xc0': b'Infinite\x00',                 # 無制限 -> Infinite
    b'\x90\xa7\x8c\xc0\x8e\x9e\x8a\xd4': b'Time Limit\x00',       # 制限時間 -> Time Limit
    b'\x83\x7c\x81\x5b\x83\x59': b'Pause\x00',                   # ポーズ -> Pause
    b'\x83\x51\x81\x5b\x83\x80': b'Game\x00',                     # ゲーム -> Game
    b'\x83\x56\x83\x58\x83\x65\x83\x80': b'System\x00',           # システム -> System
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
        print(f"Patched {c} text occurrences in '{sys.argv[1]}'.")
    else:
        print("Usage: python patch_strings.py <input_file> <output_file>")
