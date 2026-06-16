from core.analyzer import analyze_sql


def test_valid_grouped_report_query():
    result = analyze_sql("""
        SELECT categoria, SUM(total) AS total_ventas
        FROM ventas
        WHERE fecha >= '2026-01-01' AND estado = 'CERRADO'
        GROUP BY categoria
        ORDER BY total_ventas DESC
        LIMIT 10;
    """)
    assert result["valid"] is True
    assert result["structured_json"]["operation"] == "SELECT"
    assert result["structured_json"]["fields"][1]["type"] == "aggregate"
    assert result["structured_json"]["group_by"] == ["categoria"]
    assert result["structured_json"]["limit"] == 10


def test_valid_join_query():
    result = analyze_sql("""
        SELECT c.nombre, COUNT(*) AS total_pedidos
        FROM clientes c
        INNER JOIN pedidos p ON c.id = p.cliente_id
        WHERE p.estado = 'PAGADO'
        GROUP BY c.nombre
        HAVING COUNT(*) >= 2;
    """)
    assert result["valid"] is True
    assert result["structured_json"]["joins"][0]["type"] == "INNER"
    assert result["structured_json"]["having"]["operator"] == ">="


def test_invalid_missing_from():
    result = analyze_sql("SELECT nombre, total WHERE total > 100;")
    assert result["valid"] is False
    assert result["stage"] == "syntactic"
    assert result["errors"][0]["expected"] == "FROM"


def test_invalid_lexical_character():
    result = analyze_sql("SELECT nombre FROM clientes @;")
    assert result["valid"] is False
    assert result["stage"] == "lexical"


def test_tokens_include_regular_expression_and_parse_tree():
    result = analyze_sql("SELECT nombre, prioridad FROM incidencias;")
    assert result["valid"] is True
    assert result["tokens"][0]["regex"]
    punctuation = next(token for token in result["tokens"] if token["type"] == "PUNCTUATION" and token["value"] == ",")
    assert punctuation["regex"] == r"[,\.\(\);]"
    assert result["parse_tree"]["label"] == "Consulta SQL válida"
    assert result["automaton"]["type"] == "AFD"
