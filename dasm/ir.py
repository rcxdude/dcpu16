from . import instrs
class UnknownInstruction(Exception):
    def __init__(self,instruction):
        self.instruction = instruction

    def __str__(self):
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
        if self.instr in instrs.opcodes:
            a_addr,a_word = self.a_addr.assemble()
            b_addr,b_word = self.b_addr.assemble()
            asm_instr = instrs.opcodes[self.instr] | \
                   (a_addr << 4) | \
                   (b_addr << 10)
        elif self.instr in instrs.ext_opcodes:
            b_word = None
            a_addr,a_word = self.a_addr.assemble()
            asm_instr = instrs.opcodes['EXT'] | \
                    (instrs.ext_opcodes[self.instr] << 4) | \
                    (a_addr << 10)
        else:
            raise UnknownInstruction(self.instr)

        words.append(asm_instr)
        if a_word is not None:
            words.append(a_word)
        if b_word is not None:
            words.append(b_word)
        return words

class Address:
    def __init__(self, name = None, direct=True, offset=None, labels = None):
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
                if (self.offset.addr() < 0x20):
                    return (self.offset.addr() | 0x20,None)
                else:
                    return (0x1f,self.offset.addr())
            if self.name in instrs.regs:
                return (instrs.regs[self.name],None)
            elif self.name in instrs.addrs:
                return (instrs.addrs[self.name],None)
        else:
            if self.name is None:
                return (0x1e, self.offset.addr())
            elif self.offset is None or self.offset.addr() == 0:
                return (instrs.regs[self.name] + 0x8, None)
            else:
                return (instrs.regs[self.name] + 0x10, self.offset.addr())

class Word:
    def __init__(self, word):
        self.word = word

    def assemble(self):
        return [self.word]

class String:
    def __init__(self, string):
        self.string = string

    def assemble(self):
        words = bytes(self.string, encoding='ascii')
        return [int(w) for w in words]

class Data(list):
    def __init__(self, *args, **kargs):
        super().__init__(*args, **kargs)
        self.addr = -1

    def assemble(self):
        ret = []
        for d in self:
            ret.extend(d.assemble())
        return ret

class Label:
    def __init__(self, name, instr, addr = None):
        self.name = name
        self.instr = instr

    def addr(self):
        return self.instr.addr

    def __repr__(self):
        return 'Label({}, {})'.format(self.name, self.instr)

class UnknownLabel(Exception):
    def __init__(self, label):
        self.label = label

    def __str__(self):
        return 'Unknown label {}'.format(self.label)

class LabelOffset:
    def __init__(self, name, labels = None):
        self.name = name
        if labels is None:
            self.labels = {}
        else:
            self.labels = labels

    def addr(self):
        if self.name not in self.labels:
            raise UnknownLabel(self.name)
        return self.labels[self.name].addr()

    def __repr__(self):
        return 'LabelOffset({})'.format(self.name)

class FixedOffset:
    def __init__(self, addr):
        self._addr = addr

    def addr(self):
        return self._addr

    def __repr__(self):
        return 'FixedOffset({})'.format(self.addr())

class GroupOffset(list):
    def __init__(self, *args, **kargs):
        super().__init__(*args, **kargs)

    def addr(self):
        return sum((x.addr() for x in self))
