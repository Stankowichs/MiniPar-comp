#include "minipar_runtime.h"

#include <stdio.h>
#include <string.h>

#ifdef _WIN32
#include <winsock2.h>
#include <ws2tcpip.h>

static void mp_socket_startup(void) {
    static int initialized = 0;
    WSADATA wsa_data;
    if (!initialized) {
        if (WSAStartup(MAKEWORD(2, 2), &wsa_data) != 0) {
            fprintf(stderr, "Erro ao inicializar Winsock.\n");
            return;
        }
        initialized = 1;
    }
}

static void mp_close_socket(SOCKET socket_fd) {
    closesocket(socket_fd);
}
#else
#include <arpa/inet.h>
#include <netinet/in.h>
#include <sys/socket.h>
#include <unistd.h>

typedef int SOCKET;
#define INVALID_SOCKET (-1)
#define SOCKET_ERROR (-1)

static void mp_socket_startup(void) {
}

static void mp_close_socket(SOCKET socket_fd) {
    close(socket_fd);
}
#endif

void mp_send(const char* host, int port, const char* message) {
    SOCKET socket_fd;
    struct sockaddr_in address;

    mp_socket_startup();

    socket_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (socket_fd == INVALID_SOCKET) {
        fprintf(stderr, "Erro ao criar socket de envio.\n");
        return;
    }

    memset(&address, 0, sizeof(address));
    address.sin_family = AF_INET;
    address.sin_port = htons((unsigned short)port);

    if (inet_pton(AF_INET, host, &address.sin_addr) <= 0) {
        fprintf(stderr, "Host invalido para envio: %s\n", host);
        mp_close_socket(socket_fd);
        return;
    }

    if (connect(socket_fd, (struct sockaddr*)&address, sizeof(address)) == SOCKET_ERROR) {
        fprintf(stderr, "Erro ao conectar em %s:%d.\n", host, port);
        mp_close_socket(socket_fd);
        return;
    }

    send(socket_fd, message, (int)strlen(message), 0);
    mp_close_socket(socket_fd);
}

void mp_receive(int port, char* buffer, int buffer_size) {
    SOCKET server_fd;
    SOCKET client_fd;
    struct sockaddr_in address;
    int opt = 1;
    int received;

    if (buffer_size <= 0) {
        return;
    }
    buffer[0] = '\0';

    mp_socket_startup();

    server_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (server_fd == INVALID_SOCKET) {
        fprintf(stderr, "Erro ao criar socket de recebimento.\n");
        return;
    }

    setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR, (const char*)&opt, sizeof(opt));

    memset(&address, 0, sizeof(address));
    address.sin_family = AF_INET;
    address.sin_addr.s_addr = htonl(INADDR_ANY);
    address.sin_port = htons((unsigned short)port);

    if (bind(server_fd, (struct sockaddr*)&address, sizeof(address)) == SOCKET_ERROR) {
        fprintf(stderr, "Erro ao abrir porta %d para recebimento.\n", port);
        mp_close_socket(server_fd);
        return;
    }

    if (listen(server_fd, 1) == SOCKET_ERROR) {
        fprintf(stderr, "Erro ao escutar porta %d.\n", port);
        mp_close_socket(server_fd);
        return;
    }

    client_fd = accept(server_fd, NULL, NULL);
    if (client_fd == INVALID_SOCKET) {
        fprintf(stderr, "Erro ao aceitar conexao.\n");
        mp_close_socket(server_fd);
        return;
    }

    received = recv(client_fd, buffer, buffer_size - 1, 0);
    if (received < 0) {
        received = 0;
    }
    buffer[received] = '\0';

    mp_close_socket(client_fd);
    mp_close_socket(server_fd);
}
