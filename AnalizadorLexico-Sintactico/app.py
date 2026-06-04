from flask import Flask, jsonify, render_template, request

from core.analyzer import analyze_sql

app = Flask(__name__)

EXAMPLE_QUERIES = [
    {
        "name": "Reporte de ventas por categoría",
        "sql": """SELECT categoria, SUM(total) AS total_ventas
FROM ventas
WHERE fecha >= '2026-01-01' AND estado = 'CERRADO'
GROUP BY categoria
ORDER BY total_ventas DESC
LIMIT 10;""",
    },
    {
        "name": "Reporte de clientes con JOIN",
        "sql": """SELECT c.nombre, COUNT(*) AS total_pedidos
FROM clientes c
INNER JOIN pedidos p ON c.id = p.cliente_id
WHERE p.estado = 'PAGADO'
GROUP BY c.nombre
HAVING COUNT(*) >= 2
ORDER BY total_pedidos DESC;""",
    },
    {
        "name": "Consulta con error sintáctico",
        "sql": "SELECT nombre, total WHERE total > 100;",
    },
]


@app.route("/")
def index():
    return render_template("index.html", examples=EXAMPLE_QUERIES)


@app.route("/api/analyze", methods=["POST"])
def analyze_endpoint():
    payload = request.get_json(silent=True) or {}
    sql = payload.get("sql", "")
    result = analyze_sql(sql)
    status = 200 if result.get("valid") else 400
    return jsonify(result), status


@app.route("/api/examples", methods=["GET"])
def examples_endpoint():
    return jsonify(EXAMPLE_QUERIES)


@app.errorhandler(404)
def not_found(_error):
    return jsonify({"valid": False, "message": "Ruta no encontrada."}), 404


if __name__ == "__main__":
    app.run(debug=True)
