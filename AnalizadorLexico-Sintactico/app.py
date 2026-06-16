import csv
import io
import json
from datetime import datetime

from flask import Flask, jsonify, make_response, render_template, request, send_file
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, Preformatted, SimpleDocTemplate, Spacer, Table, TableStyle

from core.analyzer import analyze_sql

app = Flask(__name__)

ALLOWED_UPLOAD_EXTENSIONS = {"txt", "csv"}

EXAMPLE_QUERIES = [
    {
        "name": "Reporte TI: incidencias por prioridad",
        "sql": """SELECT prioridad, COUNT(*) AS total_incidencias
FROM incidencias
WHERE estado = 'ABIERTO'
GROUP BY prioridad
ORDER BY total_incidencias DESC
LIMIT 10;""",
    },
    {
        "name": "Reporte TI: solicitudes por usuario con JOIN",
        "sql": """SELECT u.nombre, COUNT(*) AS total_tickets
FROM usuarios u
INNER JOIN tickets t ON u.id = t.usuario_id
WHERE t.estado = 'CERRADO'
GROUP BY u.nombre
HAVING COUNT(*) >= 2
ORDER BY total_tickets DESC;""",
    },
    {
        "name": "Consulta con error sintáctico",
        "sql": "SELECT nombre, total WHERE total > 100;",
    },
]


def get_file_extension(filename: str) -> str:
    return filename.rsplit(".", 1)[-1].lower() if "." in filename else ""


def extract_sql_from_csv(content: str) -> str:
    """Extrae una consulta SQL desde un archivo CSV.

    Formatos admitidos:
    1. CSV con columna sql, consulta o query.
    2. CSV simple donde la consulta se encuentra en la primera celda no vacía.
    """
    sample = content[:1024]
    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=",;")
    except csv.Error:
        dialect = csv.excel

    stream = io.StringIO(content)
    rows = list(csv.reader(stream, dialect))
    if not rows:
        return ""

    headers = [cell.strip().lower() for cell in rows[0]]
    possible_columns = {"sql", "consulta", "query", "sentencia"}
    matching_index = next((index for index, header in enumerate(headers) if header in possible_columns), None)

    if matching_index is not None:
        for row in rows[1:]:
            if matching_index < len(row) and row[matching_index].strip():
                return row[matching_index].strip()

    for row in rows:
        for cell in row:
            if cell.strip():
                return cell.strip()

    return ""


def extract_sql_from_uploaded_file(uploaded_file) -> str:
    filename = uploaded_file.filename or ""
    extension = get_file_extension(filename)
    if extension not in ALLOWED_UPLOAD_EXTENSIONS:
        raise ValueError("Solo se permiten archivos .txt o .csv.")

    content = uploaded_file.read().decode("utf-8-sig", errors="replace").strip()
    if not content:
        raise ValueError("El archivo está vacío.")

    if extension == "csv":
        content = extract_sql_from_csv(content)

    if not content:
        raise ValueError("No se encontró una consulta SQL dentro del archivo.")

    return content


def build_pdf_report(sql: str, result: dict) -> io.BytesIO:
    buffer = io.BytesIO()
    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=40,
        bottomMargin=36,
        title="Reporte de análisis SQL a JSON",
    )
    styles = getSampleStyleSheet()
    story = []

    status_text = "Consulta válida" if result.get("valid") else "Consulta con errores"
    generated_at = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    story.append(Paragraph("Reporte de análisis léxico-sintáctico SQL a JSON", styles["Title"]))
    story.append(Paragraph("Área de TI", styles["Heading2"]))
    story.append(Paragraph(f"Fecha de generación: {generated_at}", styles["Normal"]))
    story.append(Paragraph(f"Estado del análisis: <b>{status_text}</b>", styles["Normal"]))
    story.append(Spacer(1, 12))

    story.append(Paragraph("1. Consulta SQL evaluada", styles["Heading2"]))
    story.append(Preformatted(sql or "Sin consulta ingresada.", styles["Code"]))
    story.append(Spacer(1, 10))

    story.append(Paragraph("2. Traducción a JSON estructurado", styles["Heading2"]))
    json_payload = result.get("structured_json") if result.get("valid") else result
    json_text = json.dumps(json_payload, ensure_ascii=False, indent=2)
    story.append(Preformatted(json_text, styles["Code"]))
    story.append(Spacer(1, 10))

    tokens = result.get("tokens") or []
    story.append(Paragraph("3. Tokens léxicos identificados", styles["Heading2"]))
    if tokens:
        table_data = [["#", "Tipo", "Lexema", "Expresión regular"]]
        for index, token in enumerate(tokens, start=1):
            token_type = token.get("type", "")
            if token.get("subtype"):
                token_type = f"{token_type} ({token.get('subtype')})"
            table_data.append([
                str(index),
                token_type,
                str(token.get("value", ""))[:32],
                str(token.get("regex", ""))[:70],
            ])
        table = Table(table_data, colWidths=[28, 118, 120, 190], repeatRows=1)
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1d4ed8")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#dce3f0")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("FONTSIZE", (0, 0), (-1, -1), 7),
        ]))
        story.append(table)
    else:
        story.append(Paragraph("No se identificaron tokens para mostrar.", styles["Normal"]))
    story.append(Spacer(1, 10))

    errors = result.get("errors") or []
    if errors:
        story.append(Paragraph("4. Observaciones o errores detectados", styles["Heading2"]))
        for error in errors:
            message = error.get("message", "Error no especificado.")
            line = error.get("line")
            column = error.get("column")
            position = f" Línea {line}, columna {column}." if line and column else ""
            story.append(Paragraph(f"• {message}{position}", styles["Normal"]))

    document.build(story)
    buffer.seek(0)
    return buffer


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


@app.route("/api/upload", methods=["POST"])
def upload_endpoint():
    uploaded_file = request.files.get("file")
    if uploaded_file is None or not uploaded_file.filename:
        return jsonify({"valid": False, "message": "Debe seleccionar un archivo TXT o CSV."}), 400

    try:
        sql = extract_sql_from_uploaded_file(uploaded_file)
    except ValueError as exc:
        return jsonify({"valid": False, "message": str(exc)}), 400

    return jsonify({"valid": True, "filename": uploaded_file.filename, "sql": sql})


@app.route("/api/report", methods=["POST"])
def report_endpoint():
    payload = request.get_json(silent=True) or {}
    sql = payload.get("sql", "")
    result = analyze_sql(sql)
    pdf_buffer = build_pdf_report(sql, result)

    filename_date = datetime.now().strftime("%Y%m%d_%H%M%S")
    return send_file(
        pdf_buffer,
        mimetype="application/pdf",
        as_attachment=True,
        download_name=f"reporte_sql_json_{filename_date}.pdf",
    )


@app.route("/api/examples", methods=["GET"])
def examples_endpoint():
    return jsonify(EXAMPLE_QUERIES)


@app.errorhandler(404)
def not_found(_error):
    return jsonify({"valid": False, "message": "Ruta no encontrada."}), 404


if __name__ == "__main__":
    app.run(debug=True)
