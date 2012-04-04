tokens = ('COLON','RBRACKET','LBRACKET',
           'NUMBER', 'PLUS', 'COMMA',
           'NAME', 'COMMENT')

t_COLON = r':'
t_LBRACKET = r'\['
t_RBRACKET = r'\]'
t_PLUS = r'\+'
t_COMMA = r','
t_NAME = r'[a-zA-Z_][a-zA-Z0-9_]*'

def t_COMMENT(t):
    r';.*'
    pass

def t_NUMBER(t):
    r'(0x)?\d+'
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

import ply.lex
lexer = ply.lex.lex()
