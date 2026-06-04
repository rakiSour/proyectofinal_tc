from dataclasses import dataclass
from typing import Any, Dict, List, Optional


KEYWORDS = {
    "SELECT", "FROM", "WHERE", "GROUP", "BY", "ORDER", "ASC", "DESC", "LIMIT",
    "AS", "AND", "OR", "NOT", "JOIN", "INNER", "LEFT", "RIGHT", "FULL", "ON",
    "HAVING", "COUNT", "SUM", "AVG", "MIN", "MAX", "DISTINCT", "IN", "LIKE", "IS", "NULL"
}

AGGREGATE_FUNCTIONS = {"COUNT", "SUM", "AVG", "MIN", "MAX"}

TOKEN_CATALOG = [
    {"type": "KEYWORD", "description": "Palabras reservadas SQL", "examples": ["SELECT", "FROM", "WHERE", "GROUP BY"]},
    {"type": "IDENTIFIER", "description": "Nombres de tablas, columnas o alias", "examples": ["ventas", "cliente_id", "v.total"]},
    {"type": "NUMBER", "description": "Valores numéricos enteros o decimales", "examples": ["10", "25.50"]},
    {"type": "STRING", "description": "Cadenas encerradas entre comillas simples", "examples": ["'ACTIVO'", "'2026-01-01'"]},
    {"type": "OPERATOR", "description": "Operadores aritméticos o comparativos", "examples": ["=", ">=", "<>", "*"]},
    {"type": "PUNCTUATION", "description": "Símbolos delimitadores", "examples": [",", ".", "(", ")", ";"]},
    {"type": "EOF", "description": "Fin de entrada", "examples": ["<EOF>"]},
]


@dataclass
class Token:
    type: str
    value: str
    position: int
    line: int
    column: int
    subtype: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        data = {
            "type": self.type,
            "value": self.value,
            "position": self.position,
            "line": self.line,
            "column": self.column,
        }
        if self.subtype:
            data["subtype"] = self.subtype
        return data


class LexicalError(Exception):
    def __init__(self, message: str, position: int, line: int, column: int):
        super().__init__(message)
        self.message = message
        self.position = position
        self.line = line
        self.column = column

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stage": "lexical",
            "message": self.message,
            "position": self.position,
            "line": self.line,
            "column": self.column,
        }


class SQLLexer:
    """Analizador léxico simple para consultas SELECT orientadas a reportería.

    La implementación evita librerías externas de parsing para evidenciar las fases de
    Teoría de la Computación: lectura secuencial, reconocimiento de lexemas y emisión
    de tokens clasificados por un catálogo formal.
    """

    COMPARISON_OPERATORS = {"<=", ">=", "!=", "<>", "=", "<", ">"}
    SINGLE_OPERATORS = {"+", "-", "*", "/"}
    PUNCTUATION = {",", ".", "(", ")", ";"}

    def tokenize(self, sql: str) -> List[Token]:
        tokens: List[Token] = []
        i = 0
        line = 1
        column = 1
        length = len(sql)

        def advance(n: int = 1) -> None:
            nonlocal i, line, column
            for _ in range(n):
                if i < length and sql[i] == "\n":
                    line += 1
                    column = 1
                else:
                    column += 1
                i += 1

        while i < length:
            char = sql[i]

            if char.isspace():
                advance()
                continue

            # Comentario de línea: -- comentario
            if sql.startswith("--", i):
                while i < length and sql[i] != "\n":
                    advance()
                continue

            # Comentario de bloque: /* comentario */
            if sql.startswith("/*", i):
                start_pos, start_line, start_col = i, line, column
                advance(2)
                closed = False
                while i < length:
                    if sql.startswith("*/", i):
                        advance(2)
                        closed = True
                        break
                    advance()
                if not closed:
                    raise LexicalError("Comentario de bloque sin cierre '*/'.", start_pos, start_line, start_col)
                continue

            start_pos, start_line, start_col = i, line, column

            # Cadenas SQL con comilla simple. Se acepta escape SQL estándar: ''
            if char == "'":
                value_chars = [char]
                advance()
                closed = False
                while i < length:
                    value_chars.append(sql[i])
                    if sql[i] == "'":
                        advance()
                        if i < length and sql[i] == "'":
                            # Comilla escapada dentro de la cadena
                            value_chars.append(sql[i])
                            advance()
                            continue
                        closed = True
                        break
                    advance()
                if not closed:
                    raise LexicalError("Cadena de texto sin comilla simple de cierre.", start_pos, start_line, start_col)
                tokens.append(Token("STRING", "".join(value_chars), start_pos, start_line, start_col))
                continue

            # Identificadores entre comillas dobles o backticks: "columna" / `tabla`
            if char in {'"', '`'}:
                quote = char
                value_chars = []
                advance()
                while i < length and sql[i] != quote:
                    value_chars.append(sql[i])
                    advance()
                if i >= length:
                    raise LexicalError(f"Identificador sin cierre {quote}.", start_pos, start_line, start_col)
                advance()
                value = "".join(value_chars)
                if not value.strip():
                    raise LexicalError("Identificador vacío.", start_pos, start_line, start_col)
                tokens.append(Token("IDENTIFIER", value, start_pos, start_line, start_col))
                continue

            # Números enteros o decimales
            if char.isdigit():
                value_chars = []
                has_dot = False
                while i < length and (sql[i].isdigit() or sql[i] == "."):
                    if sql[i] == ".":
                        if has_dot:
                            raise LexicalError("Número decimal inválido.", i, line, column)
                        has_dot = True
                    value_chars.append(sql[i])
                    advance()
                tokens.append(Token("NUMBER", "".join(value_chars), start_pos, start_line, start_col))
                continue

            # Identificadores y palabras reservadas
            if char.isalpha() or char == "_":
                value_chars = []
                while i < length and (sql[i].isalnum() or sql[i] == "_" or sql[i] == "$"):
                    value_chars.append(sql[i])
                    advance()
                raw_value = "".join(value_chars)
                upper_value = raw_value.upper()
                if upper_value in KEYWORDS:
                    tokens.append(Token("KEYWORD", upper_value, start_pos, start_line, start_col, subtype=upper_value))
                else:
                    tokens.append(Token("IDENTIFIER", raw_value, start_pos, start_line, start_col))
                continue

            # Operadores compuestos y simples
            two_chars = sql[i:i + 2]
            if two_chars in self.COMPARISON_OPERATORS:
                tokens.append(Token("OPERATOR", two_chars, start_pos, start_line, start_col))
                advance(2)
                continue

            if char in self.COMPARISON_OPERATORS or char in self.SINGLE_OPERATORS:
                tokens.append(Token("OPERATOR", char, start_pos, start_line, start_col))
                advance()
                continue

            if char in self.PUNCTUATION:
                tokens.append(Token("PUNCTUATION", char, start_pos, start_line, start_col))
                advance()
                continue

            raise LexicalError(f"Carácter no reconocido: '{char}'.", start_pos, start_line, start_col)

        tokens.append(Token("EOF", "<EOF>", length, line, column))
        return tokens
