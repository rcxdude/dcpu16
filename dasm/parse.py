from .lex import tokens
from . import ir

labels = {}
statements = []
macros = {}

start = 'listing'

def p_empty_listing(t):
    'listing :'

def p_listing(t):
    'listing : listing line'

def p_labeled_line(t):
    'line : LABEL statement'
    labels[t[1]] = ir.Label(t[1],t[2])

def p_line(t):
    'line : statement'

def p_statement(t):
    '''statement : instruction
                 | data'''
    statements.append(t[1])
    t[0] = t[1]

def p_data(t):
    'data : DAT data_list'
    t[0] = t[2]

def p_data_list(t):
    '''data_list : data_list COMMA data_part
                 | data_part'''
    if len(t) == 2:
        t[0] = ir.Data([t[1]])
    else:
        t[1].append(t[3])
        t[0] = t[1]

def p_data_string(t):
    'data_part : STRING'
    t[0] = ir.String(t[1])

def p_data_word(t):
    'data_part : NUMBER'
    t[0] = ir.Word(t[1])

def p_instruction(t):
    'instruction : INSTR address COMMA address'
    instr = ir.Instruction(t[1].upper(),t[2],t[4])
    t[0] = instr

def p_ext_instruction(t):
    'instruction : INSTR address'
    instr = ir.Instruction(t[1].upper(),t[2],None)
    t[0] = instr

def p_indirect_address(t):
    '''address : LBRACKET address RBRACKET'''
    t[0] = ir.Address(name = t[2].name, direct = False, offset = t[2].offset, labels = labels)

def p_literal_address(t):
    'address : offsets'
    t[0] = ir.Address(offset = t[1])

def p_name_address(t):
    'address : ADDR'
    t[0] = ir.Address(name = t[1], labels = labels)

def p_offset_address(t):
    'address : ADDR PLUS offsets'
    t[0] = ir.Address(name = t[1], offset = t[3], labels = labels)

def p_offset_address_r(t):
    'address : offsets PLUS ADDR'
    t[0] = ir.Address(name = t[3], offset = t[1], labels = labels)

def p_const_offset(t):
    '''offset : const'''
    t[0] = ir.FixedOffset(t[1])

def p_label_offset(t):
    '''offset : NAME'''
    t[0] = ir.LabelOffset(t[1], labels = labels)

def p_group_offset(t):
    '''offsets : offsets PLUS offset
               | offset'''
    if len(t) == 2:
        t[0] = ir.GroupOffset([t[1]])
    else:
        t[1].append(t[3])
        t[0] = t[1]

def p_const(t):
    '''const : NUMBER'''
    t[0] = t[1]

errors = []

def p_error(t):
    errors.append(t)

import ply.yacc
parser = ply.yacc.yacc()

