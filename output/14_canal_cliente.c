#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include "minipar_runtime.h"

int main() {
    /* c_channel calculadora, computador_1, computador_2 */
    mp_send("127.0.0.1", 5001, "ADD 2 3");
    return 0;
}
