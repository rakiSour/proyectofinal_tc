const sqlInput = document.getElementById("sqlInput");
const analyzeBtn = document.getElementById("analyzeBtn");
const clearBtn = document.getElementById("clearBtn");
const copyBtn = document.getElementById("copyBtn");
const exampleSelect = document.getElementById("exampleSelect");
const statusCard = document.getElementById("statusCard");
const tokensTableBody = document.querySelector("#tokensTable tbody");
const jsonOutput = document.getElementById("jsonOutput");
const grammarList = document.getElementById("grammarList");

const DEFAULT_SQL = `SELECT categoria, SUM(total) AS total_ventas
FROM ventas
WHERE fecha >= '2026-01-01' AND estado = 'CERRADO'
GROUP BY categoria
ORDER BY total_ventas DESC
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
            setStatus("success", "Consulta aceptada. Se completó el análisis léxico, análisis sintáctico y transformación a JSON.");
        } else {
            const error = data.errors && data.errors[0] ? data.errors[0] : {message: "Error desconocido."};
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

analyzeBtn.addEventListener("click", analyzeSql);

clearBtn.addEventListener("click", () => {
    sqlInput.value = "";
    renderTokens([]);
    renderJson({});
    grammarList.innerHTML = `<p class="muted">Las reglas se mostrarán después del análisis.</p>`;
    setStatus("empty", "Ingresa una consulta y presiona “Analizar consulta”.");
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
