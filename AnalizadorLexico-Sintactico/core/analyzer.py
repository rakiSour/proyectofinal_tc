from typing import Any, Dict

from .lexer import SQLLexer, LexicalError, TOKEN_CATALOG
from .parser import SQLParser, SyntaxErrorSQL, GRAMMAR_RULES


def analyze_sql(sql: str) -> Dict[str, Any]:
    sql = (sql or "").strip()
    if not sql:
        return {
            "valid": False,
            "stage": "input",
            "tokens": [],
            "structured_json": None,
            "errors": [{"stage": "input", "message": "Debe ingresar una consulta SQL."}],
            "grammar": [rule.__dict__ for rule in GRAMMAR_RULES],
            "token_catalog": TOKEN_CATALOG,
        }

    lexer = SQLLexer()
    try:
        tokens = lexer.tokenize(sql)
        parser = SQLParser(tokens)
        structured_query = parser.parse()
    except LexicalError as exc:
        return {
            "valid": False,
            "stage": "lexical",
            "tokens": [],
            "structured_json": None,
            "errors": [exc.to_dict()],
            "grammar": [rule.__dict__ for rule in GRAMMAR_RULES],
            "token_catalog": TOKEN_CATALOG,
        }
    except SyntaxErrorSQL as exc:
        # Se conservan los tokens para que el usuario vea dónde falló el parsing.
        return {
            "valid": False,
            "stage": "syntactic",
            "tokens": [token.to_dict() for token in tokens if token.type != "EOF"],
            "structured_json": None,
            "errors": [exc.to_dict()],
            "grammar": [rule.__dict__ for rule in GRAMMAR_RULES],
            "token_catalog": TOKEN_CATALOG,
        }

    return {
        "valid": True,
        "stage": "accepted",
        "tokens": [token.to_dict() for token in tokens if token.type != "EOF"],
        "structured_json": structured_query,
        "errors": [],
        "grammar": [rule.__dict__ for rule in GRAMMAR_RULES],
        "token_catalog": TOKEN_CATALOG,
    }
