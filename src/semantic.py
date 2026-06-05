from ast_nodes import *
from errors import SemanticError
from symbol_table import ClassSymbol, MethodSymbol, SymbolTable, VariableSymbol


BUILTIN_TYPES = {"int", "number", "string", "bool", "void", "list", "dict"}
BUILTIN_FUNCTIONS = {
    "input": None,
    "readln": 0,
    "readNumber": 0,
    "mp_fractal_init": 0,
    "mp_fractal_set": 3,
    "mp_fractal_print": 0,
}


class SemanticAnalyzer:
    def __init__(self):
        self.symbols = SymbolTable()
        self.current_function_return_type: str | None = None
        self.current_class: ClassSymbol | None = None

    def analyze(self, program: Program) -> SymbolTable:
        self.collect_declarations(program.statements)
        self.visit_program(program)
        return self.symbols

    def collect_declarations(self, statements: list[ASTNode]) -> None:
        for stmt in statements:
            if isinstance(stmt, FuncDecl):
                self.check_duplicate_global(stmt.name)
                self.symbols.define_function(stmt.name, stmt.return_type, stmt.parameters, stmt)
            elif isinstance(stmt, ClassDecl):
                self.check_duplicate_global(stmt.name)
                cls = self.symbols.define_class(stmt.name, stmt.super_class, stmt)
                for attr in stmt.attributes:
                    if attr.name in cls.attributes:
                        raise SemanticError(f"Atributo duplicado na classe '{stmt.name}': '{attr.name}'")
                    cls.attributes[attr.name] = VariableSymbol(name=attr.name, type=attr.type, node=attr)
                for method in stmt.methods:
                    if method.name in cls.methods:
                        raise SemanticError(f"Método duplicado na classe '{stmt.name}': '{method.name}'")
                    cls.methods[method.name] = MethodSymbol(
                        name=method.name,
                        return_type=method.return_type,
                        parameters=method.parameters,
                        node=method,
                    )

    def check_duplicate_global(self, name: str) -> None:
        if self.symbols.lookup_global(name) is not None:
            raise SemanticError(f"Símbolo duplicado no escopo global: '{name}'")

    def check_type_exists(self, type_name: str | None) -> None:
        if not type_name or type_name in BUILTIN_TYPES:
            return
        symbol = self.symbols.lookup_global(type_name)
        if not isinstance(symbol, ClassSymbol):
            raise SemanticError(f"Tipo ou classe inexistente: '{type_name}'")

    def visit_program(self, node: Program) -> None:
        for stmt in node.statements:
            self.visit(stmt)

    def visit_block(self, statements: list[ASTNode], name: str = "block") -> None:
        self.symbols.push_scope(name)
        try:
            for stmt in statements:
                self.visit(stmt)
        finally:
            self.symbols.pop_scope()

    def visit(self, node: ASTNode | None):
        if node is None:
            return None
        method = getattr(self, f"visit_{type(node).__name__}", None)
        if method is None:
            raise SemanticError(f"Análise semântica não implementada para nó: {type(node).__name__}")
        return method(node)

    def visit_VarDecl(self, node: VarDecl):
        self.check_type_exists(node.type)
        self.symbols.define_variable(node.name, node.type, node)
        if node.initializer is not None:
            self.visit(node.initializer)

    def visit_FuncDecl(self, node: FuncDecl):
        self.check_type_exists(node.return_type)
        self.symbols.push_scope(f"func {node.name}")
        previous_return = self.current_function_return_type
        self.current_function_return_type = node.return_type
        try:
            seen = set()
            for param in node.parameters:
                self.check_type_exists(param.type)
                if param.name in seen:
                    raise SemanticError(f"Parâmetro duplicado na função '{node.name}': '{param.name}'")
                seen.add(param.name)
                self.symbols.define_variable(param.name, param.type, param)
            for stmt in node.body:
                self.visit(stmt)
        finally:
            self.current_function_return_type = previous_return
            self.symbols.pop_scope()

    def visit_ClassDecl(self, node: ClassDecl):
        if node.super_class is not None:
            super_symbol = self.symbols.lookup_global(node.super_class)
            if not isinstance(super_symbol, ClassSymbol):
                raise SemanticError(f"Superclasse inexistente: '{node.super_class}'")
        cls = self.symbols.lookup_global(node.name)
        if not isinstance(cls, ClassSymbol):
            raise SemanticError(f"Classe inexistente: '{node.name}'")
        previous_class = self.current_class
        self.current_class = cls
        self.symbols.push_scope(f"class {node.name}")
        try:
            self.symbols.define_variable("this", node.name, node)
            for attr in node.attributes:
                self.check_type_exists(attr.type)
                if attr.initializer is not None:
                    self.visit(attr.initializer)
            for method in node.methods:
                self.visit(method)
        finally:
            self.symbols.pop_scope()
            self.current_class = previous_class

    def visit_MethodDecl(self, node: MethodDecl):
        self.check_type_exists(node.return_type)
        self.symbols.push_scope(f"method {node.name}")
        previous_return = self.current_function_return_type
        self.current_function_return_type = node.return_type
        try:
            seen = set()
            for param in node.parameters:
                self.check_type_exists(param.type)
                if param.name in seen:
                    raise SemanticError(f"Parâmetro duplicado no método '{node.name}': '{param.name}'")
                seen.add(param.name)
                self.symbols.define_variable(param.name, param.type, param)
            for stmt in node.body:
                self.visit(stmt)
        finally:
            self.current_function_return_type = previous_return
            self.symbols.pop_scope()

    def visit_CanalDecl(self, node: CanalDecl):
        for name in node.nomes:
            self.symbols.define_variable(name, "c_channel", node)

    def visit_Assignment(self, node: Assignment):
        if self.symbols.lookup(node.var_name) is None:
            raise SemanticError(f"Variável não declarada: '{node.var_name}'")
        self.visit(node.value)

    def visit_Identifier(self, node: Identifier):
        if self.symbols.lookup(node.name) is None:
            raise SemanticError(f"Variável não declarada: '{node.name}'")
        return self.symbols.lookup(node.name).type

    def visit_Literal(self, node: Literal):
        if isinstance(node.value, bool): return "bool"
        if isinstance(node.value, int): return "int"
        if isinstance(node.value, float): return "number"
        if isinstance(node.value, str): return "string"
        return None

    def visit_BinaryExpr(self, node: BinaryExpr):
        self.visit(node.left)
        self.visit(node.right)

    def visit_UnaryExpr(self, node: UnaryExpr):
        self.visit(node.operand)

    def visit_IfStmt(self, node: IfStmt):
        self.visit(node.condition)
        self.visit_block(node.then_branch, "if")
        if node.else_branch is not None:
            self.visit_block(node.else_branch, "else")

    def visit_WhileStmt(self, node: WhileStmt):
        self.visit(node.condition)
        self.visit_block(node.body, "while")

    def visit_DoWhileStmt(self, node: DoWhileStmt):
        self.visit_block(node.body, "do")
        self.visit(node.condition)

    def visit_ForStmt(self, node: ForStmt):
        self.visit(node.iterable)
        self.symbols.push_scope("for")
        try:
            self.visit_VarDecl(node.variable)
            for stmt in node.body:
                self.visit(stmt)
        finally:
            self.symbols.pop_scope()

    def visit_PrintStmt(self, node: PrintStmt):
        for arg in node.arguments:
            self.visit(arg)

    def visit_ReturnStmt(self, node: ReturnStmt):
        if self.current_function_return_type is None:
            raise SemanticError("'return' fora de função ou método")
        if node.value is not None:
            self.visit(node.value)

    def visit_FunctionCall(self, node: FunctionCall):
        if node.function_name in BUILTIN_FUNCTIONS:
            expected_arguments = BUILTIN_FUNCTIONS[node.function_name]
            if expected_arguments is not None and len(node.arguments) != expected_arguments:
                raise SemanticError(
                    f"Quantidade errada de argumentos em '{node.function_name}': "
                    f"esperado {expected_arguments}, recebido {len(node.arguments)}"
                )
            for arg in node.arguments:
                self.visit(arg)
            return
        symbol = self.symbols.lookup_global(node.function_name)
        if symbol is None or symbol.kind != "function":
            raise SemanticError(f"Função inexistente: '{node.function_name}'")
        self.check_argument_count(node.function_name, symbol.parameters, node.arguments)
        for arg in node.arguments:
            self.visit(arg)

    def visit_NewInstance(self, node: NewInstance):
        cls = self.symbols.lookup_global(node.class_name)
        if not isinstance(cls, ClassSymbol):
            raise SemanticError(f"Classe inexistente: '{node.class_name}'")
        constructor = cls.methods.get(node.class_name)
        if constructor is not None:
            self.check_argument_count(f"construtor {node.class_name}", constructor.parameters, node.arguments)
        for arg in node.arguments:
            self.visit(arg)
        return node.class_name

    def visit_MethodCall(self, node: MethodCall):
        object_type = self.visit(node.object)
        cls = self.symbols.lookup_global(object_type) if object_type else None
        if isinstance(cls, ClassSymbol):
            method = cls.methods.get(node.method_name)
            if method is None:
                raise SemanticError(f"Método inexistente: '{node.method_name}' na classe '{object_type}'")
            self.check_argument_count(node.method_name, method.parameters, node.arguments)
        for arg in node.arguments:
            self.visit(arg)

    def visit_PropertyAccess(self, node: PropertyAccess):
        object_type = self.visit(node.object)
        cls = self.symbols.lookup_global(object_type) if object_type else None
        if isinstance(cls, ClassSymbol) and node.property_name not in cls.attributes:
            raise SemanticError(f"Atributo inexistente: '{node.property_name}' na classe '{object_type}'")
        if isinstance(cls, ClassSymbol):
            return cls.attributes[node.property_name].type
        return None

    def visit_PropertyAssign(self, node: PropertyAssign):
        self.visit_PropertyAccess(PropertyAccess(node.object, node.property_name))
        self.visit(node.value)

    def visit_SeqBlock(self, node: SeqBlock):
        self.visit_block(node.statements, "seq")

    def visit_ParBlock(self, node: ParBlock):
        self.visit_block(node.statements, "par")

    def visit_SendStmt(self, node: SendStmt):
        self.visit(node.channel)
        for arg in node.arguments:
            self.visit(arg)

    def visit_ReceiveStmt(self, node: ReceiveStmt):
        self.visit(node.channel)
        for arg in node.arguments:
            self.visit(arg)

    def visit_InputExpr(self, node: InputExpr):
        if node.prompt is not None:
            self.visit(node.prompt)
        return "string"

    def visit_ReadlnExpr(self, node: ReadlnExpr): return "string"
    def visit_ReadNumberExpr(self, node: ReadNumberExpr): return "number"
    def visit_ThisExpr(self, node: ThisExpr):
        if self.current_class is None:
            raise SemanticError("'this' fora de classe")
        return self.current_class.name

    def visit_SuperCall(self, node: SuperCall):
        for arg in node.arguments:
            self.visit(arg)

    def visit_ListLiteral(self, node: ListLiteral):
        for elem in node.elements: self.visit(elem)
        return "list"

    def visit_DictLiteral(self, node: DictLiteral):
        for entry in node.entries:
            self.visit(entry.key)
            self.visit(entry.value)
        return "dict"

    def visit_IndexExpr(self, node: IndexExpr):
        self.visit(node.target)
        self.visit(node.index)

    def visit_IndexAssign(self, node: IndexAssign):
        self.visit(node.target)
        self.visit(node.index)
        self.visit(node.value)

    def visit_BreakStmt(self, node: BreakStmt): pass
    def visit_ContinueStmt(self, node: ContinueStmt): pass
    def visit_Program(self, node: Program): self.visit_block(node.statements, "anonymous")

    def check_argument_count(self, name: str, parameters: list[Parameter], arguments: list[ASTNode]) -> None:
        if len(parameters) != len(arguments):
            raise SemanticError(
                f"Quantidade errada de argumentos em '{name}': esperado {len(parameters)}, recebido {len(arguments)}"
            )
