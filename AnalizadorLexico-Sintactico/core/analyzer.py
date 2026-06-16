from typing import Any, Dict

from .lexer import SQLLexer, LexicalError, TOKEN_CATALOG
from .parser import SQLParser, SyntaxErrorSQL, GRAMMAR_RULES
from .visual_models import AUTOMATON_MODEL, build_parse_tree


def base_payload() -> Dict[str, Any]:
    return {
        "grammar": [rule.__dict__ for rule in GRAMMAR_RULES],
        "token_catalog": TOKEN_CATALOG,
        "automaton": AUTOMATON_MODEL,
    }


def analyze_sql(sql: str) -> Dict[str, Any]:
    sql = (sql or "").strip()
    if not sql:
        return {
            "valid": False,
            "stage": "input",
            "tokens": [],
            "structured_json": None,
            "parse_tree": None,
            "errors": [{"stage": "input", "message": "Debe ingresar una consulta SQL."}],
            **base_payload(),
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
            "parse_tree": None,
            "errors": [exc.to_dict()],
            **base_payload(),
        }
    except SyntaxErrorSQL as exc:
        # Se conservan los tokens para que el usuario vea dónde falló el parsing.
        return {
            "valid": False,
            "stage": "syntactic",
            "tokens": [token.to_dict() for token in tokens if token.type != "EOF"],
            "structured_json": None,
            "parse_tree": None,
            "errors": [exc.to_dict()],
            **base_payload(),
        }

    return {
        "valid": True,
        "stage": "accepted",
        "tokens": [token.to_dict() for token in tokens if token.type != "EOF"],
        "structured_json": structured_query,
        "parse_tree": build_parse_tree(structured_query),
        "errors": [],
        **base_payload(),
    }
