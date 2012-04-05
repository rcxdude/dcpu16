#include <assert.h>
#include <stdio.h>
#include <string.h>
#include "dcpu.h"

void init_cpu_state(struct cpu_state *state) {
    memset(state, 0, sizeof(struct cpu_state));
    state->SP = MEM_SIZE - 1;
}

static uint16_t *reg(struct cpu_state *s, uint8_t addr) {
    switch(addr) {
        case 0x0:
            return &(s->A);
        case 0x1:
            return &(s->B);
        case 0x2:
            return &(s->C);
        case 0x3:
            return &(s->X);
        case 0x4:
            return &(s->Y);
        case 0x5:
            return &(s->Z);
        case 0x6:
            return &(s->I);
        case 0x7:
            return &(s->J);
        default:
            printf("%x\n",addr);
            assert(0);
    }
}

#define N_ADDRS 2
static uint16_t lit_pos;
static uint16_t lit[N_ADDRS];

static uint16_t *lookup(struct cpu_state *s, uint8_t addr) {
    assert(addr < 0x40);
    if (addr < 0x8) {
        return reg(s, addr);
    }
    if (addr < 0x10) {
        return s->mem + *reg(s, addr - 0x8);
    }
    if (addr < 0x18) {
        s->cycles++;
        return s->mem + *reg(s, addr - 0x10) + s->mem[s->PC++];
    }
    switch(addr) {
        case 0x18: //POP
            return s->mem + s->SP++;
        case 0x19: //PEEK
            return s->mem + s->SP;
        case 0x1a: //PUSH
            return s->mem + --s->SP;
        case 0x1b:
            return &(s->SP);
        case 0x1c:
            return &(s->PC);
        case 0x1d:
            return &(s->O);
        case 0x1e:
            s->cycles++;
            return s->mem + s->mem[s->PC++];
        case 0x1f:
            s->cycles++;
            return s->mem + s->PC++;
        default:
            //hacky, but prevents redefining literals
            lit_pos = (lit_pos + 1) % N_ADDRS;
            lit[lit_pos] = addr & 0x1f;
            return lit + lit_pos;
    }
}

static void decode(struct cpu_state *s, uint8_t addr) {
    assert(addr < 0x40);
    if (addr >= 0x10 && addr < 0x18 || addr == 0x1e || addr == 0x1f) {
        //does this cost cycles?
        s->PC++;
    }
}

void print_mem(struct cpu_state *s, uint16_t start, uint16_t end) {
    uint32_t pos;
    for (pos = start; pos < end; pos += 8) {
        int ii;
        uint8_t print_line = 0;
        for (ii = 0; ii < 8; ii++) {
            if (s->mem[pos + ii] != 0) {
                print_line = 1;
                break;
            }
        }
        if (!print_line) {
            continue;
        }
        printf("%4x:",pos);
        for (ii = 0; ii < 8; ii++) {
            printf(" %04x", s->mem[pos + ii]);
        }
        printf("\n");
    }
}

void print_regs(struct cpu_state *s) {
    printf("A: %4x B: %4x C: %4x X: %4x Y: %4x Z: %4x I: %4x J: %4x\n",
           s->A, s->B, s->C, s->X, s->Y, s->Z, s->I, s->J);
    printf("PC: %4x SP: %4x O: %4x\n", s->PC, s->SP, s->O);
}

static void trace(struct cpu_state *s, char *instr, uint16_t a_addr, uint16_t *a, uint16_t b_addr, uint16_t *b) {
    printf("INSTR: %s a: %4x(%4x) b: %4x(%4x)\n", instr, a_addr, *a, b_addr, b?*b:0);
    printf("STATE: cycles: %lu, PC + 1: %4x, PC + 2: %4x\n", s->cycles, s->mem[s->PC + 1], s->mem[s->PC + 2]);
}

#ifdef ENABLE_TRACE
#define TRACE(x) trace(s, (x), a_addr, a, b_addr, b) 
#else
#define TRACE(x)
#endif

