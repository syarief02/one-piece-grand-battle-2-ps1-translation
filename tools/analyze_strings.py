import csv
import sys

with open('extracted/exe_strings.csv', 'r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    rows = [r for r in reader]

# Look for actual meaningful Japanese text - filter out short gibberish
jp = [r for r in rows if r['category'] == 'JAPANESE_TEXT']
meaningful_jp = [r for r in jp if len(r['original']) >= 4 and not all(
    c in 'ﾞﾟｯｰ<>!@#$%^&*()=+[]{}|;:,./\\\'\"0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz '
    for c in r['original']
)]

print(f'Total Japanese strings: {len(jp)}')
print(f'Meaningful Japanese strings (4+ chars): {len(meaningful_jp)}')
print()

# Show strings from the later part of the executable (more likely to be game text)
print('=== Japanese strings from offset > 0x20000 (likely game data area) ===')
late_jp = [r for r in meaningful_jp if int(r['offset'], 16) > 0x20000]
print(f'Count: {len(late_jp)}')
for r in late_jp[:100]:
    print(f"  {r['offset']}: [{len(r['original'])} chars] {r['original'][:100]}")

print()
print('=== ALL OTHER strings from offset > 0x20000 ===')
late_other = [r for r in rows if r['category'] in ('OTHER', 'MENU', 'GAMEPLAY') and int(r['offset'], 16) > 0x20000]
print(f'Count: {len(late_other)}')
for r in late_other[:100]:
    print(f"  {r['offset']}: {r['original'][:100]}")

# Also look for One Piece character names in the binary
print()
print('=== Searching for known character names (Shift-JIS) ===')
with open('extracted/SLPS_034.08', 'rb') as f:
    exe_data = f.read()

# Common One Piece character names in Shift-JIS
names_to_find = {
    'ルフィ': b'\x83\x8b\x83\x74\x83\x42',        # Luffy
    'ゾロ': b'\x83\x5a\x83\x8d',                    # Zoro
    'ナミ': b'\x83\x69\x83\x7e',                    # Nami
    'ウソップ': b'\x83\x45\x83\x5c\x83\x62\x83\x76', # Usopp
    'サンジ': b'\x83\x54\x83\x93\x83\x57',          # Sanji
    'チョッパー': b'\x83\x60\x83\x87\x83\x62\x83\x70\x81\x5b', # Chopper
}

for name, sjis_bytes in names_to_find.items():
    offsets = []
    start = 0
    while True:
        pos = exe_data.find(sjis_bytes, start)
        if pos == -1:
            break
        offsets.append(f'0x{pos:08X}')
        start = pos + 1
    if offsets:
        print(f"  {name}: Found at {', '.join(offsets[:10])}")
    else:
        print(f"  {name}: NOT FOUND in executable")
