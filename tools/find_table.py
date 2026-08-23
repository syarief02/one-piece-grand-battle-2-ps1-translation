with open("extracted/OP.APF", "rb") as f:
    data = f.read(1024 * 1024)

# Find first non-zero byte after offset 0x20
idx = 0x20
while idx < len(data) and data[idx] == 0:
    idx += 1

print(f"First non-zero byte at offset: 0x{idx:08X} ({idx})")

# Print 256 bytes starting from idx
for i in range(idx, min(idx + 256, len(data)), 16):
    line = data[i:i+16]
    hex_str = " ".join(f"{b:02X}" for b in line)
    asc_str = "".join(chr(b) if 32 <= b <= 126 else "." for b in line)
    print(f"{i:06X}: {hex_str:<48} | {asc_str}")
