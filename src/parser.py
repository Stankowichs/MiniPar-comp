from tokens import Token, TokenType
from errors import ParseError
from ast_nodes import *


class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.current = 0

    def parse(self) -> Program:
        statements = []
        while not self.is_at_end():
            statements.append(self.declaration())
        return Program(statements)

    def declaration(self) -> ASTNode:
        if self.match(TokenType.CLASS):
            return self.class_declaration()
        if self.match(TokenType.FUNC):
            return self.function_declaration()
        if self.match(TokenType.C_CHANNEL):
            return self.channel_declaration()
        if self.is_var_decl_start():
            return self.var_declaration()
        return self.statement()

    def class_declaration(self) -> ClassDecl:
        name = self.consume(TokenType.ID, "Esperado nome da classe").lexeme
        super_class = None
        if self.match(TokenType.EXTENDS):
            super_class = self.consume(TokenType.ID, "Esperado nome da superclasse").lexeme
        self.consume(TokenType.LEFT_BRACE, "Esperado '{' após declaração da classe")
        attributes, methods = [], []
        while not self.check(TokenType.RIGHT_BRACE) and not self.is_at_end():
            if self.is_var_decl_start():
                attributes.append(self.var_declaration())
            elif self.is_constructor_start(name):
                methods.append(self.constructor_declaration(name))
            elif self.is_method_start():
                methods.append(self.method_declaration())
            else:
                raise self.error(self.peek(), "Esperado declaração de método ou atributo")
        self.consume(TokenType.RIGHT_BRACE, "Esperado '}' após corpo da classe")
        return ClassDecl(name, super_class, attributes, methods)

    def constructor_declaration(self, class_name: str) -> MethodDecl:
        self.advance()
        self.consume(TokenType.LEFT_PAREN, "Esperado '(' após nome do construtor")
        params = self.parameters()
        self.consume(TokenType.RIGHT_PAREN, "Esperado ')' após parâmetros")
        self.consume(TokenType.LEFT_BRACE, "Esperado '{' antes do corpo do construtor")
        body = self.block()
        self.consume(TokenType.RIGHT_BRACE, "Esperado '}' após corpo do construtor")
        return MethodDecl(class_name, class_name, params, body)

    def method_declaration(self) -> MethodDecl:
        return_type = self.advance().lexeme
        name = self.consume(TokenType.ID, "Esperado nome do método").lexeme
        self.consume(TokenType.LEFT_PAREN, "Esperado '(' após nome do método")
        params = self.parameters()
        self.consume(TokenType.RIGHT_PAREN, "Esperado ')' após parâmetros")
        self.consume(TokenType.LEFT_BRACE, "Esperado '{' antes do corpo do método")
        body = self.block()
        self.consume(TokenType.RIGHT_BRACE, "Esperado '}' após corpo do método")
        return MethodDecl(return_type, name, params, body)

    def function_declaration(self) -> FuncDecl:
        name = self.consume(TokenType.ID, "Esperado nome da função").lexeme
        self.consume(TokenType.LEFT_PAREN, "Esperado '(' após nome da função")
        params = self.parameters()
        self.consume(TokenType.RIGHT_PAREN, "Esperado ')' após parâmetros")
        self.consume(TokenType.ARROW, "Esperado '->' após parâmetros da função")
        return_type = self.consume_type_token_or_id("Esperado tipo de retorno").lexeme
        self.consume(TokenType.LEFT_BRACE, "Esperado '{' antes do corpo da função")
        body = self.block()
        self.consume(TokenType.RIGHT_BRACE, "Esperado '}' após corpo da função")
        return FuncDecl(name, return_type, params, body)

    def parameters(self) -> list[Parameter]:
        params = []
        if not self.check(TokenType.RIGHT_PAREN):
            while True:
                type_token = self.consume_type_token_or_id("Esperado tipo do parâmetro")
                name_token = self.consume(TokenType.ID, "Esperado nome do parâmetro")
                params.append(Parameter(name_token.lexeme, type_token.lexeme))
                if not self.match(TokenType.COMMA):
                    break
        return params

    def var_declaration(self) -> VarDecl:
        type_name = self.advance().lexeme
        name = self.consume(TokenType.ID, "Esperado nome da variável").lexeme
        initializer = self.expression() if self.match(TokenType.EQUAL) else None
        self.consume(TokenType.SEMICOLON, "Esperado ';' ao final da declaração de variável")
        return VarDecl(name, type_name, initializer)

    def channel_declaration(self) -> CanalDecl:
        names = []
        if self.match(TokenType.LEFT_PAREN):
            if not self.check(TokenType.RIGHT_PAREN):
                while True:
                    names.append(self.consume(TokenType.ID, "Esperado nome do canal").lexeme)
                    if not self.match(TokenType.COMMA):
                        break
            self.consume(TokenType.RIGHT_PAREN, "Esperado ')' após nomes dos canais")
        else:
            names.append(self.consume(TokenType.ID, "Esperado nome do canal").lexeme)
            names.append(self.consume(TokenType.ID, "Esperado identificador do primeiro componente").lexeme)
            names.append(self.consume(TokenType.ID, "Esperado identificador do segundo componente").lexeme)
        self.consume(TokenType.SEMICOLON, "Esperado ';' ao final da declaração de canal")
        return CanalDecl(names)

    def statement(self) -> ASTNode:
        if self.match(TokenType.IF): return self.if_statement()
        if self.match(TokenType.WHILE): return self.while_statement()
        if self.match(TokenType.DO): return self.do_while_statement()
        if self.match(TokenType.FOR): return self.for_statement()
        if self.match(TokenType.PRINT): return self.print_statement(False)
        if self.match(TokenType.PRINTLN): return self.print_statement(True)
        if self.match(TokenType.RETURN): return self.return_statement()
        if self.match(TokenType.BREAK):
            self.consume(TokenType.SEMICOLON, "Esperado ';' após break")
            return BreakStmt()
        if self.match(TokenType.CONTINUE):
            self.consume(TokenType.SEMICOLON, "Esperado ';' após continue")
            return ContinueStmt()
        if self.match(TokenType.SEQ): return self.seq_block()
        if self.match(TokenType.PAR): return self.par_block()
        if self.match(TokenType.LEFT_BRACE):
            stmts = self.block()
            self.consume(TokenType.RIGHT_BRACE, "Esperado '}' após bloco")
            return Program(stmts)
        return self.expression_statement()

    def if_statement(self) -> IfStmt:
        self.consume(TokenType.LEFT_PAREN, "Esperado '(' após 'if'")
        condition = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Esperado ')' após condição")
        self.consume(TokenType.LEFT_BRACE, "Esperado '{' após condição do if")
        then_branch = self.block()
        self.consume(TokenType.RIGHT_BRACE, "Esperado '}' após bloco then")
        else_branch = None
        if self.match(TokenType.ELSE):
            if self.match(TokenType.IF):
                else_branch = [self.if_statement()]
            else:
                self.consume(TokenType.LEFT_BRACE, "Esperado '{' após else")
                else_branch = self.block()
                self.consume(TokenType.RIGHT_BRACE, "Esperado '}' após bloco else")
        return IfStmt(condition, then_branch, else_branch)

    def while_statement(self) -> WhileStmt:
        self.consume(TokenType.LEFT_PAREN, "Esperado '(' após 'while'")
        condition = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Esperado ')' após condição")
        self.consume(TokenType.LEFT_BRACE, "Esperado '{' após condição do while")
        body = self.block()
        self.consume(TokenType.RIGHT_BRACE, "Esperado '}' após corpo do while")
        return WhileStmt(condition, body)

    def do_while_statement(self) -> DoWhileStmt:
        self.consume(TokenType.LEFT_BRACE, "Esperado '{' após 'do'")
        body = self.block()
        self.consume(TokenType.RIGHT_BRACE, "Esperado '}' após corpo do 'do'")
        self.consume(TokenType.WHILE, "Esperado 'while' após bloco do 'do'")
        self.consume(TokenType.LEFT_PAREN, "Esperado '(' após 'while'")
        condition = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Esperado ')' após condição")
        self.consume(TokenType.SEMICOLON, "Esperado ';' após do-while")
        return DoWhileStmt(body, condition)

    def for_statement(self) -> ForStmt:
        self.consume(TokenType.LEFT_PAREN, "Esperado '(' após 'for'")
        type_name = self.consume_type_token_or_id("Esperado tipo no for").lexeme
        name = self.consume(TokenType.ID, "Esperado nome da variável do for").lexeme
        variable = VarDecl(name, type_name, None)
        self.consume(TokenType.IN, "Esperado 'in' no for")
        iterable = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Esperado ')' após cláusula do for")
        self.consume(TokenType.LEFT_BRACE, "Esperado '{' após for")
        body = self.block()
        self.consume(TokenType.RIGHT_BRACE, "Esperado '}' após corpo do for")
        return ForStmt(variable, iterable, body)

    def print_statement(self, newline: bool) -> PrintStmt:
        self.consume(TokenType.LEFT_PAREN, "Esperado '(' após print/println")
        args = []
        if not self.check(TokenType.RIGHT_PAREN):
            while True:
                args.append(self.expression())
                if not self.match(TokenType.COMMA): break
        self.consume(TokenType.RIGHT_PAREN, "Esperado ')' após argumentos de print")
        self.consume(TokenType.SEMICOLON, "Esperado ';' ao final do print")
        return PrintStmt(args, newline)

    def return_statement(self) -> ReturnStmt:
        value = None if self.check(TokenType.SEMICOLON) else self.expression()
        self.consume(TokenType.SEMICOLON, "Esperado ';' ao final da instrução de retorno")
        return ReturnStmt(value)

    def seq_block(self) -> SeqBlock:
        self.consume(TokenType.LEFT_BRACE, "Esperado '{' após 'seq'")
        stmts = self.block()
        self.consume(TokenType.RIGHT_BRACE, "Esperado '}' após bloco seq")
        return SeqBlock(stmts)

    def par_block(self) -> ParBlock:
        self.consume(TokenType.LEFT_BRACE, "Esperado '{' após 'par'")
        stmts = self.block()
        self.consume(TokenType.RIGHT_BRACE, "Esperado '}' após bloco par")
        return ParBlock(stmts)

    def block(self) -> list[ASTNode]:
        stmts = []
        while not self.check(TokenType.RIGHT_BRACE) and not self.is_at_end():
            stmts.append(self.declaration())
        return stmts

    def expression_statement(self) -> ASTNode:
        expr = self.expression()
        self.consume(TokenType.SEMICOLON, "Esperado ';' ao final da instrução")
        return expr

    def expression(self) -> ASTNode: return self.assignment()

    def assignment(self) -> ASTNode:
        expr = self.logic_or()
        if self.match(TokenType.EQUAL):
            value = self.assignment()
            if isinstance(expr, Identifier): return Assignment(expr.name, value)
            if isinstance(expr, PropertyAccess): return PropertyAssign(expr.object, expr.property_name, value)
            if isinstance(expr, IndexExpr): return IndexAssign(expr.target, expr.index, value)
            raise self.error(self.previous(), "Alvo de atribuição inválido")
        return expr

    def logic_or(self):
        expr = self.logic_and()
        while self.match(TokenType.OR): expr = BinaryExpr(expr, self.previous().lexeme, self.logic_and())
        return expr

    def logic_and(self):
        expr = self.equality()
        while self.match(TokenType.AND): expr = BinaryExpr(expr, self.previous().lexeme, self.equality())
        return expr

    def equality(self):
        expr = self.comparison()
        while self.match(TokenType.EQUAL_EQUAL, TokenType.NOT_EQUAL): expr = BinaryExpr(expr, self.previous().lexeme, self.comparison())
        return expr

    def comparison(self):
        expr = self.term()
        while self.match(TokenType.GREATER, TokenType.GREATER_EQUAL, TokenType.LESS, TokenType.LESS_EQUAL): expr = BinaryExpr(expr, self.previous().lexeme, self.term())
        return expr

    def term(self):
        expr = self.factor()
        while self.match(TokenType.PLUS, TokenType.MINUS): expr = BinaryExpr(expr, self.previous().lexeme, self.factor())
        return expr

    def factor(self):
        expr = self.unary()
        while self.match(TokenType.STAR, TokenType.SLASH, TokenType.MOD): expr = BinaryExpr(expr, self.previous().lexeme, self.unary())
        return expr

    def unary(self):
        if self.match(TokenType.BANG, TokenType.MINUS): return UnaryExpr(self.previous().lexeme, self.unary())
        return self.call()

    def call(self):
        expr = self.primary()
        while True:
            if self.match(TokenType.LEFT_PAREN):
                expr = self.finish_call(expr)
            elif self.match(TokenType.DOT):
                if self.match(TokenType.ID, TokenType.SEND, TokenType.RECEIVE):
                    name = self.previous().lexeme
                else:
                    raise self.error(self.peek(), "Esperado nome do método/propriedade após '.'")
                if name in ("send", "receive"):
                    self.consume(TokenType.LEFT_PAREN, f"Esperado '(' após '{name}'")
                    args = self.arguments()
                    self.consume(TokenType.RIGHT_PAREN, "Esperado ')' após argumentos")
                    expr = SendStmt(expr, args) if name == "send" else ReceiveStmt(expr, args)
                elif self.match(TokenType.LEFT_PAREN):
                    args = self.arguments()
                    self.consume(TokenType.RIGHT_PAREN, "Esperado ')' após argumentos")
                    expr = MethodCall(expr, name, args)
                else:
                    expr = PropertyAccess(expr, name)
            elif self.match(TokenType.LEFT_BRACKET):
                index = self.expression()
                self.consume(TokenType.RIGHT_BRACKET, "Esperado ']' após índice")
                expr = IndexExpr(expr, index)
            else:
                break
        return expr

    def finish_call(self, callee: ASTNode) -> FunctionCall:
        args = self.arguments()
        self.consume(TokenType.RIGHT_PAREN, "Esperado ')' após argumentos")
        if isinstance(callee, Identifier): return FunctionCall(callee.name, args)
        raise self.error(self.previous(), "Chamada inválida")

    def arguments(self) -> list[ASTNode]:
        args = []
        if not self.check(TokenType.RIGHT_PAREN):
            while True:
                args.append(self.expression())
                if not self.match(TokenType.COMMA): break
        return args

    def primary(self) -> ASTNode:
        if self.match(TokenType.TRUE): return Literal(True)
        if self.match(TokenType.FALSE): return Literal(False)
        if self.match(TokenType.THIS): return ThisExpr()
        if self.match(TokenType.SUPER):
            self.consume(TokenType.LEFT_PAREN, "Esperado '(' após 'super'")
            args = self.arguments()
            self.consume(TokenType.RIGHT_PAREN, "Esperado ')' após argumentos de 'super'")
            return SuperCall(args)
        if self.match(TokenType.NUMBER):
            x = self.previous().lexeme
            return Literal(float(x) if "." in x else int(x))
        if self.match(TokenType.STRING): return Literal(self.previous().lexeme)
        if self.match(TokenType.INPUT):
            prompt = None
            if self.match(TokenType.LEFT_PAREN):
                if not self.check(TokenType.RIGHT_PAREN): prompt = self.expression()
                self.consume(TokenType.RIGHT_PAREN, "Esperado ')' após input")
            return InputExpr(prompt)
        if self.match(TokenType.READLN):
            self.consume(TokenType.LEFT_PAREN, "Esperado '(' após readln")
            self.consume(TokenType.RIGHT_PAREN, "Esperado ')' após readln")
            return ReadlnExpr()
        if self.match(TokenType.READNUMBER):
            self.consume(TokenType.LEFT_PAREN, "Esperado '(' após readNumber")
            self.consume(TokenType.RIGHT_PAREN, "Esperado ')' após readNumber")
            return ReadNumberExpr()
        if self.match(TokenType.NEW):
            class_name = self.consume(TokenType.ID, "Esperado nome da classe após 'new'").lexeme
            self.consume(TokenType.LEFT_PAREN, "Esperado '(' após nome da classe")
            args = self.arguments()
            self.consume(TokenType.RIGHT_PAREN, "Esperado ')' após argumentos do construtor")
            return NewInstance(class_name, args)
        if self.match(TokenType.LEFT_BRACKET):
            elems = []
            if not self.check(TokenType.RIGHT_BRACKET):
                while True:
                    elems.append(self.expression())
                    if not self.match(TokenType.COMMA): break
            self.consume(TokenType.RIGHT_BRACKET, "Esperado ']' após literal de lista")
            return ListLiteral(elems)
        if self.match(TokenType.LEFT_BRACE):
            entries = []
            if not self.check(TokenType.RIGHT_BRACE):
                while True:
                    key = self.expression()
                    self.consume(TokenType.COLON, "Esperado ':' entre chave e valor no dicionário")
                    entries.append(DictEntry(key, self.expression()))
                    if not self.match(TokenType.COMMA): break
            self.consume(TokenType.RIGHT_BRACE, "Esperado '}' após literal de dicionário")
            return DictLiteral(entries)
        if self.match(TokenType.ID): return Identifier(self.previous().lexeme)
        if self.match(TokenType.LEFT_PAREN):
            expr = self.expression()
            self.consume(TokenType.RIGHT_PAREN, "Esperado ')' após expressão")
            return expr
        raise self.error(self.peek(), "Esperado expressão")

    def match(self, *types: TokenType) -> bool:
        if any(self.check(t) for t in types):
            self.advance()
            return True
        return False

    def check(self, token_type: TokenType) -> bool:
        return not self.is_at_end() and self.peek().type == token_type

    def advance(self) -> Token:
        if not self.is_at_end(): self.current += 1
        return self.previous()

    def is_at_end(self) -> bool:
        return self.peek().type == TokenType.EOF

    def peek(self) -> Token: return self.tokens[self.current]
    def previous(self) -> Token: return self.tokens[self.current - 1]

    def consume(self, token_type: TokenType, message: str) -> Token:
        if self.check(token_type): return self.advance()
        raise self.error(self.peek(), message)

    def consume_type_token_or_id(self, message: str) -> Token:
        if self.is_type_token_or_id(self.peek().type): return self.advance()
        raise self.error(self.peek(), message)

    def is_type_token_or_id(self, token_type: TokenType) -> bool:
        return token_type in {TokenType.TYPE_INT, TokenType.TYPE_NUMBER, TokenType.TYPE_STRING, TokenType.TYPE_BOOL,
                              TokenType.TYPE_VOID, TokenType.TYPE_LIST, TokenType.TYPE_DICT, TokenType.ID}

    def is_var_decl_start(self) -> bool:
        return (self.is_type_token_or_id(self.peek().type)
                and self.current + 1 < len(self.tokens) and self.tokens[self.current + 1].type == TokenType.ID
                and self.current + 2 < len(self.tokens) and self.tokens[self.current + 2].type in {TokenType.EQUAL, TokenType.SEMICOLON})

    def is_method_start(self) -> bool:
        return (self.is_type_token_or_id(self.peek().type)
                and self.current + 2 < len(self.tokens)
                and self.tokens[self.current + 1].type == TokenType.ID
                and self.tokens[self.current + 2].type == TokenType.LEFT_PAREN)

    def is_constructor_start(self, class_name: str) -> bool:
        return (self.peek().type == TokenType.ID and self.peek().lexeme == class_name
                and self.current + 1 < len(self.tokens)
                and self.tokens[self.current + 1].type == TokenType.LEFT_PAREN)

    def error(self, token: Token, message: str) -> ParseError:
        return ParseError(f"[Erro Sintático] Linha {token.line}, Coluna {token.column}: {message} (encontrado: '{token.lexeme}')")
