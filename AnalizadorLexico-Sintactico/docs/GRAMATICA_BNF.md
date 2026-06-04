# Gramática formal simplificada para consultas SELECT

La solución implementa un subconjunto de SQL orientado a reportería gerencial. La gramática se expresa en una notación cercana a BNF/EBNF.

```bnf
<consulta> ::= SELECT [DISTINCT] <lista_seleccion> FROM <tabla>
               {<join>}
               [WHERE <condicion>]
               [GROUP BY <lista_identificadores>]
               [HAVING <condicion>]
               [ORDER BY <lista_orden>]
               [LIMIT <numero>]
               [;]

<lista_seleccion> ::= <item_seleccion> {, <item_seleccion>}

<item_seleccion> ::= *
                   | <identificador> [<alias>]
                   | <funcion_agregada> ( [DISTINCT] (* | <identificador>) ) [<alias>]

<funcion_agregada> ::= COUNT | SUM | AVG | MIN | MAX

<tabla> ::= <identificador> [<alias>]

<join> ::= [INNER | LEFT | RIGHT | FULL] JOIN <tabla> ON <condicion>

<condicion> ::= <termino_or>
<termino_or> ::= <termino_and> {OR <termino_and>}
<termino_and> ::= <factor> {AND <factor>}
<factor> ::= NOT <factor> | (<condicion>) | <predicado>

<predicado> ::= <operando> <operador_comparacion> <operando>
              | <operando> LIKE <operando>
              | <operando> IN (<lista_valores>)
              | <operando> IS [NOT] NULL

<operador_comparacion> ::= = | != | <> | < | > | <= | >=

<lista_orden> ::= <identificador> [ASC | DESC] {, <identificador> [ASC | DESC]}
<alias> ::= AS <identificador> | <identificador>
```

## Alcance

- Se priorizan consultas `SELECT` para reportería gerencial.
- Se reconocen columnas simples y calificadas: `columna`, `tabla.columna`.
- Se soportan agregaciones frecuentes: `COUNT`, `SUM`, `AVG`, `MIN`, `MAX`.
- Se soportan filtros con operadores comparativos, `AND`, `OR`, `NOT`, `LIKE`, `IN` e `IS NULL`.
- No se implementan subconsultas, `INSERT`, `UPDATE`, `DELETE`, CTE ni funciones SQL avanzadas, porque exceden el alcance del primer prototipo universitario.
