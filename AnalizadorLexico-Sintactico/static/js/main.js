const sqlInput = document.getElementById("sqlInput");
const analyzeBtn = document.getElementById("analyzeBtn");
const clearBtn = document.getElementById("clearBtn");
const copyBtn = document.getElementById("copyBtn");
const pdfBtn = document.getElementById("pdfBtn");
const uploadBtn = document.getElementById("uploadBtn");
const automatonBtn = document.getElementById("automatonBtn");
const treeBtn = document.getElementById("treeBtn");
const fileInput = document.getElementById("fileInput");
const exampleSelect = document.getElementById("exampleSelect");
const statusCard = document.getElementById("statusCard");
const tokensTableBody = document.querySelector("#tokensTable tbody");
const jsonOutput = document.getElementById("jsonOutput");
const grammarList = document.getElementById("grammarList");
const automatonCard = document.getElementById("automatonCard");
const treeCard = document.getElementById("treeCard");
const automatonDiagram = document.getElementById("automatonDiagram");
const treeDiagram = document.getElementById("treeDiagram");

const DEFAULT_SQL = `SELECT prioridad, COUNT(*) AS total_incidencias
FROM incidencias
WHERE estado = 'ABIERTO'
GROUP BY prioridad
ORDER BY total_incidencias DESC
LIMIT 10;`;

const DEFAULT_AUTOMATON = {
    type: "AFD",
    states: [
        {id: "q0", label: "q0\nInicio", start: true, accept: false},
        {id: "qID", label: "qID\nKEYWORD / IDENTIFIER", accept: true},
        {id: "qNUM", label: "qNUM\nNUMBER", accept: true},
        {id: "qSTR", label: "qSTR\nLeyendo STRING", accept: false},
        {id: "qSTR_OK", label: "qSTR_OK\nSTRING", accept: true},
        {id: "qOP", label: "qOP\nOPERATOR", accept: true},
        {id: "qPUNC", label: "qPUNC\nPUNCTUATION", accept: true},
        {id: "qERR", label: "qERR\nError léxico", accept: false},
    ],
    transitions: [
        {from: "q0", to: "q0", label: "espacio / salto de línea"},
        {from: "q0", to: "qID", label: "letra o _"},
        {from: "qID", to: "qID", label: "letra, dígito, _ o $"},
        {from: "q0", to: "qNUM", label: "dígito"},
        {from: "qNUM", to: "qNUM", label: "dígito o . decimal"},
        {from: "q0", to: "qSTR", label: "'"},
        {from: "qSTR", to: "qSTR", label: "carácter o '' escapado"},
        {from: "qSTR", to: "qSTR_OK", label: "' de cierre"},
        {from: "q0", to: "qOP", label: "=, <, >, <=, >=, !=, <>, +, -, *, /"},
        {from: "q0", to: "qPUNC", label: ", . ( ) ;"},
        {from: "q0", to: "qERR", label: "otro carácter"},
    ]
};

sqlInput.value = DEFAULT_SQL;
let lastAnalysisResult = null;
let lastAnalyzedSql = "";

function setStatus(type, message) {
    statusCard.className = `status status--${type}`;
    statusCard.innerHTML = `<strong>Estado:</strong> ${message}`;
}

