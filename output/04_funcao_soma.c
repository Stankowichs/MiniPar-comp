#include <stdio.h>
#include <stdlib.h>
#include <math.h>

int soma(int a, int b);

int soma(int a, int b) {
    return (a + b);
}

int main() {
    printf("%d\n", soma(2, 3));
    return 0;
}
