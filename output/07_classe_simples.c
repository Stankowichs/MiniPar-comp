#include <stdio.h>
#include <stdlib.h>
#include <math.h>

typedef struct {
    int idade;
} Pessoa;

int Pessoa_getIdade(Pessoa* self);

int Pessoa_getIdade(Pessoa* self) {
    (void)self;
    return self->idade;
}

int main() {
    Pessoa p;
    p.idade = 20;
    printf("%d\n", Pessoa_getIdade(&p));
    return 0;
}
