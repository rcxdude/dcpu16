#ifndef DCPU_EMU_H
#define DCPU_EMU_H

#include <stdint.h>
#include <stdio.h>
#define MEM_SIZE 0x10000
#define ENABLE_TRACE

#define BREAKPOINT 1 << 1
#define WATCHPOINT 1 << 2

#define STOP_INSTR 1
#define INVALID_INSTR 2

struct cpu {
    uint16_t mem[MEM_SIZE];
    uint16_t A,B,C,X,Y,Z,I,J,PC,SP,O;
    uint8_t skip;
    unsigned long cycles;
    int stopped;
    uint8_t breakpoints[MEM_SIZE];
    int breakpoint;
};

void init_cpu(struct cpu *s);
void step_cpu(struct cpu *s); 
void run_forever(struct cpu *s); 
void run_to_breakpoint(struct cpu *s);
void read_mem_file(struct cpu *s, FILE *ifile);
void get_next_nonzero_chunk(struct cpu *s, uint16_t last_addr, uint16_t *start_addr, uint16_t *end_addr);

void set_breakpoint(struct cpu *s, uint16_t address);
void del_breakpoint(struct cpu *s, uint16_t address);
void set_watchpoint(struct cpu *s, uint16_t address);
void del_watchpoint(struct cpu *s, uint16_t address);

#endif
