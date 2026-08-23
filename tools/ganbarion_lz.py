#!/usr/bin/env python3
"""
Fast, optimized Ganbarion LZSS decompressor for PS1.
"""

import struct

def decompress_ganbarion_lz(data):
    if len(data) < 8:
        return data
        
    decomp_size = struct.unpack_from('<I', data, 0)[0]
    if decomp_size > 20 * 1024 * 1024 or decomp_size < 16:
        return data
        
    out = bytearray(decomp_size)
    out_pos = 0
    src_pos = 4
    data_len = len(data)
    
    while out_pos < decomp_size and src_pos < data_len:
        flags = data[src_pos]
        src_pos += 1
        
        for bit in range(8):
            if out_pos >= decomp_size or src_pos >= data_len:
                break
                
            if (flags & (1 << bit)) != 0:
                out[out_pos] = data[src_pos]
                out_pos += 1
                src_pos += 1
            else:
                if src_pos + 1 >= data_len:
                    break
                b1 = data[src_pos]
                b2 = data[src_pos + 1]
                src_pos += 2
                
                offset = ((b2 & 0xF0) << 4) | b1
                length = (b2 & 0x0F) + 3
                
                match_start = out_pos - offset - 1
                for i in range(length):
                    if out_pos >= decomp_size:
                        break
                    p = match_start + i
                    if 0 <= p < out_pos:
                        out[out_pos] = out[p]
                    else:
                        out[out_pos] = 0
                    out_pos += 1
                    
    return bytes(out[:out_pos])
