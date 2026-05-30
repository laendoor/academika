# Formato de archivos Guaraní

## Archivos de SIU Guaraní soportados

- [TODO _qué opción/modulo/reporte?_] `datos_personales.py`
- [TODO _qué opción/modulo/reporte?_] `alumnos_guarani.csv`
- [TODO _qué opción/modulo/reporte?_] `inscripciones.csv`

## Configuración de parseo

- **Separador:** `;` (punto y coma)
- **Encoding:** UTF-8 (datos de prueba); producción puede requerir latin-1
- **Primera fila:** cabecera, se ignora al parsear

## datos_personales.csv

Datos del alumno. Una fila por alumno.

> **Nota de dominio:**
> Se utiliza el DNI (`doc_id`) clave primaria y fuente de verdad.
> El `legajo` se persiste igualmente como `unq_id`.

| Columna           | Tipo     | Mapea a                             | Notas                                  |
| ----------------- | -------- | ----------------------------------- | -------------------------------------- |
| Legajo            | `string` | `Student.unq_id`                    | ID interno de Guaraní; nullable, único |
| DNI               | `string` | `Student.doc_id`                    | Identidad nacional, source of truth    |
| Apellido          | `string` | `Student.last_name`                 |                                        |
| Nombre            | `string` | `Student.first_name`                |                                        |
| Email             | `string` | `Student.email`                     | Opcional, puede estar vacío            |
| Fecha             | `date`   | `Student.enrolled_at`               | Formato DD/MM/YYYY                     |
| Código de Carrera | `string` | `Student.degree_id` (via code)      | Debe existir en `degree.code`          |
| Plan de Estudios  | `int`    | `Student.plan_id` (via degree+year) | Opcional; puede no existir aún         |

El campo `academic_status` se inicializa con `"alumno_regular"` si el alumno no existe en la base.

### Ejemplo de parseo

**Fila:**

```txt
12001;35120001;García;Martina;martina.garcia1@hotmail.com;02/03/2018;P;2015
```

**Produce:**

```python
Student(
    doc_id="35120001",
    unq_id="12001",
    last_name="García",
    first_name="Martina",
    email="martina.garcia1@hotmail.com",
    degree=<Degree code="P">,
    study_plan=<StudyPlan degree="P", year=2015>,
    academic_status="alumno_regular",
)
```

## alumnos_guarani.csv

Historial de cursadas y exámenes. Una fila por evento.

| Columna          | Tipo     | Mapea a                                    | Notas                                                               |
| ---------------- | -------- | ------------------------------------------ | ------------------------------------------------------------------- |
| Legajo           | `string` | —                                          | Redundante: usamos DNI                                              |
| DNI              | `string` | `CourseEnrollment.student_id` (via doc_id) | Busca por `student.doc_id`                                          |
| Carrera          | `string` | `CourseEnrollment.degree_id` (via code)    | Debe existir en `degree.code`; un alumno puede varias carreras      |
| Regular          | `string` | `CourseEnrollment.is_regular`              | Flag de regularidad en cursada; formato exacto a confirmar          |
| Calidad          | `string` | `CourseEnrollment.enrollment_type`         | `L` → `libre`, vacío/otro → `regular`                               |
| Cod.Materia      | `string` | `CourseEnrollment.course_id` (via code)    | Debe existir en `course.code`                                       |
| Nombre_materia   | `string` | —                                          | Ignorado (nombre canónico viene del Course)                         |
| Fecha            | `date`   | `year`, `term` via `date_to_year_term()`   | Formato DD/MM/YYYY                                                  |
| Result           | `string` | `CourseEnrollment.enrollment_status`       | `P`→`promocionado`, `A`→`aprobado`, `R`→`regular`, otro→`inscripto` |
| Nota             | `string` | `CourseEnrollment.grade`                   | Puede estar vacío, contener letras (A, D, PA, ?) o números (1-10)   |
| Forma Aprobación | `string` | `CourseEnrollment.approval_type`           | Ej: "Examen", "Promoción", "Equivalencia"                           |
| Créditos         | `int`    | `CourseEnrollment.credits`                 | Puede variar por plan; se preserva por cursada                      |
| Acta Promo       | `string` | —                                          | Ignorado (referencia administrativa)                                |
| Acta Ex          | `string` | —                                          | Ignorado (referencia administrativa)                                |
| Plan             | `int`    | `CourseEnrollment.plan_year`               | Año del plan bajo el que se cursó la materia                        |

