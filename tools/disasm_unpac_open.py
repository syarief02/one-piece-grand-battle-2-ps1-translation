#!/usr/bin/env python3
"""
Disassemble UNPAC_Open implementation at 0x023400 in SLPS_034.08.
"""

import struct

MIPS_OPS = {
    0: "SPECIAL", 1: "REGIMM", 2: "j", 3: "jal", 4: "beq", 5: "bne", 6: "blez", 7: "bgtz",
    8: "addi", 9: "addiu", 10: "slti", 11: "sltiu", 12: "andi", 13: "ori", 14: "xori", 15: "lui",
    32: "lb", 33: "lh", 34: "lwl", 35: "lw", 36: "lbu", 37: "lhu", 38: "lwr", 40: "sb",
    41: "sh", 42: "swl", 43: "sw", 46: "swr"
}

MIPS_SPECIAL = {
    0: "sll", 2: "srl", 3: "sra", 4: "sllv", 6: "srlv", 7: "srav", 8: "jr", 9: "jalr",
    12: "syscall", 13: "break", 32: "add", 33: "addu", 34: "sub", 35: "subu", 36: "and",
    37: "or", 38: "xor", 39: "nor", 42: "slt", 43: "sltu"
}

REGS = ["zero", "at", "v0", "v1", "a0", "a1", "a2", "a3", "t0", "t1", "t2", "t3", "t4", "t5", "t6", "t7",
        "s0", "s1", "s2", "s3", "s4", "s5", "s6", "s7", "t8", "t9", "k0", "k1", "gp", "sp", "fp", "ra"]

def disasm_mips(instr, addr):
    op = (instr >> 26) & 0x3F
    rs = (instr >> 21) & 0x1F
    rt = (instr >> 16) & 0x1F
    rd = (instr >> 11) & 0x1F
    shamt = (instr >> 6) & 0x1F
    funct = instr & 0x3F
    imm = instr & 0xFFFF
    simm = imm if imm < 0x8000 else imm - 0x10000
    target = (instr & 0x3FFFFFF) << 2
    
    if op == 0:
        name = MIPS_SPECIAL.get(funct, f"spec_{funct}")
        if funct == 8: # jr
            return f"jr ${REGS[rs]}"
        elif funct == 0 and instr == 0:
            return "nop"
        elif funct in (0, 2, 3): # sll, srl, sra
            return f"{name} ${REGS[rd]}, ${REGS[rt]}, {shamt}"
        else:
            return f"{name} ${REGS[rd]}, ${REGS[rs]}, ${REGS[rt]}"
    elif op in (2, 3):
        name = "jal" if op == 3 else "j"
        return f"{name} 0x{(addr & 0xF0000000) | target:08X}"
    elif op in (4, 5):
        name = "beq" if op == 4 else "bne"
        b_target = addr + 4 + (simm << 2)
        return f"{name} ${REGS[rs]}, ${REGS[rt]}, 0x{b_target:08X}"
    elif op == 15: # lui
        return f"lui ${REGS[rt]}, 0x{imm:04X}"
    elif op in (8, 9, 10, 11, 12, 13, 14):
        name = MIPS_OPS.get(op, f"op_{op}")
        return f"{name} ${REGS[rt]}, ${REGS[rs]}, 0x{imm:04X} ({simm})"
    elif op in (32, 33, 34, 35, 36, 37, 38, 40, 41, 42, 43, 46):
        name = MIPS_OPS.get(op, f"op_{op}")
        return f"{name} ${REGS[rt]}, {simm}(${REGS[rs]})"
    else:
        return f"unk_{op} 0x{instr:08X}"

with open("extracted/SLPS_034.08", "rb") as f:
    f.seek(0x023400)
    data = f.read(0x180)

print("=== UNPAC_Open MIPS Disassembly ===")
for i in range(0, len(data), 4):
    instr = struct.unpack_from('<I', data, i)[0]
    addr = 0x80010000 + 0x023400 + i - 0x800
    mnemonic = disasm_mips(instr, addr)
    print(f"0x{addr:08X} (0x{0x023400+i:06X}): {instr:08X}   {mnemonic}")
