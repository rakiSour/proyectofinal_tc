const sqlInput = document.getElementById("sqlInput");
const analyzeBtn = document.getElementById("analyzeBtn");
const clearBtn = document.getElementById("clearBtn");
const copyBtn = document.getElementById("copyBtn");
const pdfBtn = document.getElementById("pdfBtn");
const uploadBtn = document.getElementById("uploadBtn");
const automatonBtn = document.getElementById("automatonBtn");
const globalAfndBtn = document.getElementById("globalAfndBtn");
const globalTransitionBtn = document.getElementById("globalTransitionBtn");
const grammarBtn = document.getElementById("grammarBtn");
const treeBtn = document.getElementById("treeBtn");
const fileInput = document.getElementById("fileInput");
const exampleSelect = document.getElementById("exampleSelect");
const statusCard = document.getElementById("statusCard");
const tokensTableBody = document.querySelector("#tokensTable tbody");
const jsonOutput = document.getElementById("jsonOutput");
const grammarList = document.getElementById("grammarList");
const grammarCard = document.getElementById("grammarCard");
const automatonCard = document.getElementById("automatonCard");
const automatonDiagram = document.getElementById("automatonDiagram");
const automatonTitle = document.getElementById("automatonTitle");
const automatonBadge = document.getElementById("automatonBadge");
const automatonDescription = document.getElementById("automatonDescription");
const treeCard = document.getElementById("treeCard");
const treeDiagram = document.getElementById("treeDiagram");
const formalDetailCard = document.getElementById("formalDetailCard");
const formalDetailBadge = document.getElementById("formalDetailBadge");
const formalDetailTitle = document.getElementById("formalDetailTitle");
const formalDetailDescription = document.getElementById("formalDetailDescription");
const formalDetailContent = document.getElementById("formalDetailContent");

const DEFAULT_SQL = `SELECT prioridad, COUNT(*) AS total_incidencias
FROM incidencias
WHERE estado = 'ABIERTO'
GROUP BY prioridad
ORDER BY total_incidencias DESC
LIMIT 10;`;

