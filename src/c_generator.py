from ast_nodes import (
    Assignment,
    ASTNode,
    BinaryExpr,
    FuncDecl,
    FunctionCall,
    Identifier,
    IfStmt,
    Literal,
    PrintStmt,
    Program,
    ReturnStmt,
    UnaryExpr,
    VarDecl,
    WhileStmt,
)
from errors import CompilerError


TYPE_MAP = {
    "int": "int",
    "number": "double",
    "bool": "int",
    "string": "char*",
    "void": "void",
}


class CGeneratorError(CompilerError):
    """Erro gerado durante a geracao de codigo C."""


class CGenerator:
    def __init__(self):
        self.function_return_types: dict[str, str] = {}
        self.scopes: list[dict[str, str]] = []
        self.current_return_type: str | None = None

    def generate(self, program: Program) -> str:
        self.collect_function_signatures(program)
        function_declarations = []
        main_statements = []

        for statement in program.statements:
            if isinstance(statement, FuncDecl):
                function_declarations.append(self.generate_function(statement))
            else:
                main_statements.append(statement)

        lines = [
            "#include <stdio.h>",
            "#include <stdlib.h>",
            "#include <math.h>",
            "",
        ]

        if function_declarations:
            lines.extend(function_declarations)
            lines.append("")

        self.push_scope()
        try:
            lines.append("int main() {")
            for statement in main_statements:
                lines.extend(self.generate_statement(statement, indent=1))
            lines.append("    return 0;")
            lines.append("}")
        finally:
            self.pop_scope()

        return "\n".join(lines) + "\n"

    def collect_function_signatures(self, program: Program) -> None:
        for statement in program.statements:
            if isinstance(statement, FuncDecl):
                self.function_return_types[statement.name] = statement.return_type

    def generate_function(self, node: FuncDecl) -> str:
        return_type = self.c_type(node.return_type)
        params = ", ".join(f"{self.c_type(param.type)} {param.name}" for param in node.parameters)
        lines = [f"{return_type} {node.name}({params}) {{"]

        self.push_scope()
        previous_return_type = self.current_return_type
        self.current_return_type = node.return_type
        try:
            for param in node.parameters:
                self.define_variable(param.name, param.type)
            for statement in node.body:
                lines.extend(self.generate_statement(statement, indent=1))
        finally:
            self.current_return_type = previous_return_type
            self.pop_scope()

        lines.append("}")
        return "\n".join(lines)

    def generate_statement(self, node: ASTNode, indent: int) -> list[str]:
        prefix = "    " * indent

        if isinstance(node, VarDecl):
            c_type = self.c_type(node.type)
            self.define_variable(node.name, node.type)
            if node.initializer is None:
                return [f"{prefix}{c_type} {node.name};"]
            return [f"{prefix}{c_type} {node.name} = {self.generate_expression(node.initializer)};"]

        if isinstance(node, Assignment):
            return [f"{prefix}{node.var_name} = {self.generate_expression(node.value)};"]

        if isinstance(node, PrintStmt):
            lines = []
            for argument in node.arguments:
                expression = self.generate_expression(argument)
                fmt = self.printf_format(self.infer_type(argument))
                lines.append(f'{prefix}printf("{fmt}\\n", {expression});')
            return lines

        if isinstance(node, IfStmt):
            lines = [f"{prefix}if ({self.generate_expression(node.condition)}) {{"]
            self.push_scope()
            try:
                for statement in node.then_branch:
                    lines.extend(self.generate_statement(statement, indent + 1))
            finally:
                self.pop_scope()

            if node.else_branch is None:
                lines.append(f"{prefix}}}")
                return lines

            lines.append(f"{prefix}}} else {{")
            self.push_scope()
            try:
                for statement in node.else_branch:
                    lines.extend(self.generate_statement(statement, indent + 1))
            finally:
                self.pop_scope()
            lines.append(f"{prefix}}}")
            return lines

        if isinstance(node, WhileStmt):
            lines = [f"{prefix}while ({self.generate_expression(node.condition)}) {{"]
            self.push_scope()
            try:
                for statement in node.body:
                    lines.extend(self.generate_statement(statement, indent + 1))
            finally:
                self.pop_scope()
            lines.append(f"{prefix}}}")
            return lines

        if isinstance(node, ReturnStmt):
            if node.value is None:
                return [f"{prefix}return;"]
            return [f"{prefix}return {self.generate_expression(node.value)};"]

        if isinstance(node, (BinaryExpr, UnaryExpr, FunctionCall, Identifier, Literal)):
            return [f"{prefix}{self.generate_expression(node)};"]

        raise CGeneratorError(f"Geracao de C nao implementada para no: {type(node).__name__}")

    def generate_expression(self, node: ASTNode) -> str:
        if isinstance(node, Literal):
            return self.generate_literal(node)

        if isinstance(node, Identifier):
            return node.name

        if isinstance(node, BinaryExpr):
            left = self.generate_expression(node.left)
            right = self.generate_expression(node.right)
            return f"({left} {node.operator} {right})"

        if isinstance(node, UnaryExpr):
            operand = self.generate_expression(node.operand)
            return f"({node.operator}{operand})"

        if isinstance(node, Assignment):
            value = self.generate_expression(node.value)
            return f"({node.var_name} = {value})"

        if isinstance(node, FunctionCall):
            args = ", ".join(self.generate_expression(argument) for argument in node.arguments)
            return f"{node.function_name}({args})"

        raise CGeneratorError(f"Geracao de expressao C nao implementada para no: {type(node).__name__}")

    def generate_literal(self, node: Literal) -> str:
        if isinstance(node.value, bool):
            return "1" if node.value else "0"
        if isinstance(node.value, str):
            return '"' + self.escape_c_string(node.value) + '"'
        return str(node.value)

    def infer_type(self, node: ASTNode) -> str | None:
        if isinstance(node, Literal):
            if isinstance(node.value, bool):
                return "bool"
            if isinstance(node.value, int):
                return "int"
            if isinstance(node.value, float):
                return "number"
            if isinstance(node.value, str):
                return "string"

        if isinstance(node, Identifier):
            return self.lookup_variable(node.name)

        if isinstance(node, FunctionCall):
            return self.function_return_types.get(node.function_name)

        if isinstance(node, UnaryExpr):
            return self.infer_type(node.operand)

        if isinstance(node, Assignment):
            return self.lookup_variable(node.var_name)

        if isinstance(node, BinaryExpr):
            left_type = self.infer_type(node.left)
            right_type = self.infer_type(node.right)
            if node.operator in {"==", "!=", "<", "<=", ">", ">=", "&&", "||"}:
                return "bool"
            if left_type == "number" or right_type == "number":
                return "number"
            if left_type == "string" or right_type == "string":
                return "string"
            return "int"

        return None

    def printf_format(self, type_name: str | None) -> str:
        if type_name == "number":
            return "%g"
        if type_name == "string":
            return "%s"
        return "%d"

    def c_type(self, type_name: str) -> str:
        if type_name not in TYPE_MAP:
            raise CGeneratorError(f"Tipo nao suportado na geracao de C: '{type_name}'")
        return TYPE_MAP[type_name]

    def push_scope(self) -> None:
        self.scopes.append({})

    def pop_scope(self) -> None:
        self.scopes.pop()

    def define_variable(self, name: str, type_name: str) -> None:
        self.scopes[-1][name] = type_name

    def lookup_variable(self, name: str) -> str | None:
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        return None

    def escape_c_string(self, value: str) -> str:
        return (
            value.replace("\\", "\\\\")
            .replace('"', '\\"')
            .replace("\n", "\\n")
            .replace("\r", "\\r")
            .replace("\t", "\\t")
        )
