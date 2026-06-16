from typing import Any, Dict, List, Optional


AUTOMATON_MODEL: Dict[str, Any] = {
    "name": "AFD del analizador léxico SQL",
    "type": "AFD",
    "description": (
        "Se usa un Autómata Finito Determinista porque los lexemas SQL se reconocen "
        "mediante expresiones regulares y, para cada carácter leído, existe una transición "
        "definida según su clase: letra, dígito, comilla, operador, puntuación o espacio."
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
