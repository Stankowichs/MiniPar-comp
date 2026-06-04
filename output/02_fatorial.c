#include <stdio.h>
#include <stdlib.h>
#include <math.h>

int fatorial(int n);

int fatorial(int n) {
    int resultado = 1;
    while ((n > 1)) {
        resultado = (resultado * n);
        n = (n - 1);
    }
    return resultado;
}

int main() {
    printf("%d\n", fatorial(5));
    return 0;
}
