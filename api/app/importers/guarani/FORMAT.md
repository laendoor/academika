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
