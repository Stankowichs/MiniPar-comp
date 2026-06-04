from dataclasses import dataclass, field
from typing import Any


class ASTNode:
    pass


@dataclass
class Program(ASTNode):
    statements: list[ASTNode] = field(default_factory=list)


@dataclass
class Parameter:
    name: str
    type: str


@dataclass
class VarDecl(ASTNode):
    name: str
    type: str
    initializer: ASTNode | None = None


@dataclass
class FuncDecl(ASTNode):
    name: str
    return_type: str
    parameters: list[Parameter]
    body: list[ASTNode]

    @property
    def returnType(self) -> str:
        return self.return_type


@dataclass
class MethodDecl(ASTNode):
    return_type: str
    name: str
    parameters: list[Parameter]
    body: list[ASTNode]

    @property
    def returnType(self) -> str:
        return self.return_type


@dataclass
class ClassDecl(ASTNode):
    name: str
    super_class: str | None
    attributes: list[VarDecl]
    methods: list[MethodDecl]

    @property
    def superClass(self) -> str | None:
        return self.super_class


@dataclass
class Assignment(ASTNode):
    var_name: str
    value: ASTNode

    @property
    def varName(self) -> str:
        return self.var_name


@dataclass
class BinaryExpr(ASTNode):
    left: ASTNode
    operator: str
    right: ASTNode


@dataclass
class UnaryExpr(ASTNode):
    operator: str
    operand: ASTNode


@dataclass
class Literal(ASTNode):
    value: Any


@dataclass
class Identifier(ASTNode):
    name: str


@dataclass
class IfStmt(ASTNode):
    condition: ASTNode
    then_branch: list[ASTNode]
    else_branch: list[ASTNode] | None = None

    @property
    def thenBranch(self) -> list[ASTNode]:
        return self.then_branch

    @property
    def elseBranch(self) -> list[ASTNode] | None:
        return self.else_branch


@dataclass
class WhileStmt(ASTNode):
    condition: ASTNode
    body: list[ASTNode]


@dataclass
class DoWhileStmt(ASTNode):
    body: list[ASTNode]
    condition: ASTNode


@dataclass
class ForStmt(ASTNode):
    variable: VarDecl
    iterable: ASTNode
    body: list[ASTNode]


@dataclass
class PrintStmt(ASTNode):
    arguments: list[ASTNode]
    newline: bool = False


@dataclass
class ReturnStmt(ASTNode):
    value: ASTNode | None = None


@dataclass
class BreakStmt(ASTNode):
    pass


@dataclass
class ContinueStmt(ASTNode):
    pass


@dataclass
class FunctionCall(ASTNode):
    function_name: str
    arguments: list[ASTNode]

    @property
    def functionName(self) -> str:
        return self.function_name


@dataclass
class MethodCall(ASTNode):
    object: ASTNode
    method_name: str
    arguments: list[ASTNode]

    @property
    def methodName(self) -> str:
        return self.method_name


@dataclass
class PropertyAccess(ASTNode):
    object: ASTNode
    property_name: str

    @property
    def propertyName(self) -> str:
        return self.property_name


@dataclass
class PropertyAssign(ASTNode):
    object: ASTNode
    property_name: str
    value: ASTNode

    @property
    def propertyName(self) -> str:
        return self.property_name


@dataclass
class NewInstance(ASTNode):
    class_name: str
    arguments: list[ASTNode]

    @property
    def className(self) -> str:
        return self.class_name


@dataclass
class SeqBlock(ASTNode):
    statements: list[ASTNode]


@dataclass
class ParBlock(ASTNode):
    statements: list[ASTNode]


@dataclass
class CanalDecl(ASTNode):
    nomes: list[str]


@dataclass
class SendStmt(ASTNode):
    channel: ASTNode
    arguments: list[ASTNode]


@dataclass
class ReceiveStmt(ASTNode):
    channel: ASTNode
    arguments: list[ASTNode]


@dataclass
class InputExpr(ASTNode):
    prompt: ASTNode | None = None


@dataclass
class ReadlnExpr(ASTNode):
    pass


@dataclass
class ReadNumberExpr(ASTNode):
    pass


@dataclass
class ThisExpr(ASTNode):
    pass


@dataclass
class SuperCall(ASTNode):
    arguments: list[ASTNode]


@dataclass
class ListLiteral(ASTNode):
    elements: list[ASTNode]


@dataclass
class DictEntry:
    key: ASTNode
    value: ASTNode


@dataclass
class DictLiteral(ASTNode):
    entries: list[DictEntry]


@dataclass
class IndexExpr(ASTNode):
    target: ASTNode
    index: ASTNode


@dataclass
class IndexAssign(ASTNode):
    target: ASTNode
    index: ASTNode
    value: ASTNode
