from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from .lexer import AGGREGATE_FUNCTIONS, Token


CLAUSE_KEYWORDS = {"FROM", "WHERE", "GROUP", "HAVING", "ORDER", "LIMIT", "EOF"}
JOIN_PREFIXES = {"JOIN", "INNER", "LEFT", "RIGHT", "FULL"}
COMPARISON_OPERATORS = {"=", "!=", "<>", "<", ">", "<=", ">="}


class SyntaxErrorSQL(Exception):
    def __init__(self, message: str, token: Token, expected: Optional[str] = None):
        super().__init__(message)
        self.message = message
        self.token = token
        self.expected = expected

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stage": "syntactic",
            "message": self.message,
            "expected": self.expected,
            "found": self.token.value,
            "position": self.token.position,
            "line": self.token.line,
            "column": self.token.column,
        }


@dataclass
class GrammarRule:
    name: str
    production: str


GRAMMAR_RULES = [
    GrammarRule("consulta", "SELECT [DISTINCT] lista_seleccion FROM tabla [joins] [WHERE condicion] [GROUP BY campos] [HAVING condicion] [ORDER BY orden] [LIMIT numero] [;]"),
    GrammarRule("lista_seleccion", "item_seleccion (, item_seleccion)*"),
    GrammarRule("item_seleccion", "* | identificador [alias] | funcion_agregada '(' (* | identificador) ')' [alias]"),
    GrammarRule("tabla", "identificador [alias]"),
    GrammarRule("join", "[INNER | LEFT | RIGHT | FULL] JOIN tabla ON condicion"),
    GrammarRule("condicion", "predicado ((AND | OR) predicado)*"),
    GrammarRule("predicado", "operando operador_comparacion operando | operando LIKE operando | operando IN '(' lista_valores ')' | operando IS [NOT] NULL"),
    GrammarRule("orden", "identificador [ASC | DESC] (, identificador [ASC | DESC])*"),
]


