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
labels = dasm.parse.labels
instructions = dasm.parse.instructions
#print(labels)
#print(instructions)
last_addr = -1
addr = 0

while last_addr != addr:
    last_addr = addr
    addr = 0
    for instr in instructions:
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
#    print(' '.join(("0x{:0>4x}".format(x) for x in instr.assemble())))