const DEFAULT_AUTOMATON = {
    name: "AFD general del analizador léxico SQL",
    type: "AFD",
    description: "Modelo determinista general para clasificar lexemas SQL.",
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
    positions: {
        q0: {x: 100, y: 230},
        qID: {x: 330, y: 90},
        qNUM: {x: 330, y: 230},
        qSTR: {x: 330, y: 370},
        qSTR_OK: {x: 590, y: 370},
        qOP: {x: 590, y: 90},
        qPUNC: {x: 590, y: 230},
        qERR: {x: 820, y: 230},
    },
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

const DEFAULT_AFND = {
    name: "AFND general del analizador léxico SQL",
    type: "AFND",
    description: "Modelo no determinista conceptual: desde q0 se bifurca mediante ε hacia ramas para reconocer cada familia de tokens.",
    states: [
        {id: "q0", label: "q0\nInicio", start: true, accept: false},
        {id: "qID", label: "rama\nID/KW", accept: true},
        {id: "qNUM", label: "rama\nNUMBER", accept: true},
        {id: "qSTR", label: "rama\nSTRING", accept: true},
        {id: "qOP", label: "rama\nOPERATOR", accept: true},
        {id: "qPUNC", label: "rama\nPUNCT", accept: true},
    ],
    positions: {
        q0: {x: 90, y: 230},
        qID: {x: 330, y: 70},
        qNUM: {x: 330, y: 150},
        qSTR: {x: 330, y: 230},
        qOP: {x: 330, y: 310},
        qPUNC: {x: 330, y: 390},
    },
    transitions: [
        {from: "q0", to: "qID", label: "ε / letra o _"},
        {from: "q0", to: "qNUM", label: "ε / dígito"},
        {from: "q0", to: "qSTR", label: "ε / '"},
        {from: "q0", to: "qOP", label: "ε / operador"},
        {from: "q0", to: "qPUNC", label: "ε / puntuación"},
        {from: "qID", to: "qID", label: "letra, dígito, _ o $"},
        {from: "qNUM", to: "qNUM", label: "dígito o ."},
        {from: "qSTR", to: "qSTR", label: "caracteres internos"},
    ]
};

const DEFAULT_TRANSITION_TABLE = [
    {state: "q0", symbol: "espacio", next: "q0", note: "Ignora espacios"},
    {state: "q0", symbol: "letra o _", next: "qID", note: "KEYWORD o IDENTIFIER"},
    {state: "qID", symbol: "letra, dígito, _ o $", next: "qID", note: "Continúa identificador"},
    {state: "q0", symbol: "dígito", next: "qNUM", note: "NUMBER"},
    {state: "qNUM", symbol: "dígito o .", next: "qNUM", note: "Continúa número"},
    {state: "q0", symbol: "'", next: "qSTR", note: "Inicio STRING"},
    {state: "qSTR", symbol: "' cierre", next: "qSTR_OK", note: "Acepta STRING"},
    {state: "q0", symbol: "operador", next: "qOP", note: "Acepta OPERATOR"},
    {state: "q0", symbol: "puntuación", next: "qPUNC", note: "Acepta PUNCTUATION"},
];

sqlInput.value = DEFAULT_SQL;
let lastAnalysisResult = null;
let lastAnalyzedSql = "";

function setStatus(type, message) {
    statusCard.className = `status status--${type}`;
    statusCard.innerHTML = `<strong>Estado:</strong> ${message}`;
}

function escapeHtml(value) {
    return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}

function getTokenModel(token) {
    const models = lastAnalysisResult?.token_automata || {};
    return models[token?.type] || null;
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
            <td>${escapeHtml(typeText)}</td>
            <td><code>${escapeHtml(token.value)}</code></td>
            <td><code>${escapeHtml(token.regex || "-")}</code></td>
            <td>
                <div class="token-actions">
                    <button class="mini-btn" type="button" data-action="afnd" data-index="${index}" title="Mostrar AFND del lexema">AFND</button>
                    <button class="mini-btn" type="button" data-action="afd" data-index="${index}" title="Mostrar AFD del lexema">AFD</button>
                    <button class="mini-btn" type="button" data-action="table" data-index="${index}" title="Mostrar tabla de transición">Tabla</button>
                    <button class="mini-btn" type="button" data-action="grammar" data-index="${index}" title="Mostrar Gramática Libre de Contexto">GLC</button>
                    <button class="mini-btn" type="button" data-action="tree" data-index="${index}" title="Mostrar árbol sintáctico">Árbol</button>
                </div>
            </td>
        `;
        tokensTableBody.appendChild(row);
    });
}

function renderGrammar(rules, highlightedToken = null) {
    grammarList.innerHTML = "";
    if (!rules || rules.length === 0) {
        grammarList.innerHTML = `<p class="muted">No hay reglas disponibles.</p>`;
        return;
    }

    const note = document.createElement("p");
    note.className = "muted";
    note.textContent = highlightedToken
        ? `Vista solicitada desde el lexema "${highlightedToken.value}" asociado al token ${highlightedToken.type}. La GLC valida la estructura sintáctica completa de la consulta.`
        : "La gramática se expresa con no terminales, terminales SQL y producciones para validar consultas SELECT.";
    grammarList.appendChild(note);

    rules.forEach((rule, index) => {
        const item = document.createElement("div");
        item.className = "grammar-rule";
        item.innerHTML = `<span class="grammar-index">${index + 1}</span><strong>${escapeHtml(rule.name)}</strong> ::= <code>${escapeHtml(rule.production)}</code>`;
        grammarList.appendChild(item);
    });
}

function renderJson(data) {
    jsonOutput.textContent = JSON.stringify(data, null, 2);
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
            setStatus("success", "Consulta aceptada. Se completó el análisis léxico, análisis sintáctico, GLC y transformación a JSON para el área de TI.");
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

async function ensureAnalysis() {
    if (!lastAnalysisResult || lastAnalyzedSql !== sqlInput.value) {
        return await analyzeSql(true);
    }
    return lastAnalysisResult;
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
        formalDetailCard.classList.add("is-hidden");
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
        setStatus("success", "Reporte PDF generado correctamente. El archivo incluye JSON, tokens, expresiones regulares y GLC con tablas ajustadas.");
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

function buildPositions(model) {
    if (model.positions) return model.positions;
    const positions = {};
    const states = model.states || [];
    states.forEach((state, index) => {
        positions[state.id] = {x: 100 + index * 190, y: 220 + (index % 2 === 0 ? 0 : -70)};
    });
    return positions;
}

function renderAutomatonInto(container, model = DEFAULT_AUTOMATON) {
    const positions = buildPositions(model);
    const transitions = model.transitions || [];
    const states = model.states || [];
    const xs = Object.values(positions).map(pos => pos.x);
    const ys = Object.values(positions).map(pos => pos.y);
    const width = Math.max(780, Math.max(...xs, 700) + 120);
    const height = Math.max(360, Math.max(...ys, 300) + 110);

    const lines = transitions.map((transition, index) => {
        const from = positions[transition.from];
        const to = positions[transition.to];
        if (!from || !to) return "";

        if (transition.from === transition.to) {
            const loopY = Math.max(38, from.y - 72 - ((index % 3) * 10));
            return `
                <path class="edge" d="M ${from.x - 30} ${from.y - 36} C ${from.x - 92} ${loopY}, ${from.x + 92} ${loopY}, ${from.x + 30} ${from.y - 36}" />
                <text class="edge-label" x="${from.x}" y="${loopY - 8}">${escapeHtml(transition.label)}</text>
            `;
        }

        const dx = to.x - from.x;
        const dy = to.y - from.y;
        const length = Math.sqrt(dx * dx + dy * dy) || 1;
        const offset = 48;
        const x1 = from.x + (dx / length) * offset;
        const y1 = from.y + (dy / length) * offset;
        const x2 = to.x - (dx / length) * offset;
        const y2 = to.y - (dy / length) * offset;
        const labelX = (x1 + x2) / 2;
        const labelY = (y1 + y2) / 2 - (index % 2 === 0 ? 14 : -18);
        return `
            <line class="edge" x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" />
            <text class="edge-label" x="${labelX}" y="${labelY}">${escapeHtml(transition.label)}</text>
        `;
    }).join("");

    const nodes = states.map(state => {
        const pos = positions[state.id];
        if (!pos) return "";
        const acceptCircle = state.accept ? `<circle class="state state-accept-inner" cx="${pos.x}" cy="${pos.y}" r="40" />` : "";
        const startArrow = state.start ? `<line class="edge" x1="18" y1="${pos.y}" x2="${pos.x - 54}" y2="${pos.y}" /><text class="edge-label" x="43" y="${pos.y - 12}">inicio</text>` : "";
        return `
            ${startArrow}
            <circle class="state ${state.accept ? 'state-accept' : ''} ${state.id === 'qERR' ? 'state-error' : ''}" cx="${pos.x}" cy="${pos.y}" r="46" />
            ${acceptCircle}
            ${multilineSvgText(state.label, pos.x, pos.y)}
        `;
    }).join("");

    container.innerHTML = `
        <svg class="diagram-svg" viewBox="0 0 ${width} ${height}" role="img" aria-label="${escapeHtml(model.name || 'Diagrama de autómata')}">
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

function showGeneralAutomaton(kind = "afd") {
    const model = kind === "afnd" ? DEFAULT_AFND : (lastAnalysisResult?.automaton || DEFAULT_AUTOMATON);
    automatonTitle.textContent = model.name || (kind === "afnd" ? "AFND general" : "AFD general");
    automatonBadge.textContent = kind === "afnd" ? "AFND" : "AFD";
    automatonDescription.textContent = model.description || "Diagrama del analizador léxico.";
    renderAutomatonInto(automatonDiagram, model);
    automatonCard.classList.remove("is-hidden");
    automatonCard.scrollIntoView({behavior: "smooth", block: "start"});
}

function renderTransitionTable(rows, token = null) {
    if (!rows || rows.length === 0) {
        return `<p class="muted">No hay transiciones disponibles para mostrar.</p>`;
    }
    const title = token ? `Tabla de transición para ${escapeHtml(token.type)} — lexema <code>${escapeHtml(token.value)}</code>` : "Tabla de transición general";
    return `
        <h3>${title}</h3>
        <div class="table-wrapper">
            <table class="transition-table">
                <thead>
                    <tr><th>Estado actual</th><th>Símbolo / entrada</th><th>Estado siguiente</th><th>Observación</th></tr>
                </thead>
                <tbody>
                    ${rows.map(row => `
                        <tr>
                            <td><code>${escapeHtml(row.state)}</code></td>
                            <td>${escapeHtml(row.symbol)}</td>
                            <td><code>${escapeHtml(row.next)}</code></td>
                            <td>${escapeHtml(row.note)}</td>
                        </tr>
                    `).join("")}
                </tbody>
            </table>
        </div>
    `;
}

function showFormalDetail(title, badge, description, html) {
    formalDetailTitle.textContent = title;
    formalDetailBadge.textContent = badge;
    formalDetailDescription.textContent = description;
    formalDetailContent.innerHTML = html;
    formalDetailCard.classList.remove("is-hidden");
    formalDetailCard.scrollIntoView({behavior: "smooth", block: "start"});
}

async function showTokenAutomaton(index, kind) {
    const data = await ensureAnalysis();
    if (!data) return;
    const token = data.tokens?.[index];
    const model = getTokenModel(token);
    if (!token || !model || !model[kind]) {
        setStatus("error", "No se encontró un modelo formal para el lexema seleccionado.");
        return;
    }
    const automaton = model[kind];
    showFormalDetail(
        `${kind.toUpperCase()} del token ${token.type}`,
        kind.toUpperCase(),
        `Lexema: ${token.value} · Expresión regular: ${token.regex || model.regex}`,
        `<div id="selectedAutomatonCanvas"></div>`
    );
    renderAutomatonInto(document.getElementById("selectedAutomatonCanvas"), automaton);
}

async function showTokenTransitionTable(index) {
    const data = await ensureAnalysis();
    if (!data) return;
    const token = data.tokens?.[index];
    const model = getTokenModel(token);
    if (!token || !model) {
        setStatus("error", "No se encontró una tabla de transición para el lexema seleccionado.");
        return;
    }
    showFormalDetail(
        `Tabla de transición del token ${token.type}`,
        "Tabla de transición",
        `Lexema: ${token.value} · Expresión regular: ${token.regex || model.regex}`,
        renderTransitionTable(model.transition_table, token)
    );
}

async function showGrammarForToken(index = null) {
    const data = await ensureAnalysis();
    if (!data) return;
    const token = Number.isInteger(index) ? data.tokens?.[index] : null;
    renderGrammar(data.grammar || [], token);
    grammarCard.classList.remove("is-hidden");
    grammarCard.scrollIntoView({behavior: "smooth", block: "start"});
}

function showGeneralTransitionTable() {
    showFormalDetail(
        "Tabla de transición general",
        "Tabla de transición",
        "Resume las transiciones principales del AFD general del analizador léxico.",
        renderTransitionTable(DEFAULT_TRANSITION_TABLE)
    );
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

async function showParseTree() {
    const data = await ensureAnalysis();
    if (!data || !data.valid) {
        treeCard.classList.remove("is-hidden");
        renderTreeDiagram(null);
        return;
    }

    treeCard.classList.remove("is-hidden");
    renderTreeDiagram(data.parse_tree);
    treeCard.scrollIntoView({behavior: "smooth", block: "start"});
}

analyzeBtn.addEventListener("click", () => analyzeSql(true));
uploadBtn.addEventListener("click", uploadFile);
pdfBtn.addEventListener("click", generatePdfReport);
automatonBtn.addEventListener("click", async () => {
    await ensureAnalysis();
    showGeneralAutomaton("afd");
});
globalAfndBtn.addEventListener("click", async () => {
    await ensureAnalysis();
    showGeneralAutomaton("afnd");
});
globalTransitionBtn.addEventListener("click", showGeneralTransitionTable);
grammarBtn.addEventListener("click", () => showGrammarForToken(null));
treeBtn.addEventListener("click", showParseTree);

tokensTableBody.addEventListener("click", async (event) => {
    const button = event.target.closest("button[data-action]");
    if (!button) return;
    const action = button.dataset.action;
    const index = Number(button.dataset.index);

    if (action === "afnd") return showTokenAutomaton(index, "afnd");
    if (action === "afd") return showTokenAutomaton(index, "afd");
    if (action === "table") return showTokenTransitionTable(index);
    if (action === "grammar") return showGrammarForToken(index);
    if (action === "tree") return showParseTree();
});

clearBtn.addEventListener("click", () => {
    sqlInput.value = "";
    fileInput.value = "";
    lastAnalysisResult = null;
    lastAnalyzedSql = "";
    renderTokens([]);
    renderJson({});
    renderTreeDiagram(null);
    formalDetailCard.classList.add("is-hidden");
    automatonCard.classList.add("is-hidden");
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
    formalDetailCard.classList.add("is-hidden");
});