## Ejemplo de parseo

**Fila:**

```txt
12001;35120001;P;;;80005;Elementos de Programación y Lógica;01/12/2019;P;4;Examen;10;0;1231;2015
```

**Produce:**

```python
CourseEnrollment(
    student=<Student doc_id="35120001">,
    course=<Course code="80005">,
    degree=<Degree code="P">,
    year=2019,
    term="2C",
    enrollment_type="regular",
    enrollment_status="promocionado",
    grade="4",
    is_regular=None, # TODO: A Confirmar
    approval_type="Examen",
    credits=10,
    plan_year=2015,
)
```

## inscripciones.csv

Inscripciones activas al cuatrimestre en curso. Una fila por inscripción.

| Columna           | Tipo     | Mapea a                                    | Notas                         |
| ----------------- | -------- | ------------------------------------------ | ----------------------------- |
| Código de Carrera | `string` | `CourseEnrollment.degree_id` (via code)    | Debe existir `degree.code`    |
| DNI               | `string` | `CourseEnrollment.student_id` (via doc_id) | Busca por `student.doc_id`    |
| Legajo            | `string` | —                                          | Redundante: usamos DNI        |
| Código de materia | `string` | `CourseEnrollment.course_id` (via code)    | Debe existir `course.code`    |
| Comisión          | `string` | `CourseEnrollment.section`                 | Puede no existir. Default `1` |
| Fecha             | `date`   | `year`, `term` via `date_to_year_term()`   | Formato DD/MM/YYYY            |

`enrollment_status` se fija en `inscripto` para todas las filas. `enrollment_type` en `regular`.

### Ejemplo de parseo

**Fila:**

```txt
W;40123456;12007;842;4;03/03/2024
```

**Produce:**

```python
CourseEnrollment(
    student=<Student doc_id="40123456">,
    course=<Course code="842">,
    degree=<Degree code="W">,
    year=2024,
    term="1C",
    section="4",
    enrollment_type="regular",
    enrollment_status="inscripto",
    grade=None,
)
```

## carreras.csv

Catálogo de carreras. Una fila por carrera.

| Columna | Tipo     | Mapea a       | Notas                                |
| ------- | -------- | ------------- | ------------------------------------ |
| Codigo  | `string` | `Degree.code` | Clave natural; ej: `TPI`, `P`, `W`   |
| Nombre  | `string` | `Degree.name` |                                      |
| fecha   | `date`   | —             | Ignorado (fecha de creación Guaraní) |

### Ejemplo de parseo

**Fila:**

```txt
TPI;Tecnicatura Universitaria en Programación Informática;01/01/2000
```

**Produce:**

```python
DegreeRow(code="TPI", name="Tecnicatura Universitaria en Programación Informática")
```

## materias.csv

Catálogo de materias. **Sin cabecera.** Una fila por materia.

> **Nota:** este archivo no tiene fila de cabecera — `parse_csv(has_header=False)`.

| Posición | Tipo     | Mapea a                 | Notas                                  |
| -------- | -------- | ----------------------- | -------------------------------------- |
| 0        | `string` | `CourseRow.degree_code` | Código de carrera; usado para contexto |
| 1        | `int`    | `CourseRow.plan_year`   | Año del plan; usado para contexto      |
| 2        | `string` | `Course.code`           | Clave natural de la materia            |
| 3        | `string` | `Course.name`           |                                        |
| 4        | `string` | `Course.abbreviation`   | Puede estar vacío (`""`)               |

### Ejemplo de parseo

**Fila:**

```txt
TPI;2015;101;Algoritmos;algo
```

**Produce:**

```python
CourseRow(degree_code="TPI", plan_year=2015, code="101", name="Algoritmos", abbreviation="algo")
```

