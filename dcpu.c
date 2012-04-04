#include <stdint.h>
#include <assert.h>
#include <stdio.h>

#define MEM_SIZE 0x10000
#define ENABLE_TRACE
static uint16_t mem[MEM_SIZE];
static uint16_t A,B,C,X,Y,Z,I,J,PC,SP = MEM_SIZE - 1,O;

static uint16_t *reg(uint8_t addr) {
    switch(addr) {
        case 0x0:
            return &A;
        case 0x1:
            return &B;
        case 0x2:
            return &C;
        case 0x3:
            return &X;
        case 0x4:
            return &Y;
        case 0x5:
            return &Z;
        case 0x6:
            return &I;
        case 0x7:
            return &J;
        default:
            printf("%x\n",addr);
            assert(0);
    }
}

#define N_ADDRS 2
uint16_t lit_pos;
uint16_t lit[N_ADDRS];

static uint16_t *lookup(uint8_t addr) {
    assert(addr < 0x40);
    if (addr < 0x8) {
        return reg(addr);
    }
    if (addr < 0x10) {
        return mem + *reg(addr - 0x8);
    }
    if (addr < 0x18) {
        return mem + *reg(addr - 0xf) + mem[PC++];
    }
    switch(addr) {
        case 0x18:
            return mem + SP++;
        case 0x19:
            return mem + SP;
        case 0x1a:
            return mem + --SP;
        case 0x1b:
            return &SP;
        case 0x1c:
            return &PC;
        case 0x1d:
            return &O;
        case 0x1e:
            return mem + mem[PC++];
        case 0x1f:
            return mem + PC++;
        default:
            //hacky
            lit_pos = (lit_pos + 1) % N_ADDRS;
            lit[lit_pos] = addr & 0x1f;
            return lit + lit_pos;
    }
}

static void decode(uint8_t addr) {
    assert(addr < 0x40);
    if (addr >= 0x10 && addr < 0x18 || addr == 0x1e || addr == 0x1f) {
        PC++;
    }
}

static void print_mem(uint16_t start, uint16_t end) {
    uint16_t pos;
    for (pos = start; pos < end; pos += 8) {
        printf("%4x:",pos);
        int ii;
        for (ii = 0; ii < 8; ii++) {
            printf(" %04x", mem[pos + ii]);
        }
        printf("\n");
    }
}

static void print_regs(void) {
    printf("A: %4x B: %4x C: %4x X: %4x Y: %4x Z: %4x I: %4x J: %4x\n",
           A, B, C, X, Y, Z, I, J);
    printf("PC: %4x SP: %4x O: %4x\n", PC, SP, O);
}

#ifdef ENABLE_TRACE
#define TRACE(x) printf("INSTR: %s a: %4x(%4x) b: %4x(%4x)\n",(x), a_addr, *a, b_addr, *b)
#else
#define TRACE(x)
#endif

void main_loop(void) {
    uint16_t instr;
    uint8_t skip = 0;
    while(1) {
        instr = mem[PC++];
        uint8_t opcode = instr & 0xf;
        uint8_t a_addr = (instr & (0x3f << 4)) >> 4;
        uint8_t b_addr = (instr & (0x3f << 10)) >> 10;
        uint16_t *a,*b;
        if (opcode == 0) {
            opcode = a_addr | 0x80;
            if (skip) {
                decode(b_addr);
            } else {
                a = lookup(b_addr);
            }
        } else {
            if (skip) {
                decode(a_addr);
                decode(b_addr);
            } else {
                a = lookup(a_addr);
                b = lookup(b_addr);
            }
        }
        if (skip) {
            skip = 0;
            continue;
        }
        switch(opcode) {
            case 0x1: TRACE("SET");
                *a = *b;
                break;
            case 0x2: TRACE("ADD");
                *a = *a + *b;
                break;
            case 0x3: TRACE("SUB");
                *a = *a - *b;
                break;
            case 0x4: TRACE("MUL");
                *a = *a * *b;
                break;
            case 0x5: TRACE("DIV");
                *a = *a / *b;
                break;
            case 0x6: TRACE("MOD");
                *a = *a % *b;
                break;
            case 0x7: TRACE("SHL");
                *a = *a << *b;
                break;
            case 0x8: TRACE("SHR");
                *a = *a >> *b;
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
                    skip = 1;
                }
                break;
            case 0xd: TRACE("IFN");
                if (*a == *b) {
                    skip = 1;
                }
                break;
            case 0xe: TRACE("IFG");
                if (*a <= *b) {
                    skip = 1;
                }
                break;
            case 0xf: TRACE("IFL");
                if (*a >= *b) {
                    skip = 1;
                }
                break;
            case 0x80 | 0x1: TRACE("JSR");
                mem[--SP] = PC;
                PC = *a;
                break;
            default:
                return;
                assert(0);
        }
#ifdef ENABLE_TRACE
        print_regs();
#endif
    }
}

int main(int argc, char **argv) {
    if (argc > 1) {
        printf("reading mem from %s\n",argv[1]);
        FILE *ifile = fopen(argv[1],"r");
        int pos, val;
        while (fscanf(ifile,"%x:",&pos) != EOF) {
            int ii;
            for (ii = 0; ii < 8; ii++) {
                fscanf(ifile, " %x",&val);
                mem[pos + ii] = val;
            }
        }
    }
    print_mem(0,256);
    main_loop();
    print_mem(0,256);
    print_regs();
    return 0;
}
