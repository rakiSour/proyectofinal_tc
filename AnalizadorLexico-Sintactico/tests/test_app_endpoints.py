import io

from app import app


def test_upload_txt_loads_sql_query():
    client = app.test_client()
    data = {
        "file": (io.BytesIO(b"SELECT nombre FROM usuarios;"), "consulta.txt")
    }
    response = client.post("/api/upload", data=data, content_type="multipart/form-data")
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["valid"] is True
    assert payload["sql"] == "SELECT nombre FROM usuarios;"


def test_upload_csv_loads_sql_column():
    client = app.test_client()
    content = "nombre,sql\nreporte,SELECT prioridad FROM incidencias;\n"
    data = {
        "file": (io.BytesIO(content.encode("utf-8")), "consulta.csv")
    }
    response = client.post("/api/upload", data=data, content_type="multipart/form-data")
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["valid"] is True
    assert payload["sql"] == "SELECT prioridad FROM incidencias;"


def test_pdf_report_endpoint_returns_pdf():
    client = app.test_client()
    response = client.post("/api/report", json={"sql": "SELECT prioridad FROM incidencias;"})
    assert response.status_code == 200
    assert response.mimetype == "application/pdf"
    assert response.data[:4] == b"%PDF"
