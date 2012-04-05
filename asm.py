#!/usr/bin/env python3

import sys
import utils
import dasm.parse

if len(sys.argv) != 2:
    print('usage: asm.py program.asm')
    exit(1)

asm_filename = sys.argv[1]
asm_listing = open(asm_filename,'r').read()

#smurf smurf smurf
dasm.parse.parser.parse(asm_listing)

if dasm.parse.errors:
    for t in dasm.parse.errors:
        last_newline = asm_listing.rfind('\n',0,t.lexpos)
        next_newline = asm_listing.find('\n',t.lexpos)
        if last_newline < 0:
            last_newline = 0
        column = t.lexpos - last_newline
        print("Syntax error near '{}', line {}, column {}".format(t.value, t.lineno, column))
        print(asm_listing[last_newline + 1:next_newline])
        print(" " * (column - 1) + "^")
    exit(2)

labels = dasm.parse.labels
instructions = dasm.parse.statements
#print(labels)
#print(instructions)

keep_going = True
while keep_going:
    addr = 0
    keep_going = False
    for instr in instructions:
        if instr.addr != addr:
            keep_going = True
        instr.addr = addr
        addr += len(instr.assemble())

word_list = [word for instr in (instr.assemble() for instr in instructions) for word in instr]
#print(word_list)
output_hex = []
for pos,chunk in enumerate(utils.chunk(word_list,8)):
    if len(chunk) < 8:
        chunk.extend([0] * (8 - len(chunk)))
    output_hex.append('{:>4x}: '.format(pos*8) + ' '.join(('{:0>4x}'.format(x) for x in chunk)))

print('\n'.join(output_hex))
output_filename = asm_filename.rsplit('.',1)[0] 
output_file = open(output_filename + '.hex','w')
output_file.write('\n'.join(output_hex) + '\n')

#for instr in instructions:
#    print('{:>4x}: '.format(instr.addr) + ' '.join(("0x{:0>4x}".format(x) for x in instr.assemble())))
