from typing import Any, Dict, List, Optional


AUTOMATON_MODEL: Dict[str, Any] = {
    "name": "AFD general del analizador léxico SQL",
    "type": "AFD",
    "description": (
        "Modelo general del analizador léxico. A partir del estado inicial q0, "
        "el carácter leído determina una única transición hacia el tipo de lexema: "
        "palabra reservada/identificador, número, cadena, operador o puntuación."
    ),
    "alphabet": ["letra", "dígito", "_", "$", "'", "operador", "puntuación", "espacio", "otro"],
    "states": [
        {"id": "q0", "label": "q0\nInicio", "start": True, "accept": False},
        {"id": "qID", "label": "qID\nKEYWORD / IDENTIFIER", "start": False, "accept": True},
        {"id": "qNUM", "label": "qNUM\nNUMBER", "start": False, "accept": True},
        {"id": "qSTR", "label": "qSTR\nLeyendo STRING", "start": False, "accept": False},
        {"id": "qSTR_OK", "label": "qSTR_OK\nSTRING", "start": False, "accept": True},
        {"id": "qOP", "label": "qOP\nOPERATOR", "start": False, "accept": True},
        {"id": "qPUNC", "label": "qPUNC\nPUNCTUATION", "start": False, "accept": True},
        {"id": "qERR", "label": "qERR\nError léxico", "start": False, "accept": False},
    ],
    "positions": {
        "q0": {"x": 100, "y": 230},
        "qID": {"x": 330, "y": 90},
        "qNUM": {"x": 330, "y": 230},
        "qSTR": {"x": 330, "y": 370},
        "qSTR_OK": {"x": 590, "y": 370},
        "qOP": {"x": 590, "y": 90},
        "qPUNC": {"x": 590, "y": 230},
        "qERR": {"x": 820, "y": 230},
    },
    "transitions": [
        {"from": "q0", "to": "q0", "label": "espacio / salto de línea"},
        {"from": "q0", "to": "qID", "label": "letra o _"},
        {"from": "qID", "to": "qID", "label": "letra, dígito, _ o $"},
        {"from": "q0", "to": "qNUM", "label": "dígito"},
        {"from": "qNUM", "to": "qNUM", "label": "dígito o . decimal"},
        {"from": "q0", "to": "qSTR", "label": "'"},
        {"from": "qSTR", "to": "qSTR", "label": "carácter o '' escapado"},
        {"from": "qSTR", "to": "qSTR_OK", "label": "' de cierre"},
        {"from": "q0", "to": "qOP", "label": "=, <, >, <=, >=, !=, <>, +, -, *, /"},
        {"from": "q0", "to": "qPUNC", "label": ", . ( ) ;"},
        {"from": "q0", "to": "qERR", "label": "otro carácter"},
    ],
}


def transition_table(rows: List[List[str]]) -> List[Dict[str, str]]:
    return [
        {"state": state, "symbol": symbol, "next": nxt, "note": note}
        for state, symbol, nxt, note in rows
    ]


def token_model(
    token_type: str,
    title: str,
    regex: str,
    description: str,
    afnd: Dict[str, Any],
    afd: Dict[str, Any],
    table: List[Dict[str, str]],
) -> Dict[str, Any]:
    return {
        "token_type": token_type,
        "title": title,
        "regex": regex,
        "description": description,
        "afnd": {**afnd, "type": "AFND", "regex": regex},
        "afd": {**afd, "type": "AFD", "regex": regex},
        "transition_table": table,
    }