class SQLParser:
    """Analizador sintáctico descendente recursivo para una gramática SELECT.

    Devuelve un árbol/estructura equivalente a un AST simplificado, listo para ser
    convertido a JSON y usado por módulos de reportería gerencial.
    """

    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0

    @property
    def current(self) -> Token:
        return self.tokens[self.pos]

    def peek(self, offset: int = 1) -> Token:
        index = min(self.pos + offset, len(self.tokens) - 1)
        return self.tokens[index]

    def advance(self) -> Token:
        token = self.current
        if self.pos < len(self.tokens) - 1:
            self.pos += 1
        return token

    def is_keyword(self, value: str) -> bool:
        return self.current.type == "KEYWORD" and self.current.value.upper() == value.upper()

    def match_keyword(self, value: str) -> bool:
        if self.is_keyword(value):
            self.advance()
            return True
        return False

    def expect_keyword(self, value: str) -> Token:
        if self.is_keyword(value):
            return self.advance()
        raise SyntaxErrorSQL(f"Se esperaba la palabra reservada {value}.", self.current, expected=value)

    def match_punctuation(self, value: str) -> bool:
        if self.current.type == "PUNCTUATION" and self.current.value == value:
            self.advance()
            return True
        return False

    def expect_punctuation(self, value: str) -> Token:
        if self.match_punctuation(value):
            return self.tokens[self.pos - 1]
        raise SyntaxErrorSQL(f"Se esperaba el símbolo '{value}'.", self.current, expected=value)

    def match_operator(self, values: Optional[set] = None) -> Optional[str]:
        if self.current.type == "OPERATOR" and (values is None or self.current.value in values):
            return self.advance().value
        return None

    def parse(self) -> Dict[str, Any]:
        query = self.parse_select_query()
        self.match_punctuation(";")
        if self.current.type != "EOF":
            raise SyntaxErrorSQL("Existen tokens adicionales después de finalizar la consulta.", self.current, expected="EOF")
        return query

    def parse_select_query(self) -> Dict[str, Any]:
        self.expect_keyword("SELECT")
        distinct = self.match_keyword("DISTINCT")
        fields = self.parse_select_list()
        self.expect_keyword("FROM")
        from_table = self.parse_table_ref()

        joins = []
        while self.current.type == "KEYWORD" and self.current.value in JOIN_PREFIXES:
            joins.append(self.parse_join())

        where = None
        group_by: List[str] = []
        having = None
        order_by: List[Dict[str, str]] = []
        limit = None

        if self.match_keyword("WHERE"):
            where = self.parse_condition(stop_keywords={"GROUP", "HAVING", "ORDER", "LIMIT"})

        if self.match_keyword("GROUP"):
            self.expect_keyword("BY")
            group_by = self.parse_identifier_list(stop_keywords={"HAVING", "ORDER", "LIMIT"})

        if self.match_keyword("HAVING"):
            having = self.parse_condition(stop_keywords={"ORDER", "LIMIT"})

        if self.match_keyword("ORDER"):
            self.expect_keyword("BY")
            order_by = self.parse_order_list()

        if self.match_keyword("LIMIT"):
            if self.current.type != "NUMBER" or "." in self.current.value:
                raise SyntaxErrorSQL("LIMIT debe recibir un número entero.", self.current, expected="NUMBER")
            limit = int(self.advance().value)

        return {
            "operation": "SELECT",
            "distinct": distinct,
            "fields": fields,
            "from": from_table,
            "joins": joins,
            "where": where,
            "group_by": group_by,
            "having": having,
            "order_by": order_by,
            "limit": limit,
        }

    def parse_select_list(self) -> List[Dict[str, Any]]:
        items = [self.parse_select_item()]
        while self.match_punctuation(","):
            items.append(self.parse_select_item())
        return items

    def parse_select_item(self) -> Dict[str, Any]:
        if self.current.type == "OPERATOR" and self.current.value == "*":
            self.advance()
            return {"type": "wildcard", "value": "*", "alias": self.parse_optional_alias()}

        if self.current.type == "KEYWORD" and self.current.value in AGGREGATE_FUNCTIONS and self.peek().value == "(":
            func = self.advance().value
            self.expect_punctuation("(")
            distinct = self.match_keyword("DISTINCT")
            if self.current.type == "OPERATOR" and self.current.value == "*":
                argument = "*"
                self.advance()
            else:
                argument = self.parse_identifier_path()
            self.expect_punctuation(")")
            return {
                "type": "aggregate",
                "function": func,
                "distinct": distinct,
                "argument": argument,
                "alias": self.parse_optional_alias(),
            }

        name = self.parse_identifier_path()
        return {"type": "column", "name": name, "alias": self.parse_optional_alias()}

    def parse_table_ref(self) -> Dict[str, Optional[str]]:
        name = self.parse_identifier_path()
        alias = self.parse_optional_alias(allow_direct=True)
        return {"table": name, "alias": alias}

    def parse_join(self) -> Dict[str, Any]:
        join_type = "INNER"
        if self.current.type == "KEYWORD" and self.current.value in {"INNER", "LEFT", "RIGHT", "FULL"}:
            join_type = self.advance().value
        self.expect_keyword("JOIN")
        table_ref = self.parse_table_ref()
        self.expect_keyword("ON")
        condition = self.parse_condition(stop_keywords={"JOIN", "INNER", "LEFT", "RIGHT", "FULL", "WHERE", "GROUP", "HAVING", "ORDER", "LIMIT"})
        return {"type": join_type, "table": table_ref, "on": condition}

    def parse_identifier_list(self, stop_keywords: Optional[set] = None) -> List[str]:
        values = [self.parse_identifier_path()]
        while self.match_punctuation(","):
            values.append(self.parse_identifier_path())
        if stop_keywords and self.current.type == "KEYWORD" and self.current.value not in stop_keywords and self.current.type != "EOF":
            # El control principal se encargará de las cláusulas posteriores.
            pass
        return values

    def parse_order_list(self) -> List[Dict[str, str]]:
        orders = [self.parse_order_item()]
        while self.match_punctuation(")"):
            raise SyntaxErrorSQL("Paréntesis de cierre inesperado en ORDER BY.", self.tokens[self.pos - 1], expected="identificador")
        while self.match_punctuation(","):
            orders.append(self.parse_order_item())
        return orders

    def parse_order_item(self) -> Dict[str, str]:
        field = self.parse_identifier_path()
        direction = "ASC"
        if self.current.type == "KEYWORD" and self.current.value in {"ASC", "DESC"}:
            direction = self.advance().value
        return {"field": field, "direction": direction}

    def parse_optional_alias(self, allow_direct: bool = True) -> Optional[str]:
        if self.match_keyword("AS"):
            return self.parse_identifier_name()
        if allow_direct and self.current.type == "IDENTIFIER":
            # Alias directo: SELECT total ventas_alias / FROM ventas v
            return self.advance().value
        return None

    def parse_identifier_name(self) -> str:
        if self.current.type == "IDENTIFIER":
            return self.advance().value
        # Permitir alias con palabras no estructurales solo si están entre comillas; las reservadas sin comillas se rechazan.
        raise SyntaxErrorSQL("Se esperaba un identificador.", self.current, expected="IDENTIFIER")

    def parse_identifier_path(self) -> str:
        parts = [self.parse_identifier_name()]
        while self.match_punctuation("."):
            parts.append(self.parse_identifier_name())
        return ".".join(parts)

    def parse_condition(self, stop_keywords: Optional[set] = None) -> Dict[str, Any]:
        return self.parse_or(stop_keywords or set())

    def parse_or(self, stop_keywords: set) -> Dict[str, Any]:
        left = self.parse_and(stop_keywords)
        while self.is_keyword("OR"):
            operator = self.advance().value
            right = self.parse_and(stop_keywords)
            left = {"type": "logical", "operator": operator, "left": left, "right": right}
        return left

    def parse_and(self, stop_keywords: set) -> Dict[str, Any]:
        left = self.parse_not(stop_keywords)
        while self.is_keyword("AND"):
            operator = self.advance().value
            right = self.parse_not(stop_keywords)
            left = {"type": "logical", "operator": operator, "left": left, "right": right}
        return left

    def parse_not(self, stop_keywords: set) -> Dict[str, Any]:
        if self.is_keyword("NOT"):
            self.advance()
            return {"type": "not", "condition": self.parse_not(stop_keywords)}
        return self.parse_predicate(stop_keywords)

    def parse_predicate(self, stop_keywords: set) -> Dict[str, Any]:
        if self.match_punctuation("("):
            condition = self.parse_condition(stop_keywords)
            self.expect_punctuation(")")
            return condition

        left = self.parse_value()

        op = self.match_operator(COMPARISON_OPERATORS)
        if op:
            right = self.parse_value()
            return {"type": "comparison", "operator": op, "left": left, "right": right}

        if self.match_keyword("LIKE"):
            right = self.parse_value()
            return {"type": "comparison", "operator": "LIKE", "left": left, "right": right}

        if self.match_keyword("IN"):
            self.expect_punctuation("(")
            values = [self.parse_value()]
            while self.match_punctuation(","):
                values.append(self.parse_value())
            self.expect_punctuation(")")
            return {"type": "comparison", "operator": "IN", "left": left, "right": values}

        if self.match_keyword("IS"):
            negated = self.match_keyword("NOT")
            self.expect_keyword("NULL")
            return {"type": "comparison", "operator": "IS NOT" if negated else "IS", "left": left, "right": {"type": "literal", "data_type": "NULL", "value": None}}

        if self.current.type == "KEYWORD" and self.current.value in stop_keywords:
            raise SyntaxErrorSQL("Condición incompleta: falta operador comparativo y valor.", self.current, expected="operador comparativo")

        raise SyntaxErrorSQL("Se esperaba un operador comparativo dentro de la condición.", self.current, expected="=, !=, <>, <, >, <=, >=, LIKE, IN, IS")

    def parse_value(self) -> Dict[str, Any]:
        token = self.current

        if token.type == "NUMBER":
            self.advance()
            if "." in token.value:
                value: Any = float(token.value)
                data_type = "DECIMAL"
            else:
                value = int(token.value)
                data_type = "INTEGER"
            return {"type": "literal", "data_type": data_type, "value": value}

        if token.type == "STRING":
            self.advance()
            # Se retiran las comillas simples y se normaliza el escape SQL estándar.
            value = token.value[1:-1].replace("''", "'")
            return {"type": "literal", "data_type": "STRING", "value": value}

        if token.type == "KEYWORD" and token.value == "NULL":
            self.advance()
            return {"type": "literal", "data_type": "NULL", "value": None}

        if token.type == "OPERATOR" and token.value == "*":
            self.advance()
            return {"type": "wildcard", "value": "*"}

        if token.type == "KEYWORD" and token.value in AGGREGATE_FUNCTIONS and self.peek().value == "(":
            func = self.advance().value
            self.expect_punctuation("(")
            distinct = self.match_keyword("DISTINCT")
            if self.current.type == "OPERATOR" and self.current.value == "*":
                argument: Any = {"type": "wildcard", "value": "*"}
                self.advance()
            else:
                argument = {"type": "column", "name": self.parse_identifier_path()}
            self.expect_punctuation(")")
            return {"type": "aggregate", "function": func, "distinct": distinct, "argument": argument}

        if token.type == "IDENTIFIER":
            return {"type": "column", "name": self.parse_identifier_path()}

        raise SyntaxErrorSQL("Se esperaba un valor, identificador o función.", token, expected="valor | identificador | función")
