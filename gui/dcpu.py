from ctypes import *

MEM_SIZE = 0x10000

class CpuStruct(Structure):
    _fields_ = [("mem", c_uint16 * MEM_SIZE)] + \
               [(x, c_uint16) for x in ("A","B","C","X","Y","Z","I","J","PC","SP","O")] + \
               [("skip", c_uint8),
                ("cycles", c_ulong),
                ("stopped", c_int),
                ("breakpoints", c_uint8 * MEM_SIZE),
                ("breakpoint", c_int)]

lib = cdll.LoadLibrary("./build/libdcpu-emu.so")

class MemBoundError(Exception):
    def __init__(self, address):
        self.address = address

    def __str__(self):
        return 'Attempted to access memory at address {}'.format(self.address)

class DCPU:
    def __init__(self):
        self.struct = CpuStruct()
        self.watchpoints = set()
        self.breakpoints = set()
        lib.init_cpu(byref(self.struct))

    def run_forever(self):
        lib.run_forever(byref(self.struct))

    def run_to_breakpoint(self):
        lib.run_to_breakpoint(byref(self.struct))

    def step(self, n_steps = 1):
        lib.run_steps(byref(self.struct), c_ulong(n_steps))

    def load_from_hex(self, mem, offset = 0):
        if len(mem) + offset > MEM_SIZE:
            raise MemBoundError(len(mem) + offset)
        for addr, word in enumerate(mem):
            self.struct.mem[offset + addr] = word

    def add_breakpoint(self,breakpoint):
        lib.add_breakpoint(byref(self.struct), breakpoint)

    def del_breakpoint(self,breakpoint):
        lib.del_breakpoint(byref(self.struct), breakpoint)

    def add_watchpoint(self,watchpoint):
        lib.add_watchpoint(byref(self.struct), watchpoint)

    def del_watchpoint(self,watchpoint):
        lib.del_watchpoint(byref(self.struct), watchpoint)

    def get_nonzero_chunks(self):
        last = c_uint16(0)
        start = c_uint16(0)
        end = c_uint16(0)
        chunks = []
        while True:
            lib.get_next_nonzero_chunk(byref(self.struct), last,
                                       byref(start), byref(end))
            if start.value == c_uint16(-1).value:
                break
            chunks.append((start.value,end.value))
            last.value = end.value
        return chunks



if __name__ == "__main__":
    import sys
    import utils
    ifile = open(sys.argv[1],"r")
    mem = utils.hex_to_words(ifile.read())
    cpu = DCPU()
    cpu.load_from_hex(mem)
    cpu.run_forever()
