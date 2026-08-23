#!/usr/bin/env python3
"""
One Piece Grand Battle 2 - Automated Dialogue Translator & Inserter
Translates extracted story scripts and movesets in extracted/story_dialogues.csv
and safely injects them into unpacked subfiles in extracted/apf_unpacked/
"""

import os
import sys
import csv
import struct
from pathlib import Path

# Character name and vocabulary dictionary for story / combat translation
TERM_MAP = {
    # Characters
    "ルフィ": "Luffy", "ゾロ": "Zoro", "ナミ": "Nami", "ウソップ": "Usopp", "サンジ": "Sanji",
    "チョッパー": "Chopper", "ロビン": "Robin", "エース": "Ace", "クロコダイル": "Crocodile",
    "ビビ": "Vivi", "スモーカー": "Smoker", "タシギ": "Tashigi", "バギー": "Buggy",
    "アルビダ": "Alvida", "クロー": "Kuro", "クリーク": "Krieg", "アーロン": "Arlong",
    "ミホーク": "Mihawk", "シャンクス": "Shanks", "ワポル": "Wapol", "ボン・クレー": "Bon Clay",
    "パンダマン": "Pandaman", "Mr.2": "Mr.2", "Mr.3": "Mr.3",
    
    # Combat moves & Attacks
    "必殺技": "Special Move", "必殺": "Special", "火炎星": "Fire Star", "ゴムゴム": "Gomu Gomu",
    "ピストル": "Pistol", "バズーカ": "Bazooka", "ガトリング": "Gatling", "ムチ": "Whip",
    "オニギリ": "Oni Giri", "三刀流": "Three-Sword", "虎狩り": "Tiger Hunt",
    "ディアブル": "Diable", "羊肉": "Mouton", "悪魔風脚": "Diable Jambe",
    "天候棒": "Clima-Tact", "サンダー": "Thunder", "トルネード": "Tornado",
    "ランブルボール": "Rumble Ball", "砂嵐": "Sandstorm", "砂漠の宝刀": "Desert Spada",
    "十手": "Jitte", "ホワイトアウト": "White Out", "白煙": "White Smoke",
    "バラバラ": "Chop-Chop", "キャノン": "Cannon", "スベスベ": "Smooth-Smooth",
    "杓死": "Shakushi", "大戦槍": "Great Battle Spear", "サメ肌": "Shark Skin",
    "黒刀": "Black Blade", "夜": "Yoru", "海賊王": "Pirate King",
    
    # System & Dialogue common terms
    "勝者": "Winner", "敗者": "Loser", "引き分け": "Draw", "ラウンド": "Round",
    "ファイト": "Fight", "スタート": "Start", "ゲームオーバー": "Game Over",
    "クリア": "Clear", "おめでとう": "Congrats", "次へ": "Next",
    "行くぞ": "Let's go!", "オレは": "I am ", "海賊": "Pirate", "仲間": "Crew"
}

def translate_japanese_text(jp_text):
    """Translate Japanese phrases to English using the vocabulary dictionary."""
    text = jp_text
    for jp, en in TERM_MAP.items():
        if jp in text:
            text = text.replace(jp, en)
    return text

def populate_translations(csv_in="extracted/story_dialogues.csv", csv_out="extracted/story_dialogues.csv"):
    print("Translating extracted dialogue strings...")
    rows = []
    translated_count = 0
    
    with open(csv_in, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for r in reader:
            jp = r["original_jp"]
            trans = translate_japanese_text(jp)
            if trans != jp:
                r["english_translation"] = trans
                translated_count += 1
            rows.append(r)
            
    with open(csv_out, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=["subfile", "offset", "length", "original_jp", "english_translation"])
        writer.writeheader()
        writer.writerows(rows)
        
    print(f"Populated {translated_count:,} English translations in '{csv_out}'!")
    return rows

def inject_translated_dialogues(rows, apf_dir="extracted/apf_unpacked"):
    print("\nInjecting translated dialogues into unpacked subfiles...")
    
    # Group by subfile
    by_file = {}
    for r in rows:
        fn = r["subfile"]
        if fn not in by_file:
            by_file[fn] = []
        if r.get("english_translation"):
            by_file[fn].append(r)
            
    total_injected = 0
    for fn, entries in by_file.items():
        fpath = os.path.join(apf_dir, fn)
        if not os.path.exists(fpath) or not entries:
            continue
            
        with open(fpath, "r+b") as fp:
            data = fp.read()
            patched = bytearray(data)
            
            for ent in entries:
                offset = int(ent["offset"], 16)
                orig_len = int(ent["length"])
                en_text = ent["english_translation"]
                
                # Encode in ASCII / Shift-JIS bytes
                en_bytes = en_text.encode('ascii', errors='replace')
                
                # Fit into original byte length
                if len(en_bytes) > orig_len:
                    fit_bytes = en_bytes[:orig_len]
                else:
                    fit_bytes = en_bytes + b'\x00' * (orig_len - len(en_bytes))
                    
                if offset + len(fit_bytes) <= len(patched):
                    patched[offset:offset+orig_len] = fit_bytes
                    total_injected += 1
                    
            fp.seek(0)
            fp.write(patched)
            
    print(f"Successfully injected {total_injected:,} translated dialogue lines into {len(by_file)} subfiles!")

if __name__ == "__main__":
    rows = populate_translations()
    inject_translated_dialogues(rows)
