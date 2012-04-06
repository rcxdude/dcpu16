#!/usr/bin/env python3

import sys
import utils
import dasm.assembler

if len(sys.argv) != 2:
    print('usage: asm.py program.asm')
    exit(1)

asm_filename = sys.argv[1]
asm_listing = open(asm_filename,'r').read()

word_list, statements = dasm.assembler.assemble_listing(asm_listing)

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
