#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <pthread.h>

void tarefa1();
void tarefa2();

void tarefa1() {
    printf("%d\n", 100);
}
void tarefa2() {
    printf("%d\n", 200);
}

void* __par_task_0(void* arg) {
    (void)arg;
    tarefa1();
    return NULL;
}
void* __par_task_1(void* arg) {
    (void)arg;
    tarefa2();
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
