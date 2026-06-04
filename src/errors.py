class CompilerError(Exception):
    """Erro base do compilador MiniPar."""


class LexerError(CompilerError):
    """Erro gerado durante a análise léxica."""


class ParseError(CompilerError):
    """Erro gerado durante a análise sintática."""


class SemanticError(CompilerError):
    """Erro gerado durante a análise semântica."""
