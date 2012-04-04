#!/usr/bin/env python3
import utils
import sys
import maps

if len(sys.argv) != 2:
    print("usage: disasm.py [hex file]")
    exit(1)

hexfile = open(sys.argv[1],"r")
wordlist = utils.hex_to_words(hexfile.read())

def decode_addr(addr):
    if addr < 0x8:
        return (maps.regs[addr],0)
    if addr < 0x10:
        return ('[' + maps.regs[addr - 0x8] + ']',0)
    if addr < 0x18:
        return ('[' + maps.regs[addr - 0x10] + ' + WORD]',1)
    if addr & 0x20:
        return (hex(addr & 0x1f),0)
    if addr == 0x1f or addr == 0x1e:
        return (maps.addrs[addr],1)
    else:
        return (maps.addrs[addr],0)
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
            instr = maps.ext_opcodes[(word & (0x3f) << 4) >> 4]
        else:
            instr = maps.opcodes[opcode]
            a_spec,skip = decode_addr((word & (0x3f << 4)) >> 4)
            word_skip += skip
            b_spec,skip = decode_addr((word & (0x3f << 10)) >> 10)
            word_skip += skip
        asm_line = '{0} {1}, {2}'.format(instr, a_spec, b_spec)
        asm_line_words = [word]
    if not word_skip:
        word_str = ' '.join(('0x{:0>4x}'.format(x) for x in asm_line_words))
        print('{:0>4x}: {:<30} ; {}'.format(pos,asm_line,word_str))
