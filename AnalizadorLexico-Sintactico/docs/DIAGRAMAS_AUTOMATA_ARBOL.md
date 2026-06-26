# Diagramas formales implementados

## 1. Gramática Libre de Contexto

La aplicación incluye un apartado visible denominado **Gramática Libre de Contexto**. Este apartado lista las producciones usadas por el parser descendente recursivo para validar consultas `SELECT`.

La GLC principal es:

```bnf
<consulta> ::= SELECT [DISTINCT] <lista_seleccion> FROM <tabla> [<joins>] [WHERE <condicion>] [GROUP BY <campos>] [HAVING <condicion>] [ORDER BY <orden>] [LIMIT <numero>] [;]
<lista_seleccion> ::= <item_seleccion> (, <item_seleccion>)*
<item_seleccion> ::= * | <identificador> [<alias>] | <funcion_agregada> '(' (* | <identificador>) ')' [<alias>]
<tabla> ::= <identificador> [<alias>]
<join> ::= [INNER | LEFT | RIGHT | FULL] JOIN <tabla> ON <condicion>
<condicion> ::= <predicado> ((AND | OR) <predicado>)*
<predicado> ::= <operando> <operador_comparacion> <operando> | <operando> LIKE <operando> | <operando> IN '(' <lista_valores> ')' | <operando> IS [NOT] NULL
<orden> ::= <identificador> [ASC | DESC] (, <identificador> [ASC | DESC])*
```

## 2. Botones por lexema

Cada fila de la tabla de tokens incluye acciones formales:

- **AFND:** muestra el Autómata Finito No Determinista asociado al tipo de token del lexema.
- **AFD:** muestra el Autómata Finito Determinista asociado al tipo de token del lexema.
- **Tabla:** muestra la tabla de transición del token.
- **GLC:** muestra la Gramática Libre de Contexto usada para validar la consulta completa.
- **Árbol:** muestra el árbol sintáctico de la consulta SQL válida.

## 3. AFND y AFD

Se incluyeron modelos específicos para los tokens principales:

- `KEYWORD`
- `IDENTIFIER`
- `NUMBER`
- `STRING`
- `OPERATOR`
- `PUNCTUATION`
- `EOF`

El **AFND** se usa para explicar la construcción conceptual desde expresiones regulares, especialmente por alternativas y transiciones epsilon. El **AFD** representa la versión determinista usada para el reconocimiento práctico de lexemas dentro del analizador léxico.

## 4. Tabla de transición

Cada token cuenta con una tabla de transición con:

- Estado actual.
- Símbolo o entrada.
- Estado siguiente.
- Observación.

## 5. Árbol sintáctico

El árbol sintáctico se genera desde el JSON estructurado resultante del parser. Sus nodos representan cláusulas SQL como `SELECT`, `FROM`, `WHERE`, `GROUP BY`, `HAVING`, `ORDER BY` y `LIMIT`.

## 6. Reporte PDF

El reporte PDF fue ajustado para evitar overflow. Se usa orientación horizontal, tablas con ajuste automático de texto y celdas envolventes para tokens, expresiones regulares, JSON y producciones de la gramática.
