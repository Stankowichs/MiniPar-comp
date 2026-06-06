# Roteiro curto de apresentação

## 1. Problema e objetivo - 30 segundos

"O projeto implementa um compilador para MiniPar. Ele recebe um arquivo da linguagem, valida o programa, traduz para C, chama o GCC e gera um executável real."

## 2. Pipeline - 45 segundos

Mostrar o comando `--tokens`, depois `--ast` e `--check`. Explicar: lexer cria tokens; parser monta a AST; semântico usa escopos e tabela de símbolos.

## 3. Geração C - 45 segundos

Executar um exemplo com `--emit-c` e abrir o arquivo gerado. Mostrar uma função ou uma classe convertida para `struct` e função com `self`.

## 4. Execução - 45 segundos

Executar fatorial e classe simples com `--run`. Explicar que o Python apenas coordena a compilação; o resultado final é um executável compilado pelo GCC.

## 5. Paralelismo - 45 segundos

Executar o exemplo 11 ou 12. Explicar que `par` gera threads com pthread e que a ordem das saídas pode variar.

## 6. Canais - 60 segundos

Abrir servidor e cliente em terminais diferentes. Mostrar `ADD 2 3` chegando ao servidor. Explicar que a runtime usa sockets TCP em localhost.

## 7. Fractal - 30 segundos

Executar o exemplo 15 e mostrar a matriz 27 x 27 do tapete de Sierpinski.

## 8. Limitações e conclusão - 30 segundos

Citar herança, captura de variáveis em `par`, protocolo simples de canais e recursos de coleção ainda ausentes. Encerrar reforçando o pipeline completo até o executável.
