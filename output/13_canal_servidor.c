#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include "minipar_runtime.h"

int main() {
    /* c_channel calculadora, computador_1, computador_2 */
    char __recv_buffer_0[1024];
    mp_receive(5001, __recv_buffer_0, 1024);
    printf("%s\n", __recv_buffer_0);
    return 0;
}
