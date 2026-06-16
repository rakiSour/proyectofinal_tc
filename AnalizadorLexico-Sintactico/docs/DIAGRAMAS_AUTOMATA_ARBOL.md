# Diagramas incorporados en la aplicación

## Autómata Finito Determinista

Para el analizador léxico se implementó un **AFD**. Esta elección se justifica porque los tokens SQL del proyecto se reconocen mediante expresiones regulares y, durante la lectura de la consulta, cada carácter pertenece a una clase léxica determinada: letra, dígito, comilla, operador, puntuación, espacio u otro carácter.

Estados principales:

| Estado | Significado |
|---|---|
| `q0` | Estado inicial. Lee espacios, saltos de línea o decide el tipo de lexema. |
| `qID` | Reconoce palabras reservadas e identificadores. |
| `qNUM` | Reconoce números enteros y decimales. |
| `qSTR` | Procesa cadenas entre comillas simples. |
| `qSTR_OK` | Estado de aceptación para cadenas válidas. |
| `qOP` | Reconoce operadores. |
| `qPUNC` | Reconoce signos de puntuación. |
| `qERR` | Estado de error léxico. |

## Árbol sintáctico

El árbol sintáctico se genera luego de validar una consulta `SELECT`. Representa gráficamente la estructura aceptada por la gramática formal: campos seleccionados, tabla origen, joins, condiciones, agrupaciones, ordenamientos y límite.

El botón **Mostrar árbol sintáctico** ejecuta el análisis de la consulta actual y, si la sentencia es válida, construye el árbol a partir de la estructura JSON generada por el parser.
