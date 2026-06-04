from dataclasses import dataclass, field
from typing import Any
from errors import SemanticError


@dataclass
class Symbol:
    name: str
    kind: str
    type: str | None = None
    node: Any = None


@dataclass
class VariableSymbol(Symbol):
    kind: str = "variable"


@dataclass
class FunctionSymbol(Symbol):
    parameters: list[Any] = field(default_factory=list)
    return_type: str | None = None
    kind: str = "function"

    def __post_init__(self) -> None:
        self.type = self.return_type


@dataclass
class MethodSymbol(Symbol):
    parameters: list[Any] = field(default_factory=list)
    return_type: str | None = None
    kind: str = "method"

    def __post_init__(self) -> None:
        self.type = self.return_type


@dataclass
class ClassSymbol(Symbol):
    super_class: str | None = None
    attributes: dict[str, VariableSymbol] = field(default_factory=dict)
    methods: dict[str, MethodSymbol] = field(default_factory=dict)
    kind: str = "class"


class Scope:
    def __init__(self, parent: "Scope | None" = None, name: str = "scope"):
        self.parent = parent
        self.name = name
        self.symbols: dict[str, Symbol] = {}

    def define(self, symbol: Symbol) -> None:
        if symbol.name in self.symbols:
            raise SemanticError(f"Símbolo duplicado no mesmo escopo: '{symbol.name}'")
        self.symbols[symbol.name] = symbol

    def lookup_local(self, name: str) -> Symbol | None:
        return self.symbols.get(name)

    def lookup(self, name: str) -> Symbol | None:
        scope: Scope | None = self
        while scope is not None:
            if name in scope.symbols:
                return scope.symbols[name]
            scope = scope.parent
        return None


class SymbolTable:
    def __init__(self):
        self.global_scope = Scope(name="global")
        self.current_scope = self.global_scope

    def push_scope(self, name: str = "scope") -> Scope:
        self.current_scope = Scope(parent=self.current_scope, name=name)
        return self.current_scope

    def pop_scope(self) -> None:
        if self.current_scope.parent is None:
            raise SemanticError("Tentativa de sair do escopo global")
        self.current_scope = self.current_scope.parent

    def define(self, symbol: Symbol) -> None:
        self.current_scope.define(symbol)

    def define_variable(self, name: str, type_name: str | None = None, node: Any = None) -> VariableSymbol:
        symbol = VariableSymbol(name=name, type=type_name, node=node)
        self.define(symbol)
        return symbol

    def define_function(self, name: str, return_type: str, parameters: list[Any], node: Any = None) -> FunctionSymbol:
        symbol = FunctionSymbol(name=name, return_type=return_type, parameters=parameters, node=node)
        self.define(symbol)
        return symbol

    def define_class(self, name: str, super_class: str | None = None, node: Any = None) -> ClassSymbol:
        symbol = ClassSymbol(name=name, type=name, super_class=super_class, node=node)
        self.define(symbol)
        return symbol

    def lookup(self, name: str) -> Symbol | None:
        return self.current_scope.lookup(name)

    def lookup_global(self, name: str) -> Symbol | None:
        return self.global_scope.lookup_local(name)

    def require(self, name: str, kind: str | None = None) -> Symbol:
        symbol = self.lookup(name)
        if symbol is None:
            raise SemanticError(f"Símbolo não declarado: '{name}'")
        if kind is not None and symbol.kind != kind:
            raise SemanticError(f"Símbolo '{name}' não é do tipo esperado: {kind}")
        return symbol
