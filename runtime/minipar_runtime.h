#ifndef MINIPAR_RUNTIME_H
#define MINIPAR_RUNTIME_H

void mp_send(const char* host, int port, const char* message);
void mp_receive(int port, char* buffer, int buffer_size);
void mp_fractal_init(void);
void mp_fractal_set(int i, int j, char value);
void mp_fractal_print(void);

#endif