function renderTokens(tokens) {
    tokensTableBody.innerHTML = "";
    if (!tokens || tokens.length === 0) {
        tokensTableBody.innerHTML = `<tr><td colspan="4" class="muted">No se generaron tokens.</td></tr>`;
        return;
    }

    tokens.forEach((token, index) => {
        const row = document.createElement("tr");
        const typeText = token.subtype ? `${token.type} (${token.subtype})` : token.type;
        row.innerHTML = `
            <td>${index + 1}</td>
            <td>${escapeHtml(typeText)}</td>
            <td><code>${escapeHtml(token.value)}</code></td>
            <td><code>${escapeHtml(token.regex || "-")}</code></td>
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

async function analyzeSql(showProgress = true) {
    const sql = sqlInput.value;
    if (showProgress) {
        analyzeBtn.disabled = true;
        analyzeBtn.textContent = "Analizando...";
    }

    try {
        const response = await fetch("/api/analyze", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({sql})
        });
        const data = await response.json();
        lastAnalysisResult = data;
        lastAnalyzedSql = sql;

        renderTokens(data.tokens || []);
        renderGrammar(data.grammar || []);
        renderJson(data.valid ? data.structured_json : data);

        if (data.valid) {
            setStatus("success", "Consulta aceptada. Se completó el análisis léxico, análisis sintáctico y transformación a JSON para el área de TI.");
            if (!treeCard.classList.contains("is-hidden")) {
                renderTreeDiagram(data.parse_tree);
            }
        } else {
            const error = data.errors && data.errors[0] ? data.errors[0] : {message: data.message || "Error desconocido."};
            const detail = error.line ? ` Línea ${error.line}, columna ${error.column}.` : "";
            setStatus("error", `${escapeHtml(error.message)}${detail}`);
            renderTreeDiagram(null);
        }
        return data;
    } catch (error) {
        setStatus("error", "No se pudo conectar con el servicio de análisis.");
        renderJson({error: error.message});
        return null;
    } finally {
        if (showProgress) {
            analyzeBtn.disabled = false;
            analyzeBtn.textContent = "Analizar consulta";
        }
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
        lastAnalysisResult = null;
        lastAnalyzedSql = "";
        renderTokens([]);
        renderJson({});
        renderTreeDiagram(null);
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
        setStatus("success", "Reporte PDF generado correctamente. El archivo incluye la consulta, tokens, expresiones regulares y traducción a JSON.");
    } catch (error) {
        setStatus("error", "No se pudo generar el reporte PDF.");
    } finally {
        pdfBtn.disabled = false;
        pdfBtn.textContent = "Generar reporte PDF";
    }
}

function multilineSvgText(label, x, y, cssClass = "node-label") {
    const lines = String(label).split("\n");
    const startY = y - ((lines.length - 1) * 8);
    return lines.map((line, index) =>
        `<text class="${cssClass}" x="${x}" y="${startY + (index * 16)}">${escapeHtml(line)}</text>`
    ).join("");
}

function renderAutomatonDiagram(model = DEFAULT_AUTOMATON) {
    const positions = {
        q0: {x: 100, y: 230},
        qID: {x: 330, y: 90},
        qNUM: {x: 330, y: 230},
        qSTR: {x: 330, y: 370},
        qSTR_OK: {x: 590, y: 370},
        qOP: {x: 590, y: 90},
        qPUNC: {x: 590, y: 230},
        qERR: {x: 820, y: 230},
    };

    const transitions = model.transitions || DEFAULT_AUTOMATON.transitions;
    const states = model.states || DEFAULT_AUTOMATON.states;

    const lines = transitions.map((transition, index) => {
        const from = positions[transition.from];
        const to = positions[transition.to];
        if (!from || !to) return "";

        if (transition.from === transition.to) {
            const loopY = from.y - 70;
            return `
                <path class="edge" d="M ${from.x - 30} ${from.y - 36} C ${from.x - 90} ${loopY}, ${from.x + 90} ${loopY}, ${from.x + 30} ${from.y - 36}" />
                <text class="edge-label" x="${from.x}" y="${loopY - 8}">${escapeHtml(transition.label)}</text>
            `;
        }

        const dx = to.x - from.x;
        const dy = to.y - from.y;
        const length = Math.sqrt(dx * dx + dy * dy) || 1;
        const offset = 46;
        const x1 = from.x + (dx / length) * offset;
        const y1 = from.y + (dy / length) * offset;
        const x2 = to.x - (dx / length) * offset;
        const y2 = to.y - (dy / length) * offset;
        const labelX = (x1 + x2) / 2;
        const labelY = (y1 + y2) / 2 - (index % 2 === 0 ? 12 : -16);
        return `
            <line class="edge" x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" />
            <text class="edge-label" x="${labelX}" y="${labelY}">${escapeHtml(transition.label)}</text>
        `;
    }).join("");

    const nodes = states.map(state => {
        const pos = positions[state.id];
        if (!pos) return "";
        const acceptCircle = state.accept ? `<circle class="state state-accept-inner" cx="${pos.x}" cy="${pos.y}" r="40" />` : "";
        const startArrow = state.start ? `<line class="edge" x1="20" y1="${pos.y}" x2="${pos.x - 52}" y2="${pos.y}" /><text class="edge-label" x="42" y="${pos.y - 12}">inicio</text>` : "";
        return `
            ${startArrow}
            <circle class="state ${state.accept ? 'state-accept' : ''} ${state.id === 'qERR' ? 'state-error' : ''}" cx="${pos.x}" cy="${pos.y}" r="46" />
            ${acceptCircle}
            ${multilineSvgText(state.label, pos.x, pos.y)}
        `;
    }).join("");

    automatonDiagram.innerHTML = `
        <svg class="diagram-svg" viewBox="0 0 920 470" role="img" aria-label="Diagrama de autómata finito determinista">
            <defs>
                <marker id="arrow" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto" markerUnits="strokeWidth">
                    <path d="M0,0 L0,6 L9,3 z" class="arrow-head"></path>
                </marker>
            </defs>
            ${lines}
            ${nodes}
        </svg>
    `;
}

function countLeaves(node) {
    if (!node || !node.children || node.children.length === 0) return 1;
    return node.children.reduce((total, child) => total + countLeaves(child), 0);
}

function assignTreePositions(node, depth, state) {
    node.depth = depth;
    if (!node.children || node.children.length === 0) {
        node.x = state.nextX;
        state.nextX += state.horizontalGap;
    } else {
        node.children.forEach(child => assignTreePositions(child, depth + 1, state));
        node.x = (node.children[0].x + node.children[node.children.length - 1].x) / 2;
    }
    node.y = state.top + depth * state.verticalGap;
    state.maxDepth = Math.max(state.maxDepth, depth);
}

function treeEdges(node) {
    if (!node.children || node.children.length === 0) return "";
    return node.children.map(child => `
        <line class="tree-edge" x1="${node.x}" y1="${node.y + 26}" x2="${child.x}" y2="${child.y - 26}" />
        ${treeEdges(child)}
    `).join("");
}

function treeNodes(node) {
    const label = String(node.label || "Nodo");
    const width = Math.max(130, Math.min(260, label.length * 7 + 34));
    const height = label.length > 28 ? 56 : 42;
    const safeLabel = label.length > 52 ? `${label.slice(0, 49)}...` : label;
    const labelLines = splitLabel(safeLabel, 28);
    return `
        <rect class="tree-node" x="${node.x - width / 2}" y="${node.y - height / 2}" width="${width}" height="${height}" rx="12" />
        ${labelLines.map((line, index) => `<text class="tree-label" x="${node.x}" y="${node.y - ((labelLines.length - 1) * 8) + index * 16}">${escapeHtml(line)}</text>`).join("")}
        ${(node.children || []).map(child => treeNodes(child)).join("")}
    `;
}

function splitLabel(label, maxLength) {
    if (label.length <= maxLength) return [label];
    const words = label.split(" ");
    const lines = [];
    let current = "";
    words.forEach(word => {
        const test = current ? `${current} ${word}` : word;
        if (test.length > maxLength && current) {
            lines.push(current);
            current = word;
        } else {
            current = test;
        }
    });
    if (current) lines.push(current);
    return lines.slice(0, 2);
}

function renderTreeDiagram(tree) {
    if (!tree) {
        treeDiagram.innerHTML = `<div class="empty-diagram">Primero analiza una consulta válida para generar el árbol sintáctico.</div>`;
        return;
    }

    const treeCopy = JSON.parse(JSON.stringify(tree));
    const leafCount = countLeaves(treeCopy);
    const state = {nextX: 90, horizontalGap: 170, verticalGap: 105, top: 60, maxDepth: 0};
    assignTreePositions(treeCopy, 0, state);
    const width = Math.max(760, leafCount * state.horizontalGap + 120);
    const height = state.top + (state.maxDepth + 1) * state.verticalGap + 50;

    treeDiagram.innerHTML = `
        <svg class="diagram-svg tree-svg" viewBox="0 0 ${width} ${height}" role="img" aria-label="Diagrama de árbol sintáctico">
            <defs>
                <marker id="arrow" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto" markerUnits="strokeWidth">
                    <path d="M0,0 L0,6 L9,3 z" class="arrow-head"></path>
                </marker>
            </defs>
            ${treeEdges(treeCopy)}
            ${treeNodes(treeCopy)}
        </svg>
    `;
}

function toggleCard(card) {
    card.classList.toggle("is-hidden");
    if (!card.classList.contains("is-hidden")) {
        card.scrollIntoView({behavior: "smooth", block: "start"});
    }
}

async function showParseTree() {
    if (!lastAnalysisResult || lastAnalyzedSql !== sqlInput.value) {
        const data = await analyzeSql(true);
        if (!data || !data.valid) {
            treeCard.classList.remove("is-hidden");
            renderTreeDiagram(null);
            return;
        }
    }

    treeCard.classList.remove("is-hidden");
    renderTreeDiagram(lastAnalysisResult.parse_tree);
    treeCard.scrollIntoView({behavior: "smooth", block: "start"});
}

analyzeBtn.addEventListener("click", () => analyzeSql(true));
uploadBtn.addEventListener("click", uploadFile);
pdfBtn.addEventListener("click", generatePdfReport);
automatonBtn.addEventListener("click", () => {
    renderAutomatonDiagram(lastAnalysisResult?.automaton || DEFAULT_AUTOMATON);
    toggleCard(automatonCard);
});
treeBtn.addEventListener("click", showParseTree);

clearBtn.addEventListener("click", () => {
    sqlInput.value = "";
    fileInput.value = "";
    lastAnalysisResult = null;
    lastAnalyzedSql = "";
    renderTokens([]);
    renderJson({});
    renderTreeDiagram(null);
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
    lastAnalysisResult = null;
    lastAnalyzedSql = "";
    renderTreeDiagram(null);
});
