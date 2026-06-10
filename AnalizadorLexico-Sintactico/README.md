# Analizador léxico-sintáctico SQL a JSON estructurado

Proyecto universitario para el curso de **Teoría de la Computación**.

**Tema:** Implementación de un analizador léxico-sintáctico para la validación y transformación de consultas SQL a formato JSON estructurado en la gestión de el área de TI.

## Tecnologías

- Python 3.11+
- Flask
- HTML, CSS y JavaScript
- Pytest para pruebas
- Gunicorn para despliegue

## Funcionalidades

- Analiza consultas `SELECT` orientadas a el área de TI.
- Clasifica tokens léxicos: palabras reservadas, identificadores, números, cadenas, operadores y signos de puntuación.
- Valida sintácticamente una gramática formal simplificada de SQL.
- Transforma consultas válidas a JSON estructurado.
- Muestra errores léxicos y sintácticos con línea y columna.
- Incluye interfaz web con ejemplos, tabla de tokens y visualización del JSON.


## Mejoras incorporadas por feedback docente

- Cambio de enfoque del texto principal: la transformación JSON ahora se orienta al área de TI.
- Carga de consultas SQL desde archivos `.txt` o `.csv`.
- Generación de reporte PDF con la consulta evaluada, tokens léxicos y traducción a JSON estructurado.

### Formato recomendado para archivos CSV

El sistema acepta un CSV con una columna llamada `sql`, `consulta`, `query` o `sentencia`. Ejemplo:

```csv
nombre,sql
Reporte de incidencias,SELECT prioridad, COUNT(*) AS total FROM incidencias GROUP BY prioridad;
```

## Estructura del proyecto

```text
sql_json_analyzer_flask/
├── app.py
├── core/
│   ├── analyzer.py
│   ├── lexer.py
│   └── parser.py
├── templates/
│   └── index.html
├── static/
│   ├── css/styles.css
│   └── js/main.js
├── docs/
│   ├── CATALOGO_TOKENS.md
│   ├── GRAMATICA_BNF.md
│   └── CASOS_PRUEBA.md
├── tests/
│   └── test_analyzer.py
├── requirements.txt
├── Procfile
├── render.yaml
└── runtime.txt
```

## Instalación local en PyCharm

1. Abrir la carpeta del proyecto en PyCharm.
2. Crear un entorno virtual.
3. Instalar dependencias:

```bash
pip install -r requirements.txt
```

4. Ejecutar la aplicación:

```bash
python app.py
```

5. Abrir en el navegador:

```text
http://127.0.0.1:5000
```

## Uso de la API

Endpoint:

```text
POST /api/analyze
```

Body:

```json
{
  "sql": "SELECT categoria, SUM(total) AS total_ventas FROM ventas GROUP BY categoria;"
}
```

Respuesta válida:

```json
{
  "valid": true,
  "stage": "accepted",
  "tokens": [],
  "structured_json": {
    "operation": "SELECT",
    "distinct": false,
    "fields": [],
    "from": {},
    "joins": [],
    "where": null,
    "group_by": [],
    "having": null,
    "order_by": [],
    "limit": null
  },
  "errors": []
}
```

## Ejecución de pruebas

```bash
python -m pytest
```

## Subida a GitHub

```bash
git init
git add .
git commit -m "Implementación inicial del analizador SQL a JSON"
git branch -M main
git remote add origin https://github.com/TU_USUARIO/TU_REPOSITORIO.git
git push -u origin main
```

## Despliegue en Render

El proyecto incluye:

- `Procfile`
- `render.yaml`
- `requirements.txt`
- `runtime.txt`

Configuración recomendada para un Web Service:

```text
Build Command: pip install -r requirements.txt
Start Command: gunicorn app:app
```

## Ejemplo de consulta válida

```sql
SELECT categoria, SUM(total) AS total_ventas
FROM ventas
WHERE fecha >= '2026-01-01' AND estado = 'CERRADO'
GROUP BY categoria
ORDER BY total_ventas DESC
LIMIT 10;
```

## Limitaciones del prototipo

Este prototipo valida un subconjunto controlado de SQL para fines académicos. No implementa subconsultas, CTE, `INSERT`, `UPDATE`, `DELETE`, funciones avanzadas ni conexión a una base de datos real. La finalidad principal es evidenciar las fases de análisis léxico, análisis sintáctico y traducción estructurada a JSON.