TOKEN_AUTOMATA_MODELS: Dict[str, Dict[str, Any]] = {
    "KEYWORD": token_model(
        "KEYWORD",
        "Palabra reservada SQL",
        r"(?i)\b(SELECT|FROM|WHERE|GROUP|BY|ORDER|ASC|DESC|LIMIT|AS|AND|OR|NOT|JOIN|INNER|LEFT|RIGHT|FULL|ON|HAVING|COUNT|SUM|AVG|MIN|MAX|DISTINCT|IN|LIKE|IS|NULL)\b",
        "Reconoce palabras reservadas del subconjunto SQL utilizado por el analizador.",
        {
            "name": "AFND para KEYWORD",
            "description": "El AFND representa alternativas por palabra reservada. Desde q0 existen transiciones epsilon hacia ramas equivalentes a SELECT, FROM, WHERE, JOIN y otras palabras reservadas.",
            "states": [
                {"id": "q0", "label": "q0\nInicio", "start": True, "accept": False},
                {"id": "qS", "label": "rama\nSELECT", "accept": False},
                {"id": "qF", "label": "rama\nFROM", "accept": False},
                {"id": "qW", "label": "rama\nWHERE", "accept": False},
                {"id": "qJ", "label": "rama\nJOIN/ON", "accept": False},
                {"id": "qKW", "label": "qKW\nKEYWORD", "accept": True},
            ],
            "positions": {"q0": {"x": 90, "y": 220}, "qS": {"x": 290, "y": 80}, "qF": {"x": 290, "y": 170}, "qW": {"x": 290, "y": 270}, "qJ": {"x": 290, "y": 360}, "qKW": {"x": 560, "y": 220}},
            "transitions": [
                {"from": "q0", "to": "qS", "label": "ε"},
                {"from": "q0", "to": "qF", "label": "ε"},
                {"from": "q0", "to": "qW", "label": "ε"},
                {"from": "q0", "to": "qJ", "label": "ε"},
                {"from": "qS", "to": "qKW", "label": "SELECT"},
                {"from": "qF", "to": "qKW", "label": "FROM / FULL"},
                {"from": "qW", "to": "qKW", "label": "WHERE"},
                {"from": "qJ", "to": "qKW", "label": "JOIN / ON / ..."},
            ],
        },
        {
            "name": "AFD para KEYWORD",
            "description": "El AFD simplificado lee una secuencia alfabética y acepta si el lexema completo pertenece al catálogo de palabras reservadas.",
            "states": [
                {"id": "q0", "label": "q0\nInicio", "start": True, "accept": False},
                {"id": "qWORD", "label": "qWORD\nletras", "accept": False},
                {"id": "qKW", "label": "qKW\nKEYWORD", "accept": True},
                {"id": "qID", "label": "qID\nno reservada", "accept": False},
            ],
            "positions": {"q0": {"x": 90, "y": 220}, "qWORD": {"x": 300, "y": 220}, "qKW": {"x": 540, "y": 130}, "qID": {"x": 540, "y": 310}},
            "transitions": [
                {"from": "q0", "to": "qWORD", "label": "letra"},
                {"from": "qWORD", "to": "qWORD", "label": "letra"},
                {"from": "qWORD", "to": "qKW", "label": "lexema ∈ KEYWORDS"},
                {"from": "qWORD", "to": "qID", "label": "lexema ∉ KEYWORDS"},
            ],
        },
        transition_table([
            ["q0", "letra", "qWORD", "Inicia lectura de palabra"],
            ["qWORD", "letra", "qWORD", "Continúa acumulando caracteres"],
            ["qWORD", "fin de lexema y valor reservado", "qKW", "Acepta como KEYWORD"],
            ["qWORD", "fin de lexema y valor no reservado", "qID", "No pertenece a KEYWORD"],
        ]),
    ),
    "IDENTIFIER": token_model(
        "IDENTIFIER",
        "Identificador",
        r"[A-Za-z_][A-Za-z0-9_$]*",
        "Reconoce nombres de tablas, columnas o alias.",
        {
            "name": "AFND para IDENTIFIER",
            "description": "El AFND acepta una letra o guion bajo inicial y luego permite cero o más letras, dígitos, guiones bajos o signos de dólar.",
            "states": [
                {"id": "q0", "label": "q0\nInicio", "start": True, "accept": False},
                {"id": "q1", "label": "q1\nprimer carácter", "accept": True},
            ],
            "positions": {"q0": {"x": 100, "y": 180}, "q1": {"x": 360, "y": 180}},
            "transitions": [
                {"from": "q0", "to": "q1", "label": "letra o _"},
                {"from": "q1", "to": "q1", "label": "letra | dígito | _ | $"},
            ],
        },
        {
            "name": "AFD para IDENTIFIER",
            "description": "En el AFD, cada símbolo válido conserva el estado de aceptación q1; cualquier carácter inválido se rechaza.",
            "states": [
                {"id": "q0", "label": "q0\nInicio", "start": True, "accept": False},
                {"id": "q1", "label": "q1\nIDENTIFIER", "accept": True},
                {"id": "qERR", "label": "qERR\nRechazo", "accept": False},
            ],
            "positions": {"q0": {"x": 100, "y": 180}, "q1": {"x": 360, "y": 180}, "qERR": {"x": 610, "y": 300}},
            "transitions": [
                {"from": "q0", "to": "q1", "label": "letra o _"},
                {"from": "q1", "to": "q1", "label": "letra, dígito, _ o $"},
                {"from": "q0", "to": "qERR", "label": "otro"},
                {"from": "q1", "to": "qERR", "label": "símbolo no válido"},
            ],
        },
        transition_table([
            ["q0", "letra o _", "q1", "Acepta inicio del identificador"],
            ["q1", "letra, dígito, _ o $", "q1", "Permite continuar el identificador"],
            ["q0/q1", "otro", "qERR", "Rechaza el lexema"],
        ]),
    ),
    "NUMBER": token_model(
        "NUMBER",
        "Número entero o decimal",
        r"\d+(\.\d+)?",
        "Reconoce valores numéricos enteros o decimales.",
        {
            "name": "AFND para NUMBER",
            "description": "El AFND acepta una o más cifras y opcionalmente una parte decimal formada por punto y más cifras.",
            "states": [
                {"id": "q0", "label": "q0\nInicio", "start": True, "accept": False},
                {"id": "qINT", "label": "qINT\nentero", "accept": True},
                {"id": "qDOT", "label": "qDOT\npunto", "accept": False},
                {"id": "qDEC", "label": "qDEC\ndecimal", "accept": True},
            ],
            "positions": {"q0": {"x": 80, "y": 210}, "qINT": {"x": 300, "y": 210}, "qDOT": {"x": 520, "y": 210}, "qDEC": {"x": 740, "y": 210}},
            "transitions": [
                {"from": "q0", "to": "qINT", "label": "dígito"},
                {"from": "qINT", "to": "qINT", "label": "dígito"},
                {"from": "qINT", "to": "qDOT", "label": "."},
                {"from": "qDOT", "to": "qDEC", "label": "dígito"},
                {"from": "qDEC", "to": "qDEC", "label": "dígito"},
            ],
        },
        {
            "name": "AFD para NUMBER",
            "description": "El AFD determina si el número termina en estado entero qINT o decimal qDEC; terminar en qDOT se rechaza.",
            "states": [
                {"id": "q0", "label": "q0\nInicio", "start": True, "accept": False},
                {"id": "qINT", "label": "qINT\nNUMBER", "accept": True},
                {"id": "qDOT", "label": "qDOT\npendiente", "accept": False},
                {"id": "qDEC", "label": "qDEC\nNUMBER", "accept": True},
                {"id": "qERR", "label": "qERR\nRechazo", "accept": False},
            ],
            "positions": {"q0": {"x": 80, "y": 210}, "qINT": {"x": 280, "y": 210}, "qDOT": {"x": 480, "y": 210}, "qDEC": {"x": 680, "y": 210}, "qERR": {"x": 480, "y": 340}},
            "transitions": [
                {"from": "q0", "to": "qINT", "label": "dígito"},
                {"from": "qINT", "to": "qINT", "label": "dígito"},
                {"from": "qINT", "to": "qDOT", "label": "."},
                {"from": "qDOT", "to": "qDEC", "label": "dígito"},
                {"from": "qDEC", "to": "qDEC", "label": "dígito"},
                {"from": "qDOT", "to": "qERR", "label": "fin / otro"},
            ],
        },
        transition_table([
            ["q0", "dígito", "qINT", "Comienza número entero"],
            ["qINT", "dígito", "qINT", "Sigue siendo entero"],
            ["qINT", ".", "qDOT", "Inicia parte decimal"],
            ["qDOT", "dígito", "qDEC", "Primer dígito decimal"],
            ["qDEC", "dígito", "qDEC", "Continúa decimal"],
            ["qDOT", "fin u otro", "qERR", "Rechaza decimal incompleto"],
        ]),
    ),
    "STRING": token_model(
        "STRING",
        "Cadena de texto",
        r"'([^']|'')*'",
        "Reconoce textos encerrados entre comillas simples y comillas escapadas mediante dos comillas simples.",
        {
            "name": "AFND para STRING",
            "description": "El AFND ingresa con comilla simple, consume caracteres internos o comillas escapadas y acepta al leer la comilla de cierre.",
            "states": [
                {"id": "q0", "label": "q0\nInicio", "start": True, "accept": False},
                {"id": "qIN", "label": "qIN\ncontenido", "accept": False},
                {"id": "qESC", "label": "qESC\nescape ''", "accept": False},
                {"id": "qOK", "label": "qOK\nSTRING", "accept": True},
            ],
            "positions": {"q0": {"x": 80, "y": 210}, "qIN": {"x": 300, "y": 210}, "qESC": {"x": 520, "y": 90}, "qOK": {"x": 640, "y": 210}},
            "transitions": [
                {"from": "q0", "to": "qIN", "label": "'"},
                {"from": "qIN", "to": "qIN", "label": "carácter distinto de '"},
                {"from": "qIN", "to": "qESC", "label": "''"},
                {"from": "qESC", "to": "qIN", "label": "ε"},
                {"from": "qIN", "to": "qOK", "label": "' cierre"},
            ],
        },
        {
            "name": "AFD para STRING",
            "description": "El AFD mantiene el estado qIN mientras consume contenido y acepta únicamente cuando encuentra comilla de cierre válida.",
            "states": [
                {"id": "q0", "label": "q0\nInicio", "start": True, "accept": False},
                {"id": "qIN", "label": "qIN\ncontenido", "accept": False},
                {"id": "qOK", "label": "qOK\nSTRING", "accept": True},
                {"id": "qERR", "label": "qERR\nRechazo", "accept": False},
            ],
            "positions": {"q0": {"x": 80, "y": 210}, "qIN": {"x": 300, "y": 210}, "qOK": {"x": 560, "y": 210}, "qERR": {"x": 300, "y": 340}},
            "transitions": [
                {"from": "q0", "to": "qIN", "label": "'"},
                {"from": "qIN", "to": "qIN", "label": "carácter / '' escapado"},
                {"from": "qIN", "to": "qOK", "label": "' cierre"},
                {"from": "q0", "to": "qERR", "label": "otro"},
                {"from": "qIN", "to": "qERR", "label": "fin sin cierre"},
            ],
        },
        transition_table([
            ["q0", "'", "qIN", "Abre cadena"],
            ["qIN", "carácter distinto de ' o '' escapado", "qIN", "Consume contenido"],
            ["qIN", "' de cierre", "qOK", "Acepta STRING"],
            ["qIN", "fin sin cierre", "qERR", "Rechaza cadena incompleta"],
        ]),
    ),
    "OPERATOR": token_model(
        "OPERATOR",
        "Operador SQL",
        r"<=|>=|!=|<>|=|<|>|\+|-|\*|/",
        "Reconoce operadores de comparación y operadores aritméticos simples.",
        {
            "name": "AFND para OPERATOR",
            "description": "El AFND tiene alternativas para operadores de un carácter y operadores compuestos de dos caracteres.",
            "states": [
                {"id": "q0", "label": "q0\nInicio", "start": True, "accept": False},
                {"id": "qONE", "label": "qONE\nun carácter", "accept": True},
                {"id": "qPFX", "label": "qPFX\nprefijo", "accept": True},
                {"id": "qTWO", "label": "qTWO\ncompuesto", "accept": True},
            ],
            "positions": {"q0": {"x": 90, "y": 210}, "qONE": {"x": 330, "y": 100}, "qPFX": {"x": 330, "y": 280}, "qTWO": {"x": 590, "y": 280}},
            "transitions": [
                {"from": "q0", "to": "qONE", "label": "= + - * /"},
                {"from": "q0", "to": "qPFX", "label": "< > !"},
                {"from": "qPFX", "to": "qTWO", "label": "= o >"},
            ],
        },
        {
            "name": "AFD para OPERATOR",
            "description": "El AFD acepta operadores simples y compuestos válidos; el signo ! solo es válido si continúa con =.",
            "states": [
                {"id": "q0", "label": "q0\nInicio", "start": True, "accept": False},
                {"id": "qONE", "label": "qONE\nOPERATOR", "accept": True},
                {"id": "qPFX", "label": "qPFX\n< o >", "accept": True},
                {"id": "qBANG", "label": "qBANG\n!", "accept": False},
                {"id": "qTWO", "label": "qTWO\nOPERATOR", "accept": True},
                {"id": "qERR", "label": "qERR\nRechazo", "accept": False},
            ],
            "positions": {"q0": {"x": 80, "y": 230}, "qONE": {"x": 300, "y": 90}, "qPFX": {"x": 300, "y": 220}, "qBANG": {"x": 300, "y": 350}, "qTWO": {"x": 560, "y": 220}, "qERR": {"x": 560, "y": 350}},
            "transitions": [
                {"from": "q0", "to": "qONE", "label": "= + - * /"},
                {"from": "q0", "to": "qPFX", "label": "< o >"},
                {"from": "q0", "to": "qBANG", "label": "!"},
                {"from": "qPFX", "to": "qTWO", "label": "= o >"},
                {"from": "qBANG", "to": "qTWO", "label": "="},
                {"from": "qBANG", "to": "qERR", "label": "otro / fin"},
            ],
        },
        transition_table([
            ["q0", "= + - * /", "qONE", "Acepta operador simple"],
            ["q0", "< o >", "qPFX", "Acepta < o > y espera posible compuesto"],
            ["q0", "!", "qBANG", "Debe continuar con ="],
            ["qPFX", "= o >", "qTWO", "Acepta <=, >= o <>"],
            ["qBANG", "=", "qTWO", "Acepta !="],
            ["qBANG", "otro / fin", "qERR", "Rechaza ! aislado"],
        ]),
    ),
    "PUNCTUATION": token_model(
        "PUNCTUATION",
        "Signo de puntuación",
        r"[,\.\(\);]",
        "Reconoce delimitadores de la consulta: coma, punto, paréntesis y punto y coma.",
        {
            "name": "AFND para PUNCTUATION",
            "description": "El AFND acepta cualquiera de los símbolos delimitadores como alternativa válida.",
            "states": [
                {"id": "q0", "label": "q0\nInicio", "start": True, "accept": False},
                {"id": "q1", "label": "q1\nPUNCTUATION", "accept": True},
            ],
            "positions": {"q0": {"x": 100, "y": 180}, "q1": {"x": 360, "y": 180}},
            "transitions": [
                {"from": "q0", "to": "q1", "label": ", . ( ) ;"},
            ],
        },
        {
            "name": "AFD para PUNCTUATION",
            "description": "El AFD acepta un único símbolo de puntuación válido y rechaza cualquier otro carácter.",
            "states": [
                {"id": "q0", "label": "q0\nInicio", "start": True, "accept": False},
                {"id": "q1", "label": "q1\nPUNCTUATION", "accept": True},
                {"id": "qERR", "label": "qERR\nRechazo", "accept": False},
            ],
            "positions": {"q0": {"x": 100, "y": 180}, "q1": {"x": 360, "y": 180}, "qERR": {"x": 360, "y": 320}},
            "transitions": [
                {"from": "q0", "to": "q1", "label": ", . ( ) ;"},
                {"from": "q0", "to": "qERR", "label": "otro"},
            ],
        },
        transition_table([
            ["q0", ", . ( ) ;", "q1", "Acepta signo delimitador"],
            ["q0", "otro", "qERR", "Rechaza carácter"],
        ]),
    ),
    "EOF": token_model(
        "EOF",
        "Fin de entrada",
        r"\Z",
        "Marca el final de la consulta para el parser.",
        {
            "name": "AFND para EOF",
            "description": "Acepta cuando no quedan caracteres por leer.",
            "states": [
                {"id": "q0", "label": "q0\nInicio", "start": True, "accept": False},
                {"id": "qEOF", "label": "qEOF\nEOF", "accept": True},
            ],
            "positions": {"q0": {"x": 100, "y": 180}, "qEOF": {"x": 360, "y": 180}},
            "transitions": [{"from": "q0", "to": "qEOF", "label": "fin de cadena"}],
        },
        {
            "name": "AFD para EOF",
            "description": "Acepta únicamente en el fin de la entrada.",
            "states": [
                {"id": "q0", "label": "q0\nInicio", "start": True, "accept": False},
                {"id": "qEOF", "label": "qEOF\nEOF", "accept": True},
            ],
            "positions": {"q0": {"x": 100, "y": 180}, "qEOF": {"x": 360, "y": 180}},
            "transitions": [{"from": "q0", "to": "qEOF", "label": "fin de cadena"}],
        },
        transition_table([["q0", "fin de cadena", "qEOF", "Acepta EOF"]]),
    ),
}


