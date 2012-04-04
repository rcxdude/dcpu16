opcodes = {
    0x0: "EXT",
    0x1: "SET",
    0x2: "ADD",
    0x3: "SUB",
    0x4: "MUL",
    0x5: "DIV",
    0x6: "MOD",
    0x7: "SHL",
    0x8: "SHR",
    0x9: "AND",
    0xa: "BOR",
    0xb: "XOR",
    0xc: "IFE",
    0xd: "IFN",
    0xe: "IFG",
    0xf: "IFB"
}

ext_opcodes = {
    0x0: "EXT",
    0x1: "JSR",
#non-standard extension
    0x14: "STOP"
}

regs = {
    0x0: "A",
    0x1: "B",
    0x2: "C",
    0x3: "X",
    0x4: "Y",
    0x5: "Z",
    0x6: "I",
    0x7: "J"
}

addrs = {
    0x18: "POP",
    0x19: "PEEK",
    0x1a: "PUSH",
    0x1b: "SP",
    0x1c: "PC",
    0x1d: "O",
}

def bidirect(map_dict):
    for key in dict(map_dict):
        map_dict[map_dict[key]] = key

bidirect(opcodes)
bidirect(ext_opcodes)
bidirect(regs)
bidirect(addrs)
