# QA Leadership Challenge – Detektor

**Prueba técnica take-home v3.1 · Fábrica de Software Detektor**  
**Candidata:** Kelly Lorraine Vargas Cordero  
**Fecha de documentación:** 24/11/2026  
**Entorno:** laboratorio ficticio; no utilizar en producción.

## 1. Objetivo y alcance

Evaluar el contrato funcional de una API de telemetría que registra y consulta eventos GPS de varios clientes. El trabajo cubre tres pruebas automatizadas nuevas, la reproducción de defectos, la corrección de uno de ellos, una recomendación de liberación y una propuesta de gestión de calidad.

La API se ejecuta localmente en `http://127.0.0.1:8765`, utiliza la biblioteca estándar de Python y mantiene los datos en memoria.

## 2. Prerrequisitos

- Python 3.9 o superior. En el equipo utilizado para esta ejecución se instaló **Python 3.14.10**.
- Windows con CMD o una terminal equivalente.
- Archivos del laboratorio: `server.py`, `test_events.py` y `test_smoke.py`.
- Postman (opcional, para reproducir solicitudes HTTP manualmente).

No se requieren dependencias externas para las pruebas descritas; se utiliza `unittest` de la biblioteca estándar.

## 3. Estructura del proyecto

```text
QA-Leadership-Challenge/
├── server.py
├── test_events.py
├── test_smoke.py
├── README.md
├── DECISION-QA.md
└── Evidencias/
```

`__pycache__/` puede aparecer al ejecutar Python; es una carpeta generada automáticamente y no es un entregable.

## 4. Preparación y ejecución

Abrir una terminal en la carpeta del proyecto.

### 4.1 Verificar Python

```bash
python --version
```

Versión observada en el equipo: `Python 3.14.10`.

### 4.2 Levantar la API

En una primera terminal:

```bash
python server.py
```

La consola debe indicar que el laboratorio está disponible en:

```text
QA Lab: http://127.0.0.1:8765 (solo localhost)
```

Mantener esta terminal abierta mientras se ejecutan las pruebas.

### 4.3 Verificar salud

En Postman:

- Método: `GET`
- URL: `http://127.0.0.1:8765/health`

Resultado observado: HTTP `200 OK`, con `status: ok` y `service: qa-telemetria-lab`.

### 4.4 Ejecutar pruebas

En una segunda terminal, desde la carpeta del proyecto:

```bash
python -m unittest -v test_smoke.py
python -m unittest -v test_events.py
```

Para detener el servidor, volver a la primera terminal y presionar `CTRL + C`. El mensaje `KeyboardInterrupt` que aparece al detenerlo manualmente es esperado.

El laboratorio incluye `DELETE /_test/reset` para limpiar datos entre pruebas. Debe utilizarse únicamente en el entorno local de pruebas.

## 5. Escenarios automatizados y resultados

El archivo `test_events.py` ejecuta los siguientes escenarios, según los nombres y mensajes observados en la salida de `unittest`:

| Escenario | Comportamiento esperado del contrato | Código observado antes | Código observado después |
|---|---|---:|---|
| `test_events_are_isolated_between_clients` | Un cliente no consulta eventos de otro cliente, aunque compartan `device_id`. | FAIL: se devolvía también `evento-b`. | PASS: la prueba terminó en `ok`. |
| `test_same_event_retry_returns_conflict_without_duplicate` | Reintentar el mismo par cliente/evento debe responder HTTP 409 y no duplicar el registro. | FAIL: HTTP 201 en vez de 409. | FAIL: HTTP 201 en vez de 409. |
| `test_timestamp_more_than_five_minutes_in_future_is_rejected` | Un timestamp con más de cinco minutos de anticipación debe responder HTTP 422. | FAIL: HTTP 201 en vez de 422. | FAIL: HTTP 201 en vez de 422. |

**Ejecución inicial:** 3 pruebas ejecutadas; 3 fallos (`FAILED (failures=3)`).

**Ejecución posterior a la corrección de aislamiento:** 3 pruebas ejecutadas; 1 prueba aprobada y 2 fallos (`FAILED (failures=2)`).

La ejecución posterior no representa una suite completamente aprobada. Los dos fallos restantes son defectos conocidos y pendientes de corrección. La recomendación de liberación se mantiene en NO-GO.

## 6. Corrección implementada: aislamiento entre clientes

### Hallazgo

La consulta `GET /v1/events?device_id=...` filtraba los eventos por dispositivo, pero no restringía el resultado al cliente identificado por la cabecera `X-Client-ID`. La reproducción manual en Postman mostró que una consulta autenticada como `cliente-a` podía recibir un evento cuyo `client_id` era `cliente-b`.

### Cambio

En `server.py`, la selección de eventos se ajustó para exigir simultáneamente:

