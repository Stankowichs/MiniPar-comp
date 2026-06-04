#include <stdio.h>
#include <stdlib.h>
#include <math.h>

int main() {
    int n = 5;
    int a = 0;
    int b = 1;
    int i = 0;
    while ((i < n)) {
        printf("%d\n", a);
        int proximo = (a + b);
        a = b;
        b = proximo;
        i = (i + 1);
    }
    return 0;
}
