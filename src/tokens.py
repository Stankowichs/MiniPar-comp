from dataclasses import dataclass
from enum import Enum, auto


class TokenType(Enum):
    NUMBER = auto()
    STRING = auto()
    TRUE = auto()
    FALSE = auto()
    ID = auto()

    VAR = auto()
    FUNC = auto()
    PRINT = auto()
    PRINTLN = auto()
    INPUT = auto()
    READLN = auto()
    READNUMBER = auto()
    IF = auto()
    ELSE = auto()
    WHILE = auto()
    FOR = auto()
    DO = auto()
    RETURN = auto()
    BREAK = auto()
    CONTINUE = auto()
    CLASS = auto()
    EXTENDS = auto()
    NEW = auto()
    THIS = auto()
    SUPER = auto()

    TYPE_INT = auto()
    TYPE_NUMBER = auto()
    TYPE_STRING = auto()
    TYPE_BOOL = auto()
    TYPE_VOID = auto()
    TYPE_LIST = auto()
    TYPE_DICT = auto()

    PLUS = auto()
    MINUS = auto()
    STAR = auto()
    SLASH = auto()
    MOD = auto()

    EQUAL = auto()
    EQUAL_EQUAL = auto()
    NOT_EQUAL = auto()
    LESS = auto()
    LESS_EQUAL = auto()
    GREATER = auto()
    GREATER_EQUAL = auto()

    AND = auto()
    OR = auto()
    BANG = auto()

    LEFT_PAREN = auto()
    RIGHT_PAREN = auto()
    LEFT_BRACE = auto()
    RIGHT_BRACE = auto()
    LEFT_BRACKET = auto()
    RIGHT_BRACKET = auto()
    COMMA = auto()
    DOT = auto()
    COLON = auto()
    SEMICOLON = auto()
    ARROW = auto()

    SEQ = auto()
    PAR = auto()
    C_CHANNEL = auto()
    S_CHANNEL = auto()
    SEND = auto()
    RECEIVE = auto()
    IN = auto()

    NEWLINE = auto()
    EOF = auto()


KEYWORDS = {
    "var": TokenType.VAR,
    "func": TokenType.FUNC,
    "print": TokenType.PRINT,
    "println": TokenType.PRINTLN,
    "input": TokenType.INPUT,
    "readln": TokenType.READLN,
    "readNumber": TokenType.READNUMBER,
    "if": TokenType.IF,
    "else": TokenType.ELSE,
    "while": TokenType.WHILE,
    "for": TokenType.FOR,
    "do": TokenType.DO,
    "return": TokenType.RETURN,
    "break": TokenType.BREAK,
    "continue": TokenType.CONTINUE,
    "in": TokenType.IN,
    "class": TokenType.CLASS,
    "extends": TokenType.EXTENDS,
    "new": TokenType.NEW,
    "this": TokenType.THIS,
    "super": TokenType.SUPER,
    "int": TokenType.TYPE_INT,
    "number": TokenType.TYPE_NUMBER,
    "string": TokenType.TYPE_STRING,
    "bool": TokenType.TYPE_BOOL,
    "void": TokenType.TYPE_VOID,
    "list": TokenType.TYPE_LIST,
    "dict": TokenType.TYPE_DICT,
    "true": TokenType.TRUE,
    "false": TokenType.FALSE,
    "seq": TokenType.SEQ,
    "par": TokenType.PAR,
    "c_channel": TokenType.C_CHANNEL,
    "s_channel": TokenType.S_CHANNEL,
    "send": TokenType.SEND,
    "receive": TokenType.RECEIVE,
}


@dataclass(frozen=True)
class Token:
    type: TokenType
    lexeme: str
    line: int
    column: int

    def __repr__(self) -> str:
        return f"Token(type={self.type.name}, lexeme={self.lexeme!r}, line={self.line}, column={self.column})"