- Coincidencia de `device_id` con el dispositivo solicitado.
- Coincidencia de `client_id` del evento con el valor de `X-Client-ID` de la solicitud.

### Verificación

La prueba `test_events_are_isolated_between_clients` pasó después del cambio. La evidencia manual y la salida automatizada deben conservarse en la carpeta `Evidencias/`.

**Alcance del cambio:** se corrigió únicamente este defecto, tal como permite el enunciado. No se modificaron las validaciones de duplicidad ni de timestamp futuro.

## 7. Defectos pendientes y riesgo

1. **Duplicidad de eventos:** el contrato requiere HTTP 409 para un reintento del mismo `(client_id, event_id)`. La prueba recibió HTTP 201.
2. **Timestamp futuro:** el contrato requiere HTTP 422 cuando `occurred_at` supera en más de cinco minutos la hora actual. La prueba recibió HTTP 201.

Ambos comportamientos incumplen el contrato. Junto con la corrección parcial, justifican la recomendación **NO-GO** hasta que Desarrollo implemente las correcciones y QA ejecute las pruebas de confirmación y regresión.

El contrato también define validaciones de cabecera y coordenadas. No se afirma que esos escenarios adicionales hayan sido cubiertos por las tres pruebas seleccionadas en este ejercicio.

## 8. Estrategia propuesta de CI/CD

No se implementó un pipeline real; se propone el siguiente flujo:

1. Ejecutar pruebas smoke y de contrato en cada Pull Request.
2. Ejecutar regresión automatizada antes de promover una versión.
3. Publicar resultados de pruebas como artefactos del pipeline.
4. Bloquear la promoción si falla una prueba crítica o de aislamiento de datos.
5. Mantener datos de prueba independientes por escenario y cliente.
6. Preparar y limpiar el estado del laboratorio de forma controlada; no compartir identificadores entre pruebas.
7. Usar timestamps UTC deterministas o relativos al reloj controlado del test, aserciones explícitas y esperas basadas en condiciones, evitando pausas arbitrarias.

## 9. Datos, métricas y línea base 2027

Se analizaron los archivos ficticios `releases.csv` (10 releases) e `incidentes.csv` (11 registros).

**Definición propuesta:** defecto escapado atribuible a una release es un incidente de producción vinculado a un cambio o configuración de esa release, reportado dentro de los siete días posteriores a su publicación.

**Reglas de depuración:**
- Excluir registros marcados como duplicados.
- Excluir incidentes detectados en QA antes de producción.
- Excluir problemas clasificados como proveedor externo.
- Excluir defectos preexistentes.
- Contar una release como afectada una sola vez, aunque tenga más de un incidente atribuible.

**Ventana y denominador:** el registro más reciente de los archivos es del 16/10/2026 a las 08:00 UTC. Usando ese momento como corte de observación, las primeras cinco releases (REL-001 a REL-005) ya completaron siete días desde su publicación. Las releases posteriores se excluyen del denominador por tener una ventana incompleta.

Entre las cinco releases observables, REL-001, REL-002 y REL-003 tuvieron al menos un incidente de producción atribuible dentro de la ventana. Por tanto:

`Línea base = 3 releases afectadas / 5 releases observables × 100 = 60 %`

`Meta 2027 = 60 % × (1 − 0,20) = 48 %`

La meta representa una reducción relativa del 20 % en la proporción de releases afectadas. Debe medirse sobre una muestra futura con la misma definición, reglas de exclusión y ventana completa de siete días.

**Limitaciones:** conjunto ficticio y pequeño; fechas de observación limitadas; solo cinco releases con ventana completa al corte; clasificación de causas asumida como fuente de verdad; el indicador mide releases afectadas, no severidad ni cantidad total de incidentes. Los resultados no deben generalizarse a toda la operación.

## 10. Uso de IA y verificación

Se utilizó asistencia de IA como apoyo para estructurar el análisis, revisar la lógica de la corrección y preparar documentación. Las recomendaciones se contrastaron con el contrato funcional del PDF, los registros CSV, la reproducción manual en Postman y la ejecución local de `unittest`. La IA no sustituyó la ejecución ni la validación de resultados.

## 11. Evidencias

Conservar en `Evidencias/` las capturas originales de:

- Ejecución inicial de las tres pruebas.
- Reproducción del defecto de aislamiento en Postman, mostrando `X-Client-ID: cliente-a` y el evento perteneciente a `cliente-b`.
- Fragmento de `server.py` con el filtro por cliente.
- Ejecución posterior con la prueba de aislamiento aprobada y los dos defectos pendientes.

Los nombres de archivo pueden seguir una secuencia como `01_ejecucion_inicial.png`, `02_defecto_aislamiento_postman.png`, `03_correccion_aislamiento.png` y `04_resultado_post_correccion.png`. Verificar que las capturas estén efectivamente incluidas antes de comprimir la entrega.
