# DECISION-QA
## QA Leadership Challenge – Detektor
**Candidata:** Kelly Lorraine Vargas Cordero · **Fecha:** 24/11/2026

### 1. Recomendación de liberación: NO-GO

Se recomienda **NO-GO** para Tracking API en su estado actual. La prueba de aislamiento entre clientes pasó después de corregir el filtro por `client_id`; sin embargo, permanecen dos incumplimientos del contrato:

- Reintento del mismo `(client_id, event_id)`: la API respondió 201 en lugar de 409.
- Timestamp con más de cinco minutos en el futuro: la API respondió 201 en lugar de 422.

Estos defectos afectan la integridad y confiabilidad de los datos. La decisión técnica corresponde a QA con evidencia reproducible; cualquier aceptación de riesgo residual requiere aprobación explícita del responsable de negocio/Product Owner, con Desarrollo y DevOps informados. No se recomienda liberar mientras los defectos sigan abiertos. Antes de una liberación posterior, exigir corrección, pruebas de confirmación y regresión, monitoreo y plan de rollback probado/documentado.

### 2. Plan de capacidad QA (cinco días)

Capacidad efectiva disponible: **QA-A 16 h + QA-B 14 h = 30 h**. Demanda: 46 h. Brecha: 16 h.

| Día | QA-A (16 h) | QA-B (14 h) |
|---|---|---|
| 1 | Tracking: 6 h | SmartWork: 4 h |
| 2 | Tracking: 6 h | SmartWork: 3 h |
| 3 | Manager: 4 h | SmartWork: 3 h |
| 4 | Sin capacidad disponible | Manager: 4 h |
| 5 | Sin capacidad disponible | Sin capacidad disponible |

**Asignación por frente:** Tracking 12 h; SmartWork 10 h; Manager 8 h; regresión web por país 0 h asignadas y 16 h diferidas/renegociadas. La cobertura web se debe replanificar con el PO; no se presume capacidad adicional. La asignación respeta las fechas de necesidad: Tracking día 2, SmartWork día 3 y Manager día 4.

QA-A lidera Tracking y ejecuta parte de Manager; QA-B lidera SmartWork y completa Manager. Se comparten casos, resultados y evidencias para reducir dependencia de una persona. Desarrollo debe priorizar y entregar correcciones; DevOps debe asegurar ambiente/pipeline y reportes; PO debe confirmar prioridades y aceptar formalmente cualquier riesgo residual. Un tablero diario de horas, bloqueos y avance evitará sobreasignación.

### 3. Automatización y CI/CD

Propuesta (no implementada como pipeline real): smoke en cada despliegue; pruebas de contrato API en Pull Requests; regresión antes de release; publicación de reportes; gate que bloquee promoción ante fallos críticos, especialmente aislamiento, duplicidad e integridad temporal. Usar datos independientes por escenario/cliente, identificadores únicos y limpieza controlada con `DELETE /_test/reset` solo en el laboratorio. Evitar flakiness con timestamps UTC controlados, preparación/limpieza de datos, aserciones explícitas y sin esperas arbitrarias.

### 4. Línea base y meta 2027

**Indicador:** porcentaje de releases con al menos un defecto escapado atribuible a esa release dentro de los siete días posteriores a su publicación.

Se excluyen duplicados, incidencias detectadas en QA, problemas de proveedor externo y defectos preexistentes. Una release se cuenta una sola vez aunque tenga varios incidentes atribuibles.

Los CSV contienen 10 releases y 11 registros de incidentes. El registro más reciente es del **16/10/2026 a las 08:00 UTC**; al usarlo como corte, REL-001 a REL-005 completaron siete días de observación. Tres de esas cinco releases (REL-001, REL-002 y REL-003) tuvieron incidentes de producción atribuibles.

**Línea base = 3 / 5 = 60 %.**  
**Meta 2027 = 60 % × 0,80 = 48 %** (reducción relativa del 20 %).

Limitaciones: datos ficticios, muestra pequeña, solo cinco releases con ventana completa, y dependencia de la clasificación de causa registrada. Comparar periodos futuros con la misma ventana, reglas y criterios.

### 5. Plan 30/60/90

- **30 días – Diagnóstico y control:** mapear riesgos, flujo de QA, ambientes y criterios de entrada/salida. Evidencia: diagnóstico, matriz de riesgos y tablero inicial.
- **60 días – Estandarización y automatización:** priorizar pruebas API/regresión e incorporar gates en CI/CD. Evidencia: pipeline ejecutado, reportes y suite priorizada.
- **90 días – Medición y mejora:** comparar defectos escapados con la línea base, analizar tendencias y acordar acciones. Evidencia: informe de métricas y plan de mejora aprobado.

---
**Decisión sujeta a:** cierre verificable de defectos críticos, regresión satisfactoria y aprobación formal de los responsables correspondientes.
