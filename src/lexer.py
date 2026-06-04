from tokens import KEYWORDS, Token, TokenType
from errors import LexerError


class Lexer:
    def __init__(self, source: str):
        self.source = source
        self.tokens: list[Token] = []
        self.start = 0
        self.current = 0
        self.line = 1
        self.column = 1
        self.start_line = 1
        self.start_column = 1

    def scan_tokens(self) -> list[Token]:
        while not self.is_at_end():
            self.start = self.current
            self.start_line = self.line
            self.start_column = self.column
            self.scan_token()
        self.tokens.append(Token(TokenType.EOF, "", self.line, self.column))
        return self.tokens

    def scan_token(self) -> None:
        c = self.advance()
        single = {
            "(": TokenType.LEFT_PAREN,
            ")": TokenType.RIGHT_PAREN,
            "{": TokenType.LEFT_BRACE,
            "}": TokenType.RIGHT_BRACE,
            "[": TokenType.LEFT_BRACKET,
            "]": TokenType.RIGHT_BRACKET,
            ",": TokenType.COMMA,
            ".": TokenType.DOT,
            ":": TokenType.COLON,
            ";": TokenType.SEMICOLON,
            "+": TokenType.PLUS,
            "%": TokenType.MOD,
            "*": TokenType.STAR,
        }
        if c in single:
            self.add_token(single[c])
            return
        if c == "-":
            self.add_token(TokenType.ARROW if self.match(">") else TokenType.MINUS)
        elif c == "/":
            if self.match("/"):
                while self.peek() != "\n" and not self.is_at_end():
                    self.advance()
            elif self.match("*"):
                self.block_comment()
            else:
                self.add_token(TokenType.SLASH)
        elif c == "#":
            while self.peek() != "\n" and not self.is_at_end():
                self.advance()
        elif c == "!":
            self.add_token(TokenType.NOT_EQUAL if self.match("=") else TokenType.BANG)
        elif c == "=":
            self.add_token(TokenType.EQUAL_EQUAL if self.match("=") else TokenType.EQUAL)
        elif c == "<":
            self.add_token(TokenType.LESS_EQUAL if self.match("=") else TokenType.LESS)
        elif c == ">":
            self.add_token(TokenType.GREATER_EQUAL if self.match("=") else TokenType.GREATER)
        elif c == "&":
            if self.match("&"):
                self.add_token(TokenType.AND)
            else:
                self.error("Esperado '&' após '&'")
        elif c == "|":
            if self.match("|"):
                self.add_token(TokenType.OR)
            else:
                self.error("Esperado '|' após '|'")
        elif c in " \r\t":
            pass
        elif c == "\n":
            pass
        elif c == '"':
            self.string()
        elif c.isdigit():
            self.number()
        elif self.is_alpha(c):
            self.identifier()
        else:
            self.error(f"Caractere inesperado: {c}")

    def block_comment(self) -> None:
        while not self.is_at_end():
            if self.peek() == "*" and self.peek_next() == "/":
                self.advance()
                self.advance()
                return
            self.advance()
        self.error("Comentário de bloco não fechado")

    def string(self) -> None:
        while self.peek() != '"' and not self.is_at_end():
            self.advance()
        if self.is_at_end():
            self.error("String não fechada")
        self.advance()
        value = self.source[self.start + 1:self.current - 1]
        self.add_token(TokenType.STRING, value)

    def number(self) -> None:
        while self.peek().isdigit():
            self.advance()
        if self.peek() == "." and self.peek_next().isdigit():
            self.advance()
            while self.peek().isdigit():
                self.advance()
        self.add_token(TokenType.NUMBER)

    def identifier(self) -> None:
        while self.is_alpha_numeric(self.peek()):
            self.advance()
        text = self.source[self.start:self.current]
        self.add_token(KEYWORDS.get(text, TokenType.ID))

    def match(self, expected: str) -> bool:
        if self.is_at_end() or self.source[self.current] != expected:
            return False
        self.advance()
        return True

    def peek(self) -> str:
        if self.is_at_end():
            return "\0"
        return self.source[self.current]

    def peek_next(self) -> str:
        if self.current + 1 >= len(self.source):
            return "\0"
        return self.source[self.current + 1]

    def advance(self) -> str:
        c = self.source[self.current]
        self.current += 1
        if c == "\n":
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        return c

    def add_token(self, token_type: TokenType, literal: str | None = None) -> None:
        text = self.source[self.start:self.current]
        self.tokens.append(Token(token_type, text if literal is None else literal, self.start_line, self.start_column))

    def is_at_end(self) -> bool:
        return self.current >= len(self.source)

    @staticmethod
    def is_alpha(c: str) -> bool:
        return c == "_" or c.isalpha()

    def is_alpha_numeric(self, c: str) -> bool:
        return self.is_alpha(c) or c.isdigit()

    def error(self, message: str) -> None:
        raise LexerError(f"[Erro Léxico] Linha {self.line}, Coluna {self.column}: {message}")
