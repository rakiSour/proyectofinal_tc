# Catálogo formal de tokens

Este catálogo define la clasificación léxica usada por el proyecto. En la interfaz web, cada token muestra su tipo, lexema reconocido y expresión regular asociada. Se omitieron las columnas de línea y columna porque el objetivo de la tabla es evidenciar la clasificación formal del lexema.

| Tipo | Expresión regular | Descripción | Ejemplos |
|---|---|---|---|
| `KEYWORD` | `(?i)\b(SELECT|FROM|WHERE|GROUP|BY|ORDER|ASC|DESC|LIMIT|AS|AND|OR|NOT|JOIN|INNER|LEFT|RIGHT|FULL|ON|HAVING|COUNT|SUM|AVG|MIN|MAX|DISTINCT|IN|LIKE|IS|NULL)\b` | Palabras reservadas SQL reconocidas por la gramática. | `SELECT`, `FROM`, `WHERE`, `GROUP`, `BY`, `ORDER`, `LIMIT`, `JOIN` |
| `IDENTIFIER` | `[A-Za-z_][A-Za-z0-9_$]*` | Nombres de tablas, columnas o alias. | `ventas`, `cliente_id`, `c.nombre` |
| `NUMBER` | `\d+(\.\d+)?` | Valores numéricos enteros o decimales. | `10`, `1500.50` |
| `STRING` | `'([^']|'')*'` | Literales de texto entre comillas simples. | `'ACTIVO'`, `'2026-01-01'` |
| `OPERATOR` | `<=|>=|!=|<>|=|<|>|\+|-|\*|/` | Operadores comparativos o aritméticos. | `=`, `>=`, `<>`, `*` |
| `PUNCTUATION` | `[,\.\(\);]` | Delimitadores de estructura. | `,`, `.`, `(`, `)`, `;` |
| `EOF` | `\Z` | Marca interna de fin de entrada. | `<EOF>` |

## Palabras reservadas soportadas

`SELECT`, `FROM`, `WHERE`, `GROUP`, `BY`, `ORDER`, `ASC`, `DESC`, `LIMIT`, `AS`, `AND`, `OR`, `NOT`, `JOIN`, `INNER`, `LEFT`, `RIGHT`, `FULL`, `ON`, `HAVING`, `COUNT`, `SUM`, `AVG`, `MIN`, `MAX`, `DISTINCT`, `IN`, `LIKE`, `IS`, `NULL`.
