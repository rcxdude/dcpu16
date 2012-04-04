from asmlex import tokens
import asmir

labels = {}
instructions = []

start = 'listing'

def p_empty_listing(t):
    'listing :'

def p_listing(t):
    'listing : listing line'

def p_labeled_line(t):
    'line : label instruction'
    labels[t[1]] = asmir.Label(t[1],t[2])

def p_line(t):
    'line : instruction'

def p_label(t):
    'label : COLON NAME'
    t[0] = t[2]

def p_instruction(t):
    'instruction : NAME address COMMA address'
    instr = asmir.Instruction(t[1],t[2],t[4])
    instructions.append(instr)
    t[0] = instr

def p_ext_instruction(t):
    'instruction : NAME address'
    instr = asmir.Instruction(t[1],t[2],None)
    instructions.append(instr)
    t[0] = instr

def p_indirect_address(t):
    '''address : LBRACKET address RBRACKET'''
    t[0] = asmir.Address(name = t[2].name, direct = False, offset = t[2].offset, labels = labels)

def p_literal_address(t):
    'address : NUMBER'
    t[0] = asmir.Address(offset = t[1])

def p_name_address(t):
    'address : NAME'
    t[0] = asmir.Address(name = t[1], labels = labels)

def p_offset_address(t):
    'address : NAME PLUS NUMBER'
    t[0] = asmir.Address(name = t[1], offset = t[3], labels = labels)

def p_offset_address_r(t):
    'address : NUMBER PLUS NAME'
    t[0] = asmir.Address(name = t[3], offset = t[1], labels = labels)

def p_error(t):
    print("Syntax error at '{}'".format(t))

import ply.yacc
parser = ply.yacc.yacc()

