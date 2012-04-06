from . import instrs
tokens = (
'RBRACKET',
'LBRACKET',
'MACRO',
'NUMBER',
'EQUALS',
'PLUS',
'MINUS',
'COMMA',
'COMMENT',
'STRING',
'NAME',
'DAT',
'INSTR',
'ADDR',
'LABEL'
)

import ply.lex
def Lexer(syntax_only = False):
    t_LBRACKET = r'\['
    t_RBRACKET = r'\]'
    t_PLUS = r'\+'
    t_MINUS = r'-'
    t_EQUALS = r'='
    t_MACRO = r'\$[a-zA-Z_][a-zA-Z0-9_]*'
    t_COMMA = r','

    def t_STRING(t):
        r'"(\\"|[^"])*"'
        if syntax_only:
            return t
        t.value = t.value[1:-1]
        return t

    def t_LABEL(t):
        r':[a-zA-Z_][a-zA-Z0-9_]*'
        if syntax_only:
            return t
        t.value = t.value[1:]
        return t

    def t_NAME(t):
        r'[a-zA-Z_][a-zA-Z0-9_]*'
        value = t.value.upper()
        if value in instrs.opcodes or \
           value in instrs.ext_opcodes:
            t.type = 'INSTR'
            t.value = value
        elif value in instrs.regs or \
           value in instrs.addrs:
            t.type = 'ADDR'
            t.value = value
        elif value == 'DAT':
            t.type = 'DAT'
            t.value = value
        return t

    def t_COMMENT(t):
        r';.*'
        if syntax_only:
            return t

    def t_NUMBER(t):
        r'(0x)?[0-9a-fA-F]+'
        if syntax_only:
            return t
        if t.value.startswith('0x'):
            t.value = int(t.value,16)
        elif t.value.startswith('0'):
            t.value = int(t.value,8)
        else:
            t.value = int(t.value)
        return t

    t_ignore = " \t"

    def t_newline(t):
        r'\n+'
        t.lexer.lineno += t.value.count("\n")

    def t_error(t):
        print("Unexpected character {}".format(t.value[0]))
        t.lexer.skip(1)

    return ply.lex.lex()
