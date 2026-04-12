# Académika — Roadmap

> Documento interno de producto.
> Última actualización: 2026-04-12

---

## Qué es

Plataforma web AI-first para que las direcciones de carrera y los equipos docentes de la UNQ puedan analizar trayectorias académicas, detectar patrones y anticipar problemáticas.

## Usuarios objetivo (MVP)

| Usuario         | Rol          | Problema que resuelve                                                                     |
| --------------- | ------------ | ----------------------------------------------------------------------------------------- |
| Eugenio Cálcena | Director TPI | Identificar materias cuello de botella y estudiantes en riesgo de abandono                |
| Denise Pari     | Directora LI | Detectar materias con pocas inscripciones en años avanzados y analizar tasa de graduación |

### Luego del MVP

Permitir que los equipos docentes accedan al análisis específico de sus materias.

---

## Fases

### Preludio — Investigación y diseño

**Estado:** en curso
**Cierre estimado:** 17/04/2026 (reunión de seguimiento)

- [x] Stack tecnológico (ADR-003)
- [x] `anon_guarani.py` — herramienta de anonimización para desarrollar sin datos reales
- [ ] Encuesta a directores: qué datos tienen, qué preguntas quieren responder
- [ ] Roadmap acordado con Gabi

---

### Fase 1 — Fundación

**Objetivo:** app tradicional funcional sin IA, con datos reales (anonimizados), deployed en Digital Ocean
**Duración estimada:** 3-4 semanas

#### Backend

- [ ] FastAPI: estructura base, health check, configuración de entornos
- [ ] Modelos de datos: Alumno, Carrera, Materia, PlanDeEstudio, Cursada, Inscripción
- [ ] Importador de planillas Guaraní (CSV → base de datos)
  - `alumnos_guarani.csv`, `datos_personales.csv`, `inscripciones.csv`
  - `carreras.csv`, `materias.csv`
  - `planes_lds.csv`, `planes_tpi.csv`, `requisitos_lds.csv`, `requisitos_tpi.csv`
- [ ] API REST: endpoints de consulta para el frontend
- [ ] Autenticación y autorización (JWT, roles: admin / director)

#### Frontend (React + TypeScript)

- [ ] **Auth:** login, registro, recuperación de contraseña
- [ ] **Backoffice (admin):** gestión de usuarios, roles y permisos, carga de planillas
- [ ] **Workspace (director):**
  - Sources: listado de planillas cargadas, estado de importación
  - Studio (panel analítico): vistas predefinidas con datos básicos de la carrera
  - Chatbot: skeleton de UI — layout, input, historial de mensajes (sin IA, deshabilitado)

#### Infra

- [ ] Deploy en Digital Ocean (droplet básico)
- [ ] CI mínimo: tests en push/PR

#### Criterio de "hecho"

Un director puede loguearse, ver los datos de su carrera y navegar el workspace. El chatbot existe pero está deshabilitado.

---

### Fase 2 — Fundación e Imperio

**Objetivo:** análisis predefinidos útiles en el Studio, sin necesidad de pedirlos
**Duración estimada:** 3-4 semanas

#### Pipeline de datos

- [ ] Normalización y validación de planillas al importar
- [ ] Métricas por materia: tasa de aprobación, nota promedio, evolución por cohorte
- [ ] Métricas por estudiante: avance en la carrera, materias bloqueantes, tiempo en carrera
- [ ] Métricas de carrera: distribución de avance, tasa de graduación, materias con pocas inscripciones

#### Studio

- [ ] Vista de carrera: distribución de avance de cohortes
- [ ] Vista de materia: evolución histórica de aprobación, detalle por comisión
- [ ] Vista de estudiante: trayectoria individual con materias cursadas
- [ ] Alertas predefinidas: estudiantes inactivos, materias con alta reprobación, materias con pocas inscripciones en años avanzados

#### Criterio de "hecho"

Los directores pueden responder sus preguntas frecuentes sin hablar con nadie.

---

### Fase 3 — Segunda Fundación

**Objetivo:** primera versión funcional de Hari con Text-to-SQL
**Duración estimada:** 2-3 semanas

- [ ] Pipeline Text-to-SQL: Hari lee el schema y genera SQL desde lenguaje natural
- [ ] Integración con Claude API (modelo configurable — ADR-002)
- [ ] Ejecución segura de queries generados (sandboxing, timeouts, solo SELECT)
- [ ] Chatbot habilitado en el workspace
- [ ] Suite de queries canónicos con respuesta conocida (referencia para la comparativa de Fase 5)
- [ ] Guardrail básico: Hari aclara cuando no tiene suficiente información para responder

#### Criterio de "hecho"

Hari responde correctamente los queries canónicos del dominio usando Text-to-SQL.

---

### Fase 4 — Los límites de la Fundación

**Objetivo:** agregar soporte de RAG con embeddings a Hari como segundo approach
**Duración estimada:** 2-3 semanas

