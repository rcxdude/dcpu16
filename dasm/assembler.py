from . import parse

class AsmSyntaxErrors(Exception):
    def __init__(self, errors, asm_listing):
        self.errors = []
        for t in errors:
            last_newline = asm_listing.rfind('\n',0,t.lexpos)
            next_newline = asm_listing.find('\n',t.lexpos)
            if last_newline < 0:
                last_newline = 0
            column = t.lexpos - last_newline
            self.errors.append("Syntax error near '{}', line {}, column {}".format(t.value, t.lineno, column))
            self.errors.append(asm_listing[last_newline + 1:next_newline])
            self.errors.append(" " * (column - 1) + "^")

    def __str__(self):
        return '\n'.join(self.errors)

def assemble_listing(listing):
    #smurf smurf smurf
    parse.parser.parse(listing)

    if parse.errors:
        raise AsmSyntaxErrors(parse.errors, listing)

    labels = parse.labels
    statements = parse.statements
    #print(labels)
    #print(statements)

    keep_going = True
    while keep_going:
        addr = 0
        keep_going = False
        for instr in statements:
            if instr.addr != addr:
                keep_going = True
            instr.addr = addr
            addr += len(instr.assemble())

    word_list = [word for instr in (instr.assemble() for instr in statements) for word in instr]
    parse.labels = {}
    parse.statements = []
    parse.errors = []
    return word_list, statements