void step_cpu(struct cpu_state *s) {
    uint16_t instr;
    instr = s->mem[s->PC++];
    s->cycles++;
    uint8_t opcode = instr & 0xf;
    uint8_t a_addr = (instr >> 4) & 0x3f;
    uint8_t b_addr = (instr >> 10) & 0x3f;
    uint16_t *a = 0,*b = 0;
    if (opcode == 0) {
        opcode = a_addr | 0x80;
        if (s->skip) {
            decode(s,b_addr);
        } else {
            a = lookup(s,b_addr);
        }
    } else {
        if (s->skip) {
            decode(s,a_addr);
            decode(s,b_addr);
        } else {
            a = lookup(s,a_addr);
            b = lookup(s,b_addr);
        }
    }
    if (s->skip) {
        s->skip = 0;
        return;
    }
    uint32_t res = 0;
    switch(opcode) {
        case 0x1: TRACE("SET");
            *a = *b;
            break;
        case 0x2: TRACE("ADD");
            res = *a + *b;
            *a = res & 0xffff;
            s->O = (res >> 16) & 0xffff;
            s->cycles++;
            break;
        case 0x3: TRACE("SUB");
            res = *a - *b;
            *a = res & 0xffff;
            s->O = (res >> 16) & 0xffff;
            s->cycles++;
            break;
        case 0x4: TRACE("MUL");
            res = *a * *b;
            *a = res & 0xffff;
            s->O = (res >> 16) & 0xffff;
            s->cycles += 2;
            break;
        case 0x5: TRACE("DIV");
            res = ((uint32_t)*a << 16) / *b;
            s->O = res & 0xffff;
            *a = (res >> 16) & 0xffff;
            s->cycles += 2;
            break;
        case 0x6: TRACE("MOD");
            if (*b == 0) {
                *a = 0;
            } else {
                *a = *a % *b;
            }
            break;
        case 0x7: TRACE("SHL");
            res = *a << *b;
            *a = res & 0xffff;
            s->O = (res >> 16) & 0xffff;
            s->cycles++;
            break;
        case 0x8: TRACE("SHR");
            res = ((uint32_t)*a << 16) >> *b;
            s->O = res & 0xffff;
            *a = (res >> 16) & 0xffff;
            s->cycles++;
            break;
        case 0x9: TRACE("AND");
            *a = *a & *b;
            break;
        case 0xa: TRACE("BOR");
            *a = *a | *b;
            break;
        case 0xb: TRACE("XOR");
            *a = *a ^ *b;
            break;
        case 0xc: TRACE("IFE");
            if (*a != *b) {
                s->skip = 1;
            }
            s->cycles++;
            break;
        case 0xd: TRACE("IFN");
            if (*a == *b) {
                s->skip = 1;
            }
            s->cycles++;
            break;
        case 0xe: TRACE("IFG");
            if (*a <= *b) {
                s->skip = 1;
            }
            s->cycles++;
            break;
        case 0xf: TRACE("IFL");
            if (*a >= *b) {
                s->skip = 1;
            }
            s->cycles++;
            break;
        case 0x80 | 0x1: TRACE("JSR");
            s->mem[--s->SP] = s->PC;
            s->PC = *a;
            s->cycles++;
            break;
        case 0x80 | 0x14: TRACE("STOP");
            s->stopped = 1;
            break;
        default:
            assert(0);
    }
}


void run_forever(struct cpu_state *s) {
    while(!s->stopped) {
#ifdef ENABLE_TRACE
        printf("----\n");
        print_regs(s);
#endif
        step_cpu(s);
    }
}

void read_mem_file(struct cpu_state *s, FILE *ifile) {
    int pos, val;
    while (fscanf(ifile,"%x:",&pos) != EOF) {
        int ii;
        for (ii = 0; ii < 8; ii++) {
            fscanf(ifile, " %x",&val);
            s->mem[pos + ii] = val;
        }
    }
}

