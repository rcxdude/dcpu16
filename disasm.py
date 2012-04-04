#!/usr/bin/env python3
import utils
import sys

if len(sys.argv) != 2:
    print("usage: disasm.py [hex file]")
    exit(1)

hexfile = open(sys.argv[1],"r")
wordlist = utils.hex_to_words(hexfile.read())

opcodes = {
    0x0: "EXT",
    0x1: "SET",
    0x2: "ADD",
    0x3: "SUB",
    0x4: "MUL",
    0x5: "DIV",
    0x6: "MOD",
    0x7: "SHL",
    0x8: "SHR",
    0x9: "AND",
    0xa: "BOR",
    0xb: "XOR",
    0xc: "IFE",
    0xd: "IFN",
    0xe: "IFG",
    0xf: "IFB"
}

ext_opcodes = {
    0x0: "NULL",
    0x1: "JSR"
}

regs = {
    0x0: "A",
    0x1: "B",
    0x2: "C",
    0x3: "X",
    0x4: "Y",
    0x5: "Z",
    0x6: "I",
    0x7: "J"
}

addr_map = {
    0x18: "POP",
    0x19: "PEEK",
    0x1a: "PUSH",
    0x1b: "SP",
    0x1c: "PC",
    0x1d: "O",
    0x1e: "[WORD]",
    0x1f: "WORD"
}

def decode_addr(addr):
    if addr < 0x8:
        return (regs[addr],0)
    if addr < 0x10:
        return ('[' + regs[addr - 0x8] + ']',0)
    if addr < 0x18:
        return ('[' + regs[addr - 0x10] + ' + WORD]',1)
    if addr & 0x20:
        return (hex(addr & 0x1f),0)
    if addr == 0x1f or addr == 0x1e:
        return (addr_map[addr],1)
    else:
        return (addr_map[addr],0)
    return ("UNKNOWN",0)

word_skip = 0
asm_line = ''
asm_line_words = []
for pos,word in enumerate(wordlist):
    if word_skip:
        word_skip -= 1
        asm_line = asm_line.replace('WORD',"{:#x}".format(word),1)
        asm_line_words.append(word)
    else:
        opcode = word & 0xf
        if opcode == 0:
            a_spec,skip = decode_addr((word & (0x3f << 10)) >> 10)
            word_skip += skip
            b_spec = ''
            instr = ext_opcodes[(word & (0x3f) << 4) >> 4]
            pass
        else:
            instr = opcodes[opcode]
            a_spec,skip = decode_addr((word & (0x3f << 4)) >> 4)
            word_skip += skip
            b_spec,skip = decode_addr((word & (0x3f << 10)) >> 10)
            word_skip += skip
        asm_line = '{0} {1}, {2}'.format(instr, a_spec, b_spec)
        asm_line_words = [word]
    if not word_skip:
        word_str = ' '.join(('0x{:0>4x}'.format(x) for x in asm_line_words))
        print('{:0>4x}: {:<30} ; {}'.format(pos,asm_line,word_str))
