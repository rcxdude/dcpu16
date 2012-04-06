#include <emu/dcpu.h>
#include <stdio.h>

int main(int argc, char **argv) {
    struct cpu s;
    init_cpu(&s);
    if (argc > 1) {
        printf("reading mem from %s\n",argv[1]);
        FILE *ifile = fopen(argv[1],"r");
        read_mem_file(&s,ifile);
        close(ifile);
    }
    print_mem(&s, 0, MEM_SIZE-1);
    set_breakpoint(&s,0x8);
    while(!s.stopped) {
        run_to_breakpoint(&s,0);
        printf("Hit breakpoint 0x%04x\n",s.breakpoint);
        print_regs(&s);
        print_mem(&s, 0 ,MEM_SIZE-1);
    }
    return 0;
}
