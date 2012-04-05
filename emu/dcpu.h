#ifndef DCPU_EMU_H
#define DCPU_EMU_H

#include <stdint.h>
#include <stdio.h>
#define MEM_SIZE 0x10000
#define ENABLE_TRACE

struct cpu_state {
    uint16_t mem[MEM_SIZE];
    uint16_t A,B,C,X,Y,Z,I,J,PC,SP,O;
    uint8_t skip;
    unsigned long cycles;
    int stopped;
};

void init_cpu_state(struct cpu_state *s);
void step_cpu(struct cpu_state *s); 
void run_forever(struct cpu_state *s); 
void read_mem_file(struct cpu_state *s, FILE *ifile);

#endif
