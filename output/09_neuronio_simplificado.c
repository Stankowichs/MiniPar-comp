#include <stdio.h>
#include <stdlib.h>
#include <math.h>

typedef struct {
    double peso;
} Neuronio;

double Neuronio_ativacao(Neuronio* self, double soma);

double Neuronio_ativacao(Neuronio* self, double soma) {
    (void)self;
    if ((soma >= 0)) {
        return 1;
    } else {
        return 0;
    }
}

int main() {
    Neuronio n;
    n.peso = 0.5;
    printf("%g\n", Neuronio_ativacao(&n, 1));
    return 0;
}
