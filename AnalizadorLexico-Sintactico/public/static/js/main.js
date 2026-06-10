const sqlInput = document.getElementById("sqlInput");
const analyzeBtn = document.getElementById("analyzeBtn");
const clearBtn = document.getElementById("clearBtn");
const copyBtn = document.getElementById("copyBtn");
const pdfBtn = document.getElementById("pdfBtn");
const uploadBtn = document.getElementById("uploadBtn");
const fileInput = document.getElementById("fileInput");
const exampleSelect = document.getElementById("exampleSelect");
const statusCard = document.getElementById("statusCard");
const tokensTableBody = document.querySelector("#tokensTable tbody");
const jsonOutput = document.getElementById("jsonOutput");
const grammarList = document.getElementById("grammarList");

const DEFAULT_SQL = `SELECT prioridad, COUNT(*) AS total_incidencias
FROM incidencias
WHERE estado = 'ABIERTO'
GROUP BY prioridad
ORDER BY total_incidencias DESC
LIMIT 10;`;

sqlInput.value = DEFAULT_SQL;

function setStatus(type, message) {
    statusCard.className = `status status--${type}`;
    statusCard.innerHTML = `<strong>Estado:</strong> ${message}`;
}

function renderTokens(tokens) {
    tokensTableBody.innerHTML = "";
    if (!tokens || tokens.length === 0) {
        tokensTableBody.innerHTML = `<tr><td colspan="5" class="muted">No se generaron tokens.</td></tr>`;
        return;
    }

    tokens.forEach((token, index) => {
        const row = document.createElement("tr");
        const typeText = token.subtype ? `${token.type} (${token.subtype})` : token.type;
        row.innerHTML = `
            <td>${index + 1}</td>
            <td>${typeText}</td>
            <td><code>${escapeHtml(token.value)}</code></td>
            <td>${token.line}</td>
            <td>${token.column}</td>
        `;
        tokensTableBody.appendChild(row);
    });
}

function renderGrammar(rules) {
    grammarList.innerHTML = "";
    if (!rules || rules.length === 0) {
        grammarList.innerHTML = `<p class="muted">No hay reglas disponibles.</p>`;
        return;
    }

    rules.forEach(rule => {
        const item = document.createElement("div");
        item.className = "grammar-rule";
        item.innerHTML = `<strong>${escapeHtml(rule.name)}</strong> ::= <code>${escapeHtml(rule.production)}</code>`;
        grammarList.appendChild(item);
    });
}

function renderJson(data) {
    jsonOutput.textContent = JSON.stringify(data, null, 2);
}

function escapeHtml(value) {
    return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}

async function analyzeSql() {
    const sql = sqlInput.value;
    analyzeBtn.disabled = true;
    analyzeBtn.textContent = "Analizando...";

    try {
        const response = await fetch("/api/analyze", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({sql})
        });
        const data = await response.json();

        renderTokens(data.tokens || []);
        renderGrammar(data.grammar || []);
        renderJson(data.valid ? data.structured_json : data);

        if (data.valid) {
            setStatus("success", "Consulta aceptada. Se completó el análisis léxico, análisis sintáctico y transformación a JSON para el área de TI.");
        } else {
            const error = data.errors && data.errors[0] ? data.errors[0] : {message: data.message || "Error desconocido."};
            const detail = error.line ? ` Línea ${error.line}, columna ${error.column}.` : "";
            setStatus("error", `${escapeHtml(error.message)}${detail}`);
        }
    } catch (error) {
        setStatus("error", "No se pudo conectar con el servicio de análisis.");
        renderJson({error: error.message});
    } finally {
        analyzeBtn.disabled = false;
        analyzeBtn.textContent = "Analizar consulta";
    }
}

async function uploadFile() {
    const file = fileInput.files[0];
    if (!file) {
        setStatus("error", "Selecciona un archivo TXT o CSV antes de cargarlo.");
        return;
    }

    const formData = new FormData();
    formData.append("file", file);
    uploadBtn.disabled = true;
    uploadBtn.textContent = "Cargando...";

    try {
        const response = await fetch("/api/upload", {
            method: "POST",
            body: formData
        });
        const data = await response.json();

        if (!response.ok || !data.valid) {
            setStatus("error", escapeHtml(data.message || "No se pudo cargar el archivo."));
            return;
        }

        sqlInput.value = data.sql;
        renderTokens([]);
        renderJson({});
        grammarList.innerHTML = `<p class="muted">Las reglas se mostrarán después del análisis.</p>`;
        setStatus("success", `Archivo ${escapeHtml(data.filename)} cargado correctamente. Ahora puedes analizar la consulta o generar el reporte PDF.`);
    } catch (error) {
        setStatus("error", "No se pudo cargar el archivo seleccionado.");
    } finally {
        uploadBtn.disabled = false;
        uploadBtn.textContent = "Cargar archivo";
    }
}

async function generatePdfReport() {
    const sql = sqlInput.value;
    pdfBtn.disabled = true;
    pdfBtn.textContent = "Generando PDF...";

    try {
        const response = await fetch("/api/report", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({sql})
        });

        if (!response.ok) {
            setStatus("error", "No se pudo generar el reporte PDF.");
            return;
        }

        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = url;
        link.download = "reporte_sql_json.pdf";
        document.body.appendChild(link);
        link.click();
        link.remove();
        URL.revokeObjectURL(url);
        setStatus("success", "Reporte PDF generado correctamente. El archivo incluye la consulta, tokens y traducción a JSON.");
    } catch (error) {
        setStatus("error", "No se pudo generar el reporte PDF.");
    } finally {
        pdfBtn.disabled = false;
        pdfBtn.textContent = "Generar reporte PDF";
    }
}

analyzeBtn.addEventListener("click", analyzeSql);
uploadBtn.addEventListener("click", uploadFile);
pdfBtn.addEventListener("click", generatePdfReport);

clearBtn.addEventListener("click", () => {
    sqlInput.value = "";
    fileInput.value = "";
    renderTokens([]);
    renderJson({});
    grammarList.innerHTML = `<p class="muted">Las reglas se mostrarán después del análisis.</p>`;
    setStatus("empty", "Ingresa una consulta, carga un archivo TXT/CSV o presiona “Analizar consulta”.");
});

copyBtn.addEventListener("click", async () => {
    await navigator.clipboard.writeText(jsonOutput.textContent);
    copyBtn.textContent = "Copiado";
    setTimeout(() => copyBtn.textContent = "Copiar JSON", 1200);
});

exampleSelect.addEventListener("change", () => {
    const selectedIndex = exampleSelect.value;
    if (selectedIndex === "") return;
    sqlInput.value = window.EXAMPLES[Number(selectedIndex)].sql;
});
