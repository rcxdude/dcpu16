import maps
class UnknownInstruction(Exception):
    def __init__(self,instruction):
        self.instruction = instruction

    def __repr__(self):
        return "Unknown instruction {}".format(self.instruction)

class Instruction:
    def __init__(self, instr, a_addr, b_addr):
        self.instr = instr
        self.a_addr = a_addr
        self.b_addr = b_addr
        self.addr = -1

    def __repr__(self):
        return 'Instruction({}, {}, {})'.format(self.instr, self.a_addr, self.b_addr)

    def assemble(self):
        words = []
        if self.instr in maps.opcodes:
            a_addr,a_word = self.a_addr.assemble()
            b_addr,b_word = self.b_addr.assemble()
            asm_instr = maps.opcodes[self.instr] | \
                   (a_addr << 4) | \
                   (b_addr << 10)
        elif self.instr in maps.ext_opcodes:
            b_word = None
            a_addr,a_word = self.a_addr.assemble()
            asm_instr = maps.opcodes['EXT'] | \
                    (maps.ext_opcodes[self.instr] << 4) | \
                    (a_addr << 10)
        else:
            raise UnknownInstruction(self.instr)

        words.append(asm_instr)
        if a_word is not None:
            words.append(a_word)
        if b_word is not None:
            words.append(b_word)
        return words

class UnknownLabel(Exception):
    def __init__(self, label):
        self.label = label

    def __rept__(self):
        return 'Unknown label {}'.format(self.label)

class Address:
    def __init__(self, name = None, direct=True, offset=0, labels = None):
        self.name = name
        self.direct = direct
        self.offset = offset
        if labels is None:
            self.labels = {}
        else:
            self.labels = labels

    def __repr__(self):
        return 'Address({}, {}, {})'.format(self.name, self.direct, self.offset)
    
    def assemble(self):
        if self.direct:
            if self.name is None:
                if (self.offset < 0x20):
                    return (self.offset | 0x20,None)
                else:
                    return (0x1f,self.offset)
                return self.offset
            if self.name in maps.regs:
                return (maps.regs[self.name],None)
            elif self.name in maps.addrs:
                return (maps.addrs[self.name],None)
            elif self.name in self.labels:
                addr = self.labels[self.name].instr.addr
                if addr < 0x20:
                    return (addr | 0x20, None)
                else:
                    return (0x1f,addr)
            else:
                raise UnknownLabel(self.name)
        else:
            if self.name is None:
                return (0x1e, self.offset)
            elif self.offset == 0:
                return (maps.regs[self.name] + 0x8, None)
            else:
                return (maps.regs[self.name] + 0x10, self.offset)


class Label:
    def __init__(self, name, instr, addr = None):
        self.name = name
        self.instr = instr

    def __repr__(self):
        return 'Label({}, {})'.format(self.name, self.instr)

