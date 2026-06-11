# MiniPar 2026.1

Compilador acadêmico para um subconjunto da linguagem MiniPar. O compilador recebe um arquivo `.mpar`, executa análise léxica, sintática e semântica, gera código C, compila com GCC e pode executar o programa gerado.

## Pipeline

```text
.mpar -> Lexer -> Parser -> AST -> Análise Semântica -> Código C -> GCC -> Executável
```

## Requisitos

- Python 3.10 ou superior
- GCC com suporte a C e pthreads
- Windows: MinGW-w64/MSYS2 recomendado; o GCC deve estar no `PATH`
- Linux: pacote `gcc` e suporte POSIX padrão

Verifique a instalação:

```powershell
py --version
gcc --version
```

No Linux/macOS, substitua `py` por `python3` nos comandos abaixo.

## Estrutura

```text
src/                    Front-end, análise semântica e gerador C
runtime/                Runtime C de canais e apoio ao fractal
examples/               Programas MiniPar de demonstração
examples/erros/         Casos que devem falhar
output/                 Código C e executáveis gerados
docs/                   Relatório-base, UML e roteiro
scripts/test_all.py     Testes automatizados principais
scripts/test_channels.py Teste isolado de canais TCP
```

## Uso

Abra o terminal na raiz do projeto.

### Mostrar tokens

```powershell
py src/compiler.py examples/01_print_variaveis.mpar --tokens
```

### Mostrar AST

```powershell
py src/compiler.py examples/01_print_variaveis.mpar --ast
```

### Validar lexer, parser e semântica

```powershell
py src/compiler.py examples/01_print_variaveis.mpar --check
```

### Gerar C

```powershell
py src/compiler.py examples/07_classe_simples.mpar --emit-c output/07_classe_simples.c
```

### Compilar e executar

```powershell
py src/compiler.py examples/02_fatorial.mpar --run
```

## Recursos implementados

- Tipos básicos: `int`, `number`, `string`, `bool` e `void`
- Variáveis, atribuições e expressões aritméticas/lógicas
- `print` e `println`
- `if/else`, `while`, `do-while`, `break` e `continue`
- Funções, parâmetros, chamadas e `return`
- Classes simples, atributos, métodos, `this`, `new` e acesso a propriedades
- Blocos `seq` e `par`; `par` é traduzido para pthreads
- `c_channel`, `send` e `receive` por sockets TCP
- Exemplo de tapete de Sierpinski em matriz 27 x 27

## Teste automatizado

```powershell
py scripts/test_all.py
```

O script valida os exemplos 01 a 12, o exemplo 15 (`15_fractal_matriz.mpar`) e os casos de erro. Para testar canais separadamente, execute `py scripts/test_channels.py`.

## Teste manual dos canais

Abra dois terminais na raiz do projeto.

Terminal 1:

```powershell
py src/compiler.py examples/13_canal_servidor.mpar --run
```

Terminal 2:

```powershell
py src/compiler.py examples/14_canal_cliente.mpar --run
```

Saída esperada no servidor:

```text
ADD 2 3
```

Para testar em máquinas diferentes, execute o servidor na máquina receptora, libere a porta no firewall e troque `127.0.0.1` no cliente pelo IPv4 da máquina servidora. O runtime aceita IPv4 literal.

## Exemplos e saídas esperadas

| Exemplo | Resultado |
|---|---|
| 01 | `15` |
| 02 | `120` |
| 03 | `0 1 1 2 3` |
| 04 | `5` |
| 05 | `1 2 4` |
| 06 | `0 1 2` |
| 07 | `20` |
| 08 | `14` |
| 09 | `1` |
| 10 | `1 2 3` |
| 11 | `100` e `200`, ordem não garantida |
| 12 | fatorial e Fibonacci, ordem não garantida |
| 13 + 14 | servidor recebe `ADD 2 3` |
| 15 | matriz 27 x 27 do tapete de Sierpinski |

## Limitações conhecidas

- Herança real e `super` não foram implementados.
- Construtores com argumentos não inicializam campos automaticamente.
- `par` exige statements independentes e não captura variáveis locais externas.
- Canais usam mensagens string simples, sem serialização de tipos.
- O backend C ainda não cobre listas, dicionários, `for-in` e entrada interativa.
- O fractal usa funções auxiliares de runtime e uma matriz fixa de 27 x 27.

## Documentação da entrega

- `docs/RELATORIO_BASE.md`: texto-base para o relatório
- `docs/UML.md`: diagramas Mermaid de casos de uso, componentes e classes
- `docs/ROTEIRO_APRESENTACAO.md`: roteiro curto de demonstração
- `evidence/README.md`: checklist de prints e evidências
