"""Testes de integração do compilador MiniPar.

Execute na raiz do projeto:
    py scripts/test_all.py
ou:
    python3 scripts/test_all.py
"""

from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMPILER = ROOT / "src" / "compiler.py"
PYTHON = sys.executable


def run_compiler(example: str, *args: str, timeout: int = 20) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [PYTHON, str(COMPILER), str(ROOT / example), *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        timeout=timeout,
    )


def normalized_lines(text: str) -> list[str]:
    return [line.rstrip() for line in text.replace("\r\n", "\n").splitlines() if line.strip()]


def assert_run(example: str, expected: list[str], unordered: bool = False) -> None:
    result = run_compiler(example, "--run")
    if result.returncode != 0:
        raise AssertionError(f"{example} falhou:\n{result.stdout}{result.stderr}")

    actual = normalized_lines(result.stdout)
    if unordered:
        ok = sorted(actual) == sorted(expected)
    else:
        ok = actual == expected
    if not ok:
        raise AssertionError(f"{example}: esperado {expected}, obtido {actual}")


def assert_check(example: str) -> None:
    result = run_compiler(example, "--check")
    if result.returncode != 0 or "concluidas com sucesso" not in result.stdout:
        raise AssertionError(f"{example} não passou no --check:\n{result.stdout}{result.stderr}")


def assert_error(example: str) -> None:
    result = run_compiler(example, "--check")
    if result.returncode == 0:
        raise AssertionError(f"{example} deveria falhar, mas terminou com sucesso")


def assert_fractal() -> None:
    result = run_compiler("examples/15_fractal_sierpinski.mpar", "--run")
    if result.returncode != 0:
        raise AssertionError(result.stdout + result.stderr)
    lines = normalized_lines(result.stdout)
    if len(lines) != 27 or any(len(line) != 27 for line in lines):
        raise AssertionError("Fractal deve possuir exatamente 27 linhas de 27 caracteres")
    if any(set(line) - {"*", "."} for line in lines):
        raise AssertionError("Fractal contém caracteres inesperados")


def assert_channels() -> None:
    server_c = ROOT / "output" / "13_canal_servidor_test.c"
    client_c = ROOT / "output" / "14_canal_cliente_test.c"
    server_exe = server_c.with_suffix(".exe" if sys.platform.startswith("win") else "")
    client_exe = client_c.with_suffix(".exe" if sys.platform.startswith("win") else "")

    for source, c_path in [
        ("examples/13_canal_servidor.mpar", server_c),
        ("examples/14_canal_cliente.mpar", client_c),
    ]:
        generated = run_compiler(source, "--emit-c", str(c_path))
        if generated.returncode != 0:
            raise AssertionError(generated.stdout + generated.stderr)

    def compile_c(c_path: Path, executable: Path) -> None:
        command = [
            "gcc", "-O2", str(c_path), str(ROOT / "runtime/minipar_runtime.c"),
            "-I", str(ROOT / "runtime"), "-o", str(executable), "-lm", "-pthread",
        ]
        if sys.platform.startswith("win"):
            command.append("-lws2_32")
        result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, timeout=30)
        if result.returncode != 0:
            raise AssertionError(result.stdout + result.stderr)

    compile_c(server_c, server_exe)
    compile_c(client_c, client_exe)

    server = subprocess.Popen(
        [str(server_exe)], cwd=ROOT, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    try:
        time.sleep(0.5)
        client = subprocess.run(
            [str(client_exe)], cwd=ROOT, text=True,
            capture_output=True, timeout=10,
        )
        if client.returncode != 0:
            raise AssertionError("Cliente falhou:\n" + client.stdout + client.stderr)
        stdout, stderr = server.communicate(timeout=10)
    except Exception:
        server.kill()
        server.communicate(timeout=5)
        raise

    if server.returncode != 0:
        raise AssertionError("Servidor falhou:\n" + stdout + stderr)
    if normalized_lines(stdout) != ["ADD 2 3"]:
        raise AssertionError(f"Servidor deveria receber ADD 2 3; recebeu {stdout!r}")


def main() -> int:
    tests: list[tuple[str, callable]] = []

    expected_outputs = {
        "examples/01_print_variaveis.mpar": ["15"],
        "examples/02_fatorial.mpar": ["120"],
        "examples/03_fibonacci.mpar": ["0", "1", "1", "2", "3"],
        "examples/04_funcao_soma.mpar": ["5"],
        "examples/05_break_continue.mpar": ["1", "2", "4"],
        "examples/06_do_while.mpar": ["0", "1", "2"],
        "examples/07_classe_simples.mpar": ["20"],
        "examples/08_classe_metodo_calculo.mpar": ["14"],
        "examples/09_neuronio_simplificado.mpar": ["1"],
        "examples/10_seq_simples.mpar": ["1", "2", "3"],
    }

    for example, expected in expected_outputs.items():
        tests.append((example, lambda e=example, x=expected: assert_run(e, x)))

    tests.append(("examples/11_par_funcoes.mpar", lambda: assert_run(
        "examples/11_par_funcoes.mpar", ["100", "200"], unordered=True)))
    tests.append(("examples/12_par_fatorial_fibonacci.mpar", lambda: assert_run(
        "examples/12_par_fatorial_fibonacci.mpar",
        ["120", "0", "1", "1", "2", "3"], unordered=True)))
    tests.append(("examples/15_fractal_sierpinski.mpar", assert_fractal))
    tests.append(("erro: variável não declarada", lambda: assert_error(
        "examples/erros/01_variavel_nao_declarada.mpar")))
    tests.append(("erro: ponto e vírgula ausente", lambda: assert_error(
        "examples/erros/02_erro_sintatico_sem_ponto_virgula.mpar")))

    failures = 0
    for name, test in tests:
        try:
            test()
            print(f"[OK] {name}")
        except Exception as error:
            failures += 1
            print(f"[FALHOU] {name}: {error}")

    total = len(tests)
    passed = total - failures
    print(f"\nResultado: {passed}/{total} testes passaram.")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
