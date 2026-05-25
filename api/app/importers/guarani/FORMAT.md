# Formato de archivos Guaraní

Archivos exportados desde SIU Guaraní para el importador de alumnos.

- **Separador:** `;` (punto y coma)
- **Encoding:** UTF-8 (datos de prueba); producción puede requerir latin-1
- **Primera fila:** cabecera, se ignora al parsear

---

## datos_personales.csv

Datos maestros del alumno. Una fila por alumno.

> **Nota de dominio:** la UNQ decidió a partir de un cierto año usar el DNI como número de legajo,
> por lo que para alumnos recientes `Legajo == DNI`. Para alumnos anteriores son distintos.
> Usamos el DNI como `doc_id` (source of truth de identidad); el `Legajo` se persiste en
> `Student.unq_id` para preservar el identificador interno de Guaraní.

| Columna           | Tipo   | Mapea a                             | Notas                                  |
| ----------------- | ------ | ----------------------------------- | -------------------------------------- |
| Legajo            | string | `Student.unq_id`                    | ID interno de Guaraní; nullable, único |
| DNI               | string | `Student.doc_id`                    | Identidad nacional, source of truth    |
| Apellido          | string | `Student.last_name`                 |                                        |
| Nombre            | string | `Student.first_name`                |                                        |
| Email             | string | `Student.email`                     | Opcional, puede estar vacío            |
| Fecha             | date   | `Student.enrolled_at`               | Formato DD/MM/YYYY                     |
| Código de Carrera | string | `Student.degree_id` (via code)      | Debe existir en `degree.code`          |
| Plan de Estudios  | int    | `Student.plan_id` (via degree+year) | Opcional; puede no existir aún         |

`academic_status` se inicializa como `alumno_regular` para todos los alumnos importados.

**Ejemplo de fila:**

```txt
12001;35120001;García;Martina;martina.garcia1@hotmail.com;02/03/2018;P;2015
```

Produce:

```python
Student(
    doc_id="35120001",
    unq_id="12001",
    last_name="García",
    first_name="Martina",
    email="martina.garcia1@hotmail.com",
    degree=<Degree code="P">,
    study_plan=<StudyPlan degree="P", year=2015>,  # None si no existe
    academic_status="alumno_regular",
)
```

---

## alumnos_guarani.csv

Historial de cursadas y exámenes. Una fila por evento de resultado.

| Columna          | Tipo   | Mapea a                                    | Notas                                                               |
| ---------------- | ------ | ------------------------------------------ | ------------------------------------------------------------------- |
| Legajo           | string | —                                          | Redundante: usamos DNI para el lookup del Student                   |
| DNI              | string | `CourseEnrollment.student_id` (via doc_id) | Busca al Student por `student.doc_id`                               |
| Carrera          | string | `CourseEnrollment.degree_id` (via code)    | Debe existir en `degree.code`; un alumno puede cursar LI y TPI      |
| Regular          | string | `CourseEnrollment.is_regular`              | Flag de regularidad en cursada; formato exacto a confirmar          |
| Calidad          | string | `CourseEnrollment.enrollment_type`         | `L` → `libre`, vacío/otro → `regular`                               |
| Cod.Materia      | string | `CourseEnrollment.course_id` (via code)    | Debe existir en `course.code`                                       |
| Nombre_materia   | string | —                                          | Ignorado (nombre canónico viene del Course)                         |
| Fecha            | date   | `year`, `term` via `date_to_year_term()`   | Formato DD/MM/YYYY                                                  |
| Result           | string | `CourseEnrollment.enrollment_status`       | `P`→`promocionado`, `A`→`aprobado`, `R`→`regular`, otro→`inscripto` |
| Nota             | string | `CourseEnrollment.grade`                   | Puede estar vacío o contener letras                                 |
| Forma Aprobación | string | `CourseEnrollment.approval_type`           | Ej: "Examen", "Promoción", "Equivalencia"                           |
| Créditos         | int    | `CourseEnrollment.credits`                 | Puede variar por plan; se preserva por cursada                      |
| Acta Promo       | string | —                                          | Ignorado (referencia administrativa)                                |
| Acta Ex          | string | —                                          | Ignorado (referencia administrativa)                                |
| Plan             | int    | `CourseEnrollment.plan_year`               | Año del plan bajo el que se cursó la materia                        |

**Ejemplo de fila:**

```txt
12001;35120001;P;;;80005;Elementos de Programación y Lógica;01/12/2019;P;4;Examen;10;0;1231;2015
```

Produce:

```python
CourseEnrollment(
    student=<Student doc_id="35120001">,
    course=<Course code="80005">,
    degree=<Degree code="P">,
    year=2019,
    term="2C",                  # diciembre → 2C
    enrollment_type="regular",
    enrollment_status="promocionado",
    grade="4",
    is_regular=None,            # vacío en el CSV
    approval_type="Examen",
    credits=10,
    plan_year=2015,
)
```

---

## inscripciones.csv

Inscripciones activas al cuatrimestre en curso. Una fila por inscripción.

| Columna           | Tipo   | Mapea a                                    | Notas                                             |
| ----------------- | ------ | ------------------------------------------ | ------------------------------------------------- |
| Código de Carrera | string | `CourseEnrollment.degree_id` (via code)    | Debe existir en `degree.code`                     |
| DNI               | string | `CourseEnrollment.student_id` (via doc_id) | Busca al Student por `student.doc_id`             |
| Legajo            | string | —                                          | Redundante: usamos DNI para el lookup del Student |
| Código de materia | string | `CourseEnrollment.course_id` (via code)    | Debe existir en `course.code`                     |
| Comisión          | string | `CourseEnrollment.section`                 | Opcional                                          |
| Fecha             | date   | `year`, `term` via `date_to_year_term()`   | Formato DD/MM/YYYY                                |

`enrollment_status` se fija en `inscripto` para todas las filas. `enrollment_type` en `regular`.

**Ejemplo de fila:**

```txt
W;40123456;12007;842;4;03/03/2024
```

Produce:

```python
CourseEnrollment(
    student=<Student doc_id="40123456">,
    course=<Course code="842">,
    degree=<Degree code="W">,
    year=2024,
    term="1C",          # marzo → 1C
    section="4",
    enrollment_type="regular",
    enrollment_status="inscripto",
    grade=None,
)
```

---

## Derivación de year y term

`date_to_year_term(d: date) -> tuple[int, str]`:

- Meses 3–7 → `(year, "1C")` (primer cuatrimestre)
- Meses 8–12 → `(year, "2C")` (segundo cuatrimestre)
- Meses 1–2 → `(year - 1, "2C")` (finales tardíos del cuatrimestre anterior)

---

## Comportamiento ante referencias faltantes

| Situación                 | Acción                             |
| ------------------------- | ---------------------------------- |
| `Degree` no encontrado    | `logger.warning` + fila descartada |
| `StudyPlan` no encontrado | `plan_id = None` (campo opcional)  |
| `Student` no encontrado   | `logger.warning` + fila descartada |
| `Course` no encontrado    | `logger.warning` + fila descartada |