- [ ] Pipeline RAG con pgvector: indexar datos académicos en vector store
- [ ] Hari puede responder usando RAG además de Text-to-SQL (configurable o por tipo de pregunta)
- [ ] Mejoras al pipeline Text-to-SQL a partir de los aprendizajes de Fase 3:
  - Anotación del schema con hints (relaciones, casos edge, convenciones de datos)
  - Generación en dos etapas: plan en lenguaje natural antes de generar el SQL
  - Manejo de ambigüedad: Hari pide aclaración cuando la pregunta no es precisa

#### Criterio de "hecho"

Hari puede responder usando ambos approaches. Ambos corren sobre el mismo conjunto de queries canónicos.

---

### Fase 5 — Fundación y Tierra

**Objetivo:** comparativa Text-to-SQL vs RAG — decidir el approach definitivo de Hari
**Duración estimada:** 1-2 semanas

- [ ] Evaluación sistemática sobre los queries canónicos de Fase 3: accuracy, latencia, casos donde falla cada uno
- [ ] Identificar qué tipo de preguntas responde mejor cada approach:
  - Text-to-SQL: aggregations, filtros exactos, comparaciones numéricas
  - RAG: preguntas narrativas, patrones, contexto cualitativo
- [ ] Decisión: Text-to-SQL solo / RAG solo / híbrido
- [ ] Suite de regresión automatizada con el approach elegido

#### Criterio de "hecho"

Approach definitivo elegido con evidencia. Hari da respuestas confiables en los escenarios de uso frecuente.

---

### Cierre

**Objetivo:** validación con usuarios reales e informe académico
**Duración estimada:** 3 semanas

- [ ] Sesión de uso con Eugenio (TPI) y Denise (LI)
- [ ] Iteración final a partir del feedback
- [ ] Decisión de infraestructura: Digital Ocean permanente vs migración a UNQ sistemas
- [ ] Informe académico completo (Markdown → LaTeX/PDF con Pandoc)
- [ ] Demo preparada para la presentación
- [ ] Repositorio limpio y documentado

#### Criterio de "hecho"

Al menos uno de los directores dice que lo usaría en su trabajo real. El informe está entregado.

---

### Fase 5 — Fundación y Tierra

**Objetivo:** validación con usuarios reales, iteración final, cierre académico
**Duración estimada:** 3 semanas

- [ ] Sesión de uso con Eugenio (TPI) y Denise (LI)
- [ ] Recolección de feedback estructurado e iteración final
- [ ] Decisión de infraestructura: Digital Ocean permanente vs migración a UNQ sistemas
- [ ] Informe académico completo (Markdown → LaTeX/PDF con Pandoc)
- [ ] Demo preparada para la presentación
- [ ] Repositorio limpio y documentado

#### Criterio de "hecho"

Al menos uno de los directores dice que lo usaría en su trabajo real. El informe está entregado.

---

## Timeline tentativo

```txt
Abril      [Preludio ████]
Mayo       [Fase 1 ████████████████]
Junio      [Fase 2 ████████████████]
Julio      [Fase 3 ██████████] [Fase 4 ██████]
Agosto     [Fase 5 ████] [Cierre ████████████]
```

**~5 meses.** Viable si:

1. Los datos de Guaraní llegan antes de fin de abril
2. El scope del Studio (Fase 2) no se expande con pedidos de nuevos análisis
3. Al menos uno de los dos approaches de Hari (Text-to-SQL o RAG) da resultados aceptables en Fase 5

---

## Dependencias externas

| Dependencia                            | Quién            | Impacto si se demora                     |
| -------------------------------------- | ---------------- | ---------------------------------------- |
| Datos reales de Guaraní (anonimizados) | Eugenio / Denise | Fase 1 y 2 se demoran en cascada         |
| Confirmación de plazo                  | Gabi             | Ajuste del timeline general              |
| Acceso a infraestructura UNQ (futuro)  | UNQ sistemas     | No bloquea MVP, sí la decisión de Fase 5 |

---

## Riesgos

| Riesgo                                                          | Probabilidad | Mitigación                                                                  |
| --------------------------------------------------------------- | ------------ | --------------------------------------------------------------------------- |
| Datos de Guaraní llegan tarde o incompletos                     | Alta         | `anon_guarani.py` + encuesta temprana; datos sintéticos como fallback       |
| Scope creep en Fase 2 (más análisis pedidos por los directores) | Media        | Definir lista fija de vistas con Eugenio/Denise antes de arrancar Fase 2    |
| Text-to-SQL genera SQL incorrecto para queries complejos        | Media        | Suite de queries canónicos desde Fase 3; generación en dos etapas en Fase 4 |
| Ningún approach (Text-to-SQL ni RAG) da resultados aceptables   | Baja         | La comparación en Fase 4 permite pivotar; el híbrido es el fallback natural |

---

## Preguntas abiertas

- ¿Qué análisis específicos necesitan Eugenio y Denise? → **encuesta pendiente**
- ¿Qué tan incompletos están los datos de Guaraní para proyección de materias?
- ¿La UNQ tiene restricciones sobre dónde pueden vivir los datos?
- ¿La validación de Fase 5 requiere que la app esté en producción real o alcanza una demo?