def make_node(label: str, children: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
    node: Dict[str, Any] = {"label": label}
    if children:
        node["children"] = children
    return node


def value_to_tree(value: Any) -> Dict[str, Any]:
    if value is None:
        return make_node("Sin valor")

    if isinstance(value, list):
        return make_node("Lista", [value_to_tree(item) for item in value])

    if not isinstance(value, dict):
        return make_node(str(value))

    value_type = value.get("type")

    if value_type == "literal":
        return make_node(f"Literal {value.get('data_type')}: {value.get('value')}")

    if value_type == "column":
        return make_node(f"Columna: {value.get('name')}")

    if value_type == "wildcard":
        return make_node("Comodín: *")

    if value_type == "aggregate":
        argument = value.get("argument")
        if isinstance(argument, dict):
            argument_node = value_to_tree(argument)
        else:
            argument_node = make_node(f"Argumento: {argument}")
        children = [argument_node]
        if value.get("distinct"):
            children.insert(0, make_node("DISTINCT"))
        return make_node(f"Función agregada: {value.get('function')}", children)

    if value_type == "comparison":
        operator = value.get("operator")
        right = value.get("right")
        if isinstance(right, list):
            right_node = make_node("Valores IN", [value_to_tree(item) for item in right])
        else:
            right_node = value_to_tree(right)
        return make_node(f"Comparación: {operator}", [value_to_tree(value.get("left")), right_node])

    if value_type == "logical":
        return make_node(f"Operador lógico: {value.get('operator')}", [
            value_to_tree(value.get("left")),
            value_to_tree(value.get("right")),
        ])

    if value_type == "not":
        return make_node("NOT", [value_to_tree(value.get("condition"))])

    return make_node(str(value))


def field_to_tree(field: Dict[str, Any]) -> Dict[str, Any]:
    field_type = field.get("type")
    children: List[Dict[str, Any]] = []

    if field_type == "column":
        label = f"Campo columna: {field.get('name')}"
    elif field_type == "wildcard":
        label = "Campo comodín: *"
    elif field_type == "aggregate":
        label = f"Campo función: {field.get('function')}"
        argument = field.get("argument")
        children.append(make_node(f"Argumento: {argument}"))
        if field.get("distinct"):
            children.insert(0, make_node("DISTINCT"))
    else:
        label = f"Campo: {field_type or 'desconocido'}"

    if field.get("alias"):
        children.append(make_node(f"Alias: {field.get('alias')}"))

    return make_node(label, children)


def table_to_tree(table_ref: Dict[str, Any]) -> Dict[str, Any]:
    children: List[Dict[str, Any]] = []
    if table_ref.get("alias"):
        children.append(make_node(f"Alias: {table_ref.get('alias')}"))
    return make_node(f"Tabla: {table_ref.get('table')}", children)


def build_parse_tree(structured_query: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    if not structured_query:
        return None

    children: List[Dict[str, Any]] = []
    children.append(make_node("SELECT", [field_to_tree(field) for field in structured_query.get("fields", [])]))

    if structured_query.get("distinct"):
        children.append(make_node("DISTINCT"))

    from_ref = structured_query.get("from")
    if from_ref:
        children.append(make_node("FROM", [table_to_tree(from_ref)]))

    joins = structured_query.get("joins") or []
    if joins:
        join_nodes = []
        for join in joins:
            join_nodes.append(make_node(f"{join.get('type')} JOIN", [
                table_to_tree(join.get("table") or {}),
                make_node("ON", [value_to_tree(join.get("on"))]),
            ]))
        children.append(make_node("JOINS", join_nodes))

    if structured_query.get("where"):
        children.append(make_node("WHERE", [value_to_tree(structured_query.get("where"))]))

    if structured_query.get("group_by"):
        children.append(make_node("GROUP BY", [make_node(field) for field in structured_query.get("group_by", [])]))

    if structured_query.get("having"):
        children.append(make_node("HAVING", [value_to_tree(structured_query.get("having"))]))

    if structured_query.get("order_by"):
        order_nodes = [make_node(f"{item.get('field')} {item.get('direction')}") for item in structured_query.get("order_by", [])]
        children.append(make_node("ORDER BY", order_nodes))

    if structured_query.get("limit") is not None:
        children.append(make_node(f"LIMIT: {structured_query.get('limit')}"))

    return make_node("Consulta SQL válida", children)
