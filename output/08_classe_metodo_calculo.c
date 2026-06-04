#include <stdio.h>
#include <stdlib.h>
#include <math.h>

typedef struct {
    int __dummy;
} Calculadora;

int Calculadora_dobro(Calculadora* self, int x);

int Calculadora_dobro(Calculadora* self, int x) {
    (void)self;
    return (x * 2);
}

int main() {
    Calculadora c;
    printf("%d\n", Calculadora_dobro(&c, 7));
    return 0;
}
