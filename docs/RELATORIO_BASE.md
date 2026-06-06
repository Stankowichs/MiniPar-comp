# Relatório - Compilador MiniPar 2026.1

## 1. Introdução

Este projeto implementa um compilador para um subconjunto funcional da linguagem MiniPar. A base do front-end foi adaptada de um interpretador Java anterior, mas a versão atual foi reorganizada em Python e passou a gerar código C, que é compilado pelo GCC. O objetivo foi construir um MVP capaz de demonstrar análise léxica, sintática e semântica, geração de código, orientação a objetos simples, paralelismo e comunicação por canais.

## 2. Arquitetura

O pipeline implementado é:

```text
Código MiniPar -> Lexer -> Tokens -> Parser -> AST -> Análise Semântica
               -> Gerador C -> GCC -> Executável
```

### 2.1 Lexer

O lexer percorre o código-fonte, ignora comentários iniciados por `#`, registra linha e coluna e produz tokens. Erros de caractere ou literal inválido resultam em `LexerError`.

### 2.2 Parser

O parser descendente recursivo consome tokens, respeita a precedência de operadores e produz a AST. Erros de sintaxe resultam em `ParseError`.

### 2.3 AST

A AST representa declarações, statements e expressões. Entre os nós principais estão `Program`, `VarDecl`, `FuncDecl`, `ClassDecl`, `MethodDecl`, `IfStmt`, `WhileStmt`, `BinaryExpr`, `FunctionCall`, `MethodCall`, `SeqBlock`, `ParBlock`, `CanalDecl`, `SendStmt` e `ReceiveStmt`.

### 2.4 Tabela de símbolos e análise semântica

A tabela de símbolos possui escopos encadeados e registra variáveis, parâmetros, funções, classes e métodos. A análise detecta, entre outros casos, símbolo duplicado, variável não declarada, função ou classe inexistente e quantidade incorreta de argumentos.

### 2.5 Gerador C

O backend percorre a AST e gera C. Funções MiniPar tornam-se funções C. Classes simples tornam-se `structs`; métodos tornam-se funções que recebem `self`. Blocos `seq` permanecem blocos normais. Blocos `par` usam `pthread_create` e `pthread_join`.

### 2.6 Runtime

A runtime em C fornece `mp_send` e `mp_receive` para comunicação TCP. Também contém funções auxiliares da demonstração do tapete de Sierpinski.

## 3. Gramática adaptada

O subconjunto cobre tipos básicos, variáveis, expressões, decisões, repetições, funções, classes simples, blocos sequenciais e paralelos e canais. A implementação preserva a proposta da linguagem anterior, mas recursos sem suporte no backend foram delimitados como limitações.

## 4. Estratégia de tradução

- Variável MiniPar -> variável C compatível
- Função MiniPar -> função C e protótipo
- Classe MiniPar -> `struct`
- Método -> função C com ponteiro `self`
- `new` -> alocação/inicialização da estrutura
- `seq` -> bloco comum
- `par` -> funções de thread + pthreads
- `send/receive` -> chamadas à runtime TCP

## 5. Testes

Foram preparados exemplos numerados de 01 a 15 e casos de erro. O script `scripts/test_all.py` executa testes de integração, verifica saídas e testa cliente e servidor em processos separados.

O tapete de Sierpinski usa uma matriz fixa de 27 por 27 caracteres. O teste verifica dimensões e caracteres. Os testes de paralelismo aceitam variação de ordem.

## 6. Limitações

- Herança e `super` não implementados.
- Construtores com argumentos não inicializam atributos automaticamente.
- `par` não captura variáveis locais externas.
- Protocolo de canais limitado a strings simples.
- Listas, dicionários, `for-in` e input não integram o backend final.
- Fractal dependente de matriz fixa e funções auxiliares de runtime.

## 7. Conclusão

O projeto demonstra o ciclo completo de compilação de uma linguagem de alto nível para C. Além do front-end, integra geração de executável, OO simples, threads e sockets. O MVP atende ao objetivo de demonstrar os componentes centrais de um compilador e explicita as extensões que podem ser implementadas em trabalhos futuros.
