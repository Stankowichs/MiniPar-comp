#ifndef MINIPAR_RUNTIME_H
#define MINIPAR_RUNTIME_H

void mp_send(const char* host, int port, const char* message);
void mp_receive(int port, char* buffer, int buffer_size);

#endif
