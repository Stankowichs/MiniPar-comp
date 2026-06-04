#include <stdio.h>
#include <stdlib.h>
#include <math.h>

int main() {
    int i = 0;
    while ((i < 5)) {
        i = (i + 1);
        if ((i == 3)) {
            continue;
        }
        printf("%d\n", i);
        if ((i == 4)) {
            break;
        }
    }
    return 0;
}