## planes\_\*.csv

Materias de un plan de estudios. Una fila por materia-plan. Archivos separados por carrera (`planes_tpi.csv`, `planes_lds.csv`).

> **Nota:** las exportaciones de Guaraní suelen incluir columnas trailing vacías (ej: `;;;;` al final de cada fila). El parser trabaja por índice y las ignora.

| Columna        | Tipo     | Mapea a                       | Notas                                |
| -------------- | -------- | ----------------------------- | ------------------------------------ |
| Codigo Carrera | `string` | `StudyPlan.degree_code`       | Debe existir en `degree.code`        |
| Plan           | `int`    | `StudyPlan.year`              | Año del plan; ej: 2015, 2018         |
| Cuatrimestre   | `string` | —                             | Ignorado                             |
| Nucleo         | `string` | —                             | Ignorado                             |
| Area           | `string` | —                             | Ignorado                             |
| Codigo         | `string` | `study_plan_course.course_id` | Debe existir en `course.code`        |
| Creditos       | `int`    | —                             | Ignorado (no modelado aún)           |
| Nombre         | `string` | —                             | Ignorado (nombre canónico en Course) |

El upsert crea/actualiza el `StudyPlan` con `name = "Plan {year}"` y luego vincula las materias en `study_plan_course` (ON CONFLICT DO NOTHING).

### Ejemplo de parseo

**Fila:**

```txt
TPI;2015;1;Básico;Programación;101;8;Algoritmos
```

**Produce:**

```python
StudyPlanCourseRow(degree_code="TPI", plan_year=2015, course_code="101")
```

## requisitos\_\*.csv

Correlatividades de un plan de estudios. Una fila por materia. Archivos separados por carrera (`requisitos_tpi.csv`, `requisitos_lds.csv`).

> **Nota:** `Obligatorias` y `Recomendadas` son listas de códigos separadas por coma. Si la lista tiene más de un elemento, el CSV la entrega entre comillas (`"101, 102"`). Si está vacía, el campo es `""`.
> El parser devuelve una `PrerequisiteRow` por fila CSV; el service expande la lista en filas individuales de `CoursePrerequisite`.

| Columna      | Tipo     | Mapea a                                | Notas                                 |
| ------------ | -------- | -------------------------------------- | ------------------------------------- |
| Carrera      | `string` | `PrerequisiteRow.degree_code`          | Debe existir en `degree.code`         |
| Plan         | `int`    | `PrerequisiteRow.plan_year`            | Año del plan                          |
| Materia      | `string` | `CoursePrerequisite.course_id`         | Materia que tiene correlativas        |
| Obligatorias | `string` | `CoursePrerequisite.is_required=True`  | Lista de códigos; vacío → lista vacía |
| Recomendadas | `string` | `CoursePrerequisite.is_required=False` | Lista de códigos; vacío → lista vacía |

### Ejemplo de parseo

**Fila:**

```txt
TPI;2015;103;"101, 102";101
```

**Produce:**

```python
PrerequisiteRow(
    degree_code="TPI",
    plan_year=2015,
    course_code="103",
    required_codes=["101", "102"],
    recommended_codes=["101"],
)
# El service expande esto en 3 filas CoursePrerequisite:
#   (plan, 103, 101, is_required=True)
#   (plan, 103, 102, is_required=True)
#   (plan, 103, 101, is_required=False)
```

## Decisiones y defaults

### Derivación para cuatrimestre

TODO: Analizar los casos de Integradores y Libres.

`date_to_year_term(d: date) -> tuple[int, str]`:

- Meses 1-6 → `(year, "1C")` (primer cuatrimestre)
- Meses 7-12 → `(year, "2C")` (segundo cuatrimestre)

### Referencias faltantes

| Situación                 | Acción                             |
| ------------------------- | ---------------------------------- |
| `Degree` no encontrado    | `logger.warning` + fila descartada |
| `StudyPlan` no encontrado | `plan_id = None` (campo opcional)  |
| `Student` no encontrado   | `logger.warning` + fila descartada |
| `Course` no encontrado    | `logger.warning` + fila descartada |
