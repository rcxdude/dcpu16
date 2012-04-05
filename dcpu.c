#include <emu/dcpu.h>
#include <stdio.h>

int main(int argc, char **argv) {
    struct cpu_state state;
    init_cpu_state(&state);
    if (argc > 1) {
        printf("reading mem from %s\n",argv[1]);
        FILE *ifile = fopen(argv[1],"r");
        read_mem_file(&state,ifile);
        close(ifile);
    }
    print_mem(&state, 0, MEM_SIZE-1);
    run_forever(&state);
    print_mem(&state, 0, MEM_SIZE-1);
    print_regs(&state);
    return 0;
}
