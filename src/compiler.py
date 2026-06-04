import argparse
from dataclasses import fields, is_dataclass
from pathlib import Path
from typing import Any

from ast_nodes import ASTNode
from errors import CompilerError
from lexer import Lexer
from parser import Parser
from semantic import SemanticAnalyzer


def format_ast(value: Any, indent: int = 0) -> str:
    prefix = " " * indent

    if not is_dataclass(value) and not isinstance(value, list):
        return repr(value)

    if isinstance(value, list):
        if not value:
            return "[]"
        lines = [f"{prefix}["]
        for item in value:
            lines.append(format_ast(item, indent + 2))
        lines.append(f"{prefix}]")
        return "\n".join(lines)

    if is_dataclass(value):
        class_name = type(value).__name__
        lines = [f"{prefix}{class_name}("]
        for field in fields(value):
            field_value = getattr(value, field.name)
            rendered = format_ast(field_value, indent + 4)
            if "\n" in rendered:
                lines.append(f"{prefix}  {field.name}=")
                lines.append(rendered)
            else:
                lines.append(f"{prefix}  {field.name}={rendered}")
        lines.append(f"{prefix})")
        return "\n".join(lines)


def read_source(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def run_lexer(source: str):
    return Lexer(source).scan_tokens()


def run_parser(tokens: list) -> ASTNode:
    return Parser(tokens).parse()


def run_semantic(ast: ASTNode):
    return SemanticAnalyzer().analyze(ast)


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="CLI principal do front-end MiniPar: lexer, parser e analisador semantico."
    )
    parser.add_argument("source", help="Arquivo .mpar de entrada.")
    parser.add_argument("--tokens", action="store_true", help="Imprime a lista de tokens gerada pelo lexer.")
    parser.add_argument("--ast", action="store_true", help="Imprime a AST gerada pelo parser.")
    parser.add_argument("--check", action="store_true", help="Executa lexer, parser e analise semantica.")
    parser.add_argument("--emit-c", action="store_true", help="Placeholder para geracao de codigo C.")
    parser.add_argument("--run", action="store_true", help="Placeholder para execucao via GCC.")
    return parser


def main() -> int:
    args = build_argument_parser().parse_args()
    source_path = Path(args.source)

    if not source_path.exists():
        print(f"Erro: arquivo nao encontrado: {source_path}")
        return 1

    try:
        source = read_source(source_path)
        tokens = run_lexer(source)

        if args.tokens:
            for token in tokens:
                print(token)

        needs_ast = args.ast or args.check
        ast = run_parser(tokens) if needs_ast else None

        if args.ast and ast is not None:
            print(format_ast(ast))

        if args.check:
            if ast is None:
                ast = run_parser(tokens)
            run_semantic(ast)
            print("OK: analise lexica, sintatica e semantica concluidas com sucesso.")

        if args.emit_c:
            print("TODO: geração de código C ainda não implementada.")

        if args.run:
            print("TODO: execução via GCC ainda não implementada.")

        if not any([args.tokens, args.ast, args.check, args.emit_c, args.run]):
            ast = run_parser(tokens)
            run_semantic(ast)
            print("OK: analise lexica, sintatica e semantica concluidas com sucesso.")

        return 0
    except CompilerError as error:
        print(error)
        return 1
    except OSError as error:
        print(f"Erro ao ler arquivo: {error}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
