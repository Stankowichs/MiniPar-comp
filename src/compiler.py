import argparse
import subprocess
import sys
from dataclasses import fields, is_dataclass
from pathlib import Path
from typing import Any

from ast_nodes import ASTNode
from c_generator import CGenerator
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

    return repr(value)


def read_source(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def run_lexer(source: str):
    return Lexer(source).scan_tokens()


def run_parser(tokens: list) -> ASTNode:
    return Parser(tokens).parse()


def run_semantic(ast: ASTNode):
    return SemanticAnalyzer().analyze(ast)


def generate_c(ast: ASTNode) -> str:
    return CGenerator().generate(ast)


def write_c_file(path: Path, code: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(code, encoding="utf-8")


def default_c_output_path(source_path: Path) -> Path:
    return Path("output") / f"{source_path.stem}.c"


def executable_path_for(c_path: Path) -> Path:
    suffix = ".exe" if sys.platform.startswith("win") else ""
    return c_path.with_suffix(suffix)


def run_gcc(c_path: Path, executable_path: Path) -> int:
    executable_path.parent.mkdir(parents=True, exist_ok=True)
    command = ["gcc", str(c_path), "-o", str(executable_path), "-lm"]

    try:
        compile_result = subprocess.run(command, text=True, capture_output=True)
    except FileNotFoundError:
        print("GCC não encontrado. Instale o GCC ou adicione ao PATH.")
        return 1

    if compile_result.returncode != 0:
        print("Erro ao compilar com GCC.")
        if compile_result.stdout:
            print(compile_result.stdout, end="")
        if compile_result.stderr:
            print(compile_result.stderr, end="")
        return compile_result.returncode

    run_result = subprocess.run([str(executable_path)], text=True, capture_output=True)
    if run_result.stdout:
        print(run_result.stdout, end="")
    if run_result.stderr:
        print(run_result.stderr, end="")
    return run_result.returncode


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="CLI principal do front-end MiniPar: lexer, parser, semantico e backend C minimo."
    )
    parser.add_argument("source", help="Arquivo .mpar de entrada.")
    parser.add_argument("--tokens", action="store_true", help="Imprime a lista de tokens gerada pelo lexer.")
    parser.add_argument("--ast", action="store_true", help="Imprime a AST gerada pelo parser.")
    parser.add_argument("--check", action="store_true", help="Executa lexer, parser e analise semantica.")
    parser.add_argument("--emit-c", metavar="CAMINHO", help="Gera codigo C e salva no caminho informado.")
    parser.add_argument("--run", action="store_true", help="Gera C, compila com GCC e executa o binario.")
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

        needs_ast = args.ast or args.check or args.emit_c or args.run
        ast = run_parser(tokens) if needs_ast else None

        if args.ast and ast is not None:
            print(format_ast(ast))

        if args.check or args.emit_c or args.run:
            if ast is None:
                ast = run_parser(tokens)
            run_semantic(ast)
            if args.check:
                print("OK: analise lexica, sintatica e semantica concluidas com sucesso.")

        if args.emit_c:
            if ast is None:
                ast = run_parser(tokens)
            c_output_path = Path(args.emit_c)
            write_c_file(c_output_path, generate_c(ast))
            print(f"C gerado em: {c_output_path}")

        if args.run:
            if ast is None:
                ast = run_parser(tokens)
            c_output_path = default_c_output_path(source_path)
            executable_path = executable_path_for(c_output_path)
            write_c_file(c_output_path, generate_c(ast))
            return run_gcc(c_output_path, executable_path)

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
