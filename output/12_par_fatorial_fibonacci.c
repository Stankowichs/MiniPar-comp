#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <pthread.h>

void mostrar_fatorial();
void mostrar_fibonacci();

void mostrar_fatorial() {
    int n = 5;
    int r = 1;
    while ((n > 1)) {
        r = (r * n);
        n = (n - 1);
    }
    printf("%d\n", r);
}
void mostrar_fibonacci() {
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
}

void* __par_task_0(void* arg) {
    (void)arg;
    mostrar_fatorial();
    return NULL;
}
void* __par_task_1(void* arg) {
    (void)arg;
    mostrar_fibonacci();
    return NULL;
}

int main() {
    {
        pthread_t __t0;
        pthread_t __t1;
        pthread_create(&__t0, NULL, __par_task_0, NULL);
        pthread_create(&__t1, NULL, __par_task_1, NULL);
        pthread_join(__t0, NULL);
        pthread_join(__t1, NULL);
    }
    return 0;
}
