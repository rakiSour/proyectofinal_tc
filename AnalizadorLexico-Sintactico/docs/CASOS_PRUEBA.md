# Casos de prueba sugeridos

| ID | Consulta | Resultado esperado |
|---|---|---|
| CP-01 | `SELECT nombre FROM clientes;` | Consulta válida. JSON con un campo y tabla `clientes`. |
| CP-02 | `SELECT categoria, SUM(total) AS total_ventas FROM ventas WHERE estado = 'CERRADO' GROUP BY categoria;` | Consulta válida. JSON con agregación y cláusula `GROUP BY`. |
| CP-03 | `SELECT c.nombre, COUNT(*) AS total FROM clientes c INNER JOIN pedidos p ON c.id = p.cliente_id GROUP BY c.nombre;` | Consulta válida. JSON con `JOIN`. |
| CP-04 | `SELECT nombre, total WHERE total > 100;` | Error sintáctico porque falta `FROM`. |
| CP-05 | `SELECT nombre FROM clientes @;` | Error léxico por carácter no reconocido. |
| CP-06 | `SELECT nombre FROM clientes WHERE estado = 'ACTIVO;` | Error léxico por cadena sin cierre. |

Para ejecutar las pruebas automatizadas:

```bash
python -m pytest
```
