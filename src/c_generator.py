from ast_nodes import (
    Assignment,
    ASTNode,
    BinaryExpr,
    BreakStmt,
    ClassDecl,
    ContinueStmt,
    DoWhileStmt,
    ForStmt,
    FuncDecl,
    FunctionCall,
    Identifier,
    IfStmt,
    Literal,
    MethodCall,
    MethodDecl,
    NewInstance,
    PrintStmt,
    Program,
    PropertyAccess,
    PropertyAssign,
    ReturnStmt,
    ThisExpr,
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
        self.classes: dict[str, ClassDecl] = {}
        self.function_return_types: dict[str, str] = {}
        self.method_return_types: dict[tuple[str, str], str] = {}
        self.scopes: list[dict[str, str]] = []
        self.current_return_type: str | None = None
        self.current_class_name: str | None = None

    def generate(self, program: Program) -> str:
        self.collect_declarations(program)
        class_declarations = []
        method_prototypes = []
        method_declarations = []
        function_declarations = []
        function_prototypes = []
        main_statements = []

        for statement in program.statements:
            if isinstance(statement, ClassDecl):
                class_declarations.append(self.generate_class_struct(statement))
                for method in statement.methods:
                    method_prototypes.append(self.generate_method_prototype(statement, method))
                    method_declarations.append(self.generate_method(statement, method))
            elif isinstance(statement, FuncDecl):
                function_prototypes.append(self.generate_function_prototype(statement))
                function_declarations.append(self.generate_function(statement))
            else:
                main_statements.append(statement)

        lines = [
            "#include <stdio.h>",
            "#include <stdlib.h>",
            "#include <math.h>",
            "",
        ]

        if class_declarations:
            lines.extend(class_declarations)
            lines.append("")

        prototypes = method_prototypes + function_prototypes
        if prototypes:
            lines.extend(prototypes)
            lines.append("")

        declarations = method_declarations + function_declarations
        if declarations:
            lines.extend(declarations)
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

    def collect_declarations(self, program: Program) -> None:
        for statement in program.statements:
            if isinstance(statement, FuncDecl):
                self.function_return_types[statement.name] = statement.return_type
            elif isinstance(statement, ClassDecl):
                self.classes[statement.name] = statement
                for method in statement.methods:
                    self.method_return_types[(statement.name, method.name)] = method.return_type

    def generate_class_struct(self, node: ClassDecl) -> str:
        lines = ["typedef struct {"]
        if node.attributes:
            for attribute in node.attributes:
                lines.append(f"    {self.c_type(attribute.type)} {attribute.name};")
        else:
            lines.append("    int __dummy;")
        lines.append(f"}} {node.name};")
        return "\n".join(lines)

    def generate_function(self, node: FuncDecl) -> str:
        signature = self.generate_function_signature(node)
        lines = [f"{signature} {{"]

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

    def generate_function_prototype(self, node: FuncDecl) -> str:
        return f"{self.generate_function_signature(node)};"

    def generate_function_signature(self, node: FuncDecl) -> str:
        return_type = self.c_type(node.return_type)
        params = ", ".join(f"{self.c_type(param.type)} {param.name}" for param in node.parameters)
        return f"{return_type} {node.name}({params})"

    def generate_method(self, class_node: ClassDecl, method: MethodDecl) -> str:
        signature = self.generate_method_signature(class_node, method)
        lines = [f"{signature} {{"]

        self.push_scope()
        previous_return_type = self.current_return_type
        previous_class_name = self.current_class_name
        self.current_return_type = method.return_type
        self.current_class_name = class_node.name
        try:
            lines.append("    (void)self;")
            for param in method.parameters:
                self.define_variable(param.name, param.type)
            for statement in method.body:
                lines.extend(self.generate_statement(statement, indent=1))
        finally:
            self.current_return_type = previous_return_type
            self.current_class_name = previous_class_name
            self.pop_scope()

        lines.append("}")
        return "\n".join(lines)

    def generate_method_prototype(self, class_node: ClassDecl, method: MethodDecl) -> str:
        return f"{self.generate_method_signature(class_node, method)};"

    def generate_method_signature(self, class_node: ClassDecl, method: MethodDecl) -> str:
        return_type = self.c_type(method.return_type)
        params = [f"{class_node.name}* self"]
        params.extend(f"{self.c_type(param.type)} {param.name}" for param in method.parameters)
        return f"{return_type} {class_node.name}_{method.name}({', '.join(params)})"

    def generate_statement(self, node: ASTNode, indent: int) -> list[str]:
        prefix = "    " * indent

        if isinstance(node, VarDecl):
            c_type = self.c_type(node.type)
            self.define_variable(node.name, node.type)
            if node.initializer is None:
                return [f"{prefix}{c_type} {node.name};"]
            if isinstance(node.initializer, NewInstance):
                if node.initializer.arguments:
                    return [f"{prefix}{c_type} {node.name}; /* TODO: argumentos de new ignorados */"]
                return [f"{prefix}{c_type} {node.name};"]
            return [f"{prefix}{c_type} {node.name} = {self.generate_expression(node.initializer)};"]

        if isinstance(node, Assignment):
            return [f"{prefix}{node.var_name} = {self.generate_expression(node.value)};"]

        if isinstance(node, PropertyAssign):
            target = self.generate_property_target(node.object, node.property_name)
            return [f"{prefix}{target} = {self.generate_expression(node.value)};"]

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

        if isinstance(node, DoWhileStmt):
            lines = [f"{prefix}do {{"]
            self.push_scope()
            try:
                for statement in node.body:
                    lines.extend(self.generate_statement(statement, indent + 1))
            finally:
                self.pop_scope()
            lines.append(f"{prefix}}} while ({self.generate_expression(node.condition)});")
            return lines

        if isinstance(node, ForStmt):
            raise CGeneratorError("TODO: geracao de C para ForStmt for-in ainda nao implementada.")

        if isinstance(node, BreakStmt):
            return [f"{prefix}break;"]

        if isinstance(node, ContinueStmt):
            return [f"{prefix}continue;"]

        if isinstance(node, ReturnStmt):
            if node.value is None:
                return [f"{prefix}return;"]
            return [f"{prefix}return {self.generate_expression(node.value)};"]

        if isinstance(node, (BinaryExpr, UnaryExpr, FunctionCall, Identifier, Literal)):
            return [f"{prefix}{self.generate_expression(node)};"]

        if isinstance(node, (MethodCall, PropertyAccess, NewInstance, ThisExpr)):
            return [f"{prefix}{self.generate_expression(node)};"]

        raise CGeneratorError(f"Geracao de C nao implementada para no: {type(node).__name__}")

    def generate_expression(self, node: ASTNode) -> str:
        if isinstance(node, Literal):
            return self.generate_literal(node)

        if isinstance(node, Identifier):
            return node.name

        if isinstance(node, ThisExpr):
            return "self"

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

        if isinstance(node, MethodCall):
            object_type = self.infer_type(node.object)
            if object_type is None:
                raise CGeneratorError(f"Nao foi possivel inferir o tipo do objeto para metodo '{node.method_name}'")
            receiver = self.generate_method_receiver(node.object)
            args = [receiver]
            args.extend(self.generate_expression(argument) for argument in node.arguments)
            return f"{object_type}_{node.method_name}({', '.join(args)})"

        if isinstance(node, PropertyAccess):
            return self.generate_property_target(node.object, node.property_name)

        if isinstance(node, PropertyAssign):
            target = self.generate_property_target(node.object, node.property_name)
            return f"({target} = {self.generate_expression(node.value)})"

        if isinstance(node, NewInstance):
            if node.arguments:
                raise CGeneratorError("TODO: argumentos em NewInstance ainda nao implementados.")
            return f"({node.class_name}){{0}}"

        raise CGeneratorError(f"Geracao de expressao C nao implementada para no: {type(node).__name__}")

    def generate_property_target(self, object_node: ASTNode, property_name: str) -> str:
        if isinstance(object_node, ThisExpr):
            return f"self->{property_name}"
        return f"{self.generate_expression(object_node)}.{property_name}"

    def generate_method_receiver(self, object_node: ASTNode) -> str:
        if isinstance(object_node, ThisExpr):
            return "self"
        return f"&{self.generate_expression(object_node)}"

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

        if isinstance(node, MethodCall):
            object_type = self.infer_type(node.object)
            if object_type is None:
                return None
            return self.method_return_types.get((object_type, node.method_name))

        if isinstance(node, PropertyAccess):
            object_type = self.infer_type(node.object)
            class_node = self.classes.get(object_type) if object_type else None
            if class_node is None:
                return None
            for attribute in class_node.attributes:
                if attribute.name == node.property_name:
                    return attribute.type
            return None

        if isinstance(node, ThisExpr):
            return self.current_class_name

        if isinstance(node, NewInstance):
            return node.class_name

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
        if type_name in self.classes:
            return type_name
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
