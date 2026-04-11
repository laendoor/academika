#!/usr/bin/env python3
"""
gen_datos_prueba.py — Generador de datos sintéticos para tests de anon_guarani.py
Dev only — no se entrega ni se commitea.

Genera en ../../proyecto-finisterre/datos-prueba/:
  - datos_personales.csv
  - alumnos_guarani.csv   (reemplaza el fixture de nacho, que tenía DNIs vacíos)
  - inscripciones.csv

Los planes, requisitos, carreras y materias no se tocan — son datos estructurales.

Uso: uv run python tools/gen_datos_prueba.py
"""

import csv
import random
from datetime import date
from pathlib import Path

OUTPUT_DIR = Path(__file__).parent.parent / "datos-prueba"

# ── Estudiantes ───────────────────────────────────────────────────────────────
# (legajo, dni, apellido, nombre, carrera, plan, anio_ingreso)

STUDENTS = [
    (12001, 35120001, "García",     "Martina",   "P", 2015, 2018),
    (12002, 37450023, "Rodríguez",  "Santiago",  "P", 2015, 2019),
    (12003, 38901234, "López",      "Valentina", "P", 2015, 2020),
    (12004, 36234567, "Martínez",   "Tomás",     "P", 2015, 2019),
    (12005, 39012345, "González",   "Camila",    "P", 2015, 2021),
    (12006, 34789012, "Fernández",  "Ignacio",   "W", 2019, 2020),
    (12007, 40123456, "Torres",     "Lucía",     "W", 2019, 2021),
    (12008, 37654321, "Ramírez",    "Mateo",     "W", 2019, 2020),
    (12009, 38765432, "Sánchez",    "Florencia", "W", 2019, 2022),
    (12010, 36543210, "Díaz",       "Bruno",     "W", 2019, 2021),
]

# ── Materias por carrera (cuatrimestre, codigo, nombre, creditos) ─────────────

TPI_MATERIAS = [
    (1, 80005, "Elementos de Programación y Lógica",         10),
    (1, 80000, "Lectura y Escritura Académica",              10),
    (1, 80003, "Matemática",                                 10),
    (2, 487,   "Introducción a la Programación",             18),
    (2, 1033,  "Matemática I",                               16),
    (2, 1032,  "Organización de Computadoras",               12),
    (3, 1036,  "Estructuras de Datos",                       16),
    (3, 1034,  "Programación con Objetos I",                 16),
    (3, 1035,  "Bases de Datos",                             12),
    (4, 1041,  "Matemática II",                               8),
    (4, 1037,  "Programación con Objetos II",                12),
    (4, 1038,  "Redes de Computadoras",                      12),
    (4, 1039,  "Sistemas Operativos",                        12),
    (4, 1045,  "Programación Funcional",                      8),
    (5, 1043,  "Construcción de Interfaces de Usuario",      12),
    (5, 1042,  "Elementos de Ingeniería de Software",        12),
    (5, 1044,  "Estrategias de Persistencia",                12),
    (5, 1047,  "Laboratorio de Sistemas Operativos y Redes",  8),
    (6, 1046,  "Desarrollo de Aplicaciones",                 12),
    (6, 1040,  "Programación Concurrente",                    8),
    (6, 1305,  "Práctica del Desarrollo de Software",        16),
]

LDS_MATERIAS = [
    (1, 80000, "Lectura y escritura académica",              10),
    (1, 80003, "Matemática",                                 10),
    (1, 80005, "Elementos de programación y lógica",         10),
    (2, 487,   "Introducción a la Programación",             16),
    (2, 1033,  "Matemática I",                               16),
    (2, 1032,  "Organización de Computadoras",               12),
    (3, 1036,  "Estructuras de Datos",                       16),
    (3, 1034,  "Programación con Objetos I",                 16),
    (3, 1035,  "Bases de Datos",                             12),
    (4, 1041,  "Matemática II",                               8),
    (4, 1037,  "Programación con Objetos II",                12),
    (4, 1038,  "Redes de Computadoras",                      12),
    (4, 1039,  "Sistemas Operativos",                        12),
    (4, 1045,  "Programación Funcional",                      8),
    (5, 1043,  "Construcción de Interfaces de Usuario",      12),
    (5, 1307,  "Algoritmos",                                 12),
    (5, 1044,  "Estrategias de Persistencia",                12),
    (5, 1047,  "Laboratorio de Sistemas Operativos y Redes",  8),
    (6, 54,    "Análisis Matemático",                        12),
    (6, 1302,  "Lógica y Programación",                      12),
    (6, 1042,  "Elementos de Ingeniería de Software",        12),
    (7, 842,   "Matemática III",                              8),
    (7, 1040,  "Programación Concurrente",                    8),
    (7, 1308,  "Ingeniería de Requerimientos",                8),
    (7, 1305,  "Práctica del Desarrollo de Software",        16),
]

# ── Helpers ───────────────────────────────────────────────────────────────────

def _email(nombre: str, apellido: str, legajo: int) -> str:
    def norm(s: str) -> str:
        return s.lower().replace(" ", "").translate(
            str.maketrans("áéíóúÁÉÍÓÚñÑ", "aeiouAEIOUnN")
        )
    domains = ["gmail.com", "hotmail.com", "yahoo.com.ar", "outlook.com"]
    return f"{norm(nombre)}.{norm(apellido)}{legajo % 100}@{domains[legajo % len(domains)]}"


def _exam_date(anio: int, cuatri: int, rng: random.Random) -> date:
    """Fecha de examen verosímil: julio o diciembre para primer cuatri, diciembre o febrero para segundo."""
    if cuatri % 2 == 1:
        month = rng.choice([7, 12])
    else:
        month = rng.choice([12, 2])
        if month == 2:
            anio += 1
    return date(anio, month, rng.randint(1, 28))


def _cuatris_avanzados(anio_ingreso: int, total_cuatris: int) -> int:
    """Cuántos cuatrimestres completó un estudiante que ingresó en anio_ingreso, al 2024."""
    return min((2024 - anio_ingreso) * 2, total_cuatris)


# ── Generadores ───────────────────────────────────────────────────────────────

def gen_datos_personales() -> list[dict]:
    rows = []
    for legajo, dni, apellido, nombre, carrera, plan, anio_ingreso in STUDENTS:
        rows.append({
            "Legajo":           legajo,
            "DNI":              dni,
            "Apellido":         apellido,
            "Nombre":           nombre,
            "Email":            _email(nombre, apellido, legajo),
            "Fecha":            date(anio_ingreso, 3, (legajo % 15) + 1).strftime("%d/%m/%Y"),
            "Código de Carrera": carrera,
            "Plan de Estudios": plan,
        })
    return rows


def gen_alumnos_guarani() -> list[dict]:
    rows = []
    for legajo, dni, apellido, nombre, carrera, plan, anio_ingreso in STUDENTS:
        materias = TPI_MATERIAS if carrera == "P" else LDS_MATERIAS
        max_cuatri = max(m[0] for m in materias)
        avanzados = _cuatris_avanzados(anio_ingreso, max_cuatri)

        rng = random.Random(legajo)

        for cuatri, codigo, nombre_mat, creditos in materias:
            if cuatri > avanzados:
                continue

            anio_cursada = anio_ingreso + (cuatri - 1) // 2
            roll = rng.random()

            if roll < 0.75:
                result, nota, forma = "P", rng.randint(6, 10), "Examen"
                fecha = _exam_date(anio_cursada, cuatri, rng)
            elif roll < 0.85:
                # Aprobó al cuatrimestre siguiente
                result, nota, forma = "P", rng.randint(4, 5), "Examen"
                fecha = _exam_date(anio_cursada + 1, cuatri, rng)
            elif roll < 0.93:
                result, nota, forma = "R", rng.randint(1, 3), "Examen"
                fecha = _exam_date(anio_cursada, cuatri, rng)
            else:
                result, nota, forma = "A", "A", "Equivalencia"
                fecha = _exam_date(anio_cursada, cuatri, rng)

            acta_ex = rng.randint(1000, 9999) if result == "P" and forma == "Examen" else 0

            rows.append({
                "Legajo":           legajo,
                "DNI":              dni,
                "Carrera":          carrera,
                "Regular":          "",
                "Calidad":          "",
                "Cod.Materia":      codigo,
                "Nombre_materia":   nombre_mat,
                "Fecha":            fecha.strftime("%d/%m/%Y"),
                "Result":           result,
                "Nota":             nota,
                "Forma Aprobación": forma,
                "Créditos":         creditos,
                "Acta Promo":       0,
                "Acta Ex":          acta_ex,
                "Plan":             plan,
            })
    return rows


def gen_inscripciones() -> list[dict]:
    """Inscripciones al próximo cuatrimestre a cursar para cada estudiante."""
    rows = []
    for legajo, dni, apellido, nombre, carrera, plan, anio_ingreso in STUDENTS:
        materias = TPI_MATERIAS if carrera == "P" else LDS_MATERIAS
        max_cuatri = max(m[0] for m in materias)
        siguiente = _cuatris_avanzados(anio_ingreso, max_cuatri) + 1

        if siguiente > max_cuatri:
            continue  # ya terminó la carrera

        rng = random.Random(legajo + 9999)
        for cuatri, codigo, nombre_mat, creditos in materias:
            if cuatri != siguiente:
                continue
            rows.append({
                "Código de Carrera": carrera,
                "DNI":               dni,
                "Legajo":            legajo,
                "Código de materia": codigo,
                "Comisión":          rng.randint(1, 4),
                "Fecha":             date(2024, 3, rng.randint(1, 20)).strftime("%d/%m/%Y"),
            })
    return rows


# ── Main ──────────────────────────────────────────────────────────────────────

def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        print(f"  {path.name}: sin filas, saltado")
        return
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()), delimiter=";")
        writer.writeheader()
        writer.writerows(rows)
    print(f"  {path.name}: {len(rows)} filas")


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Generando CSVs en {OUTPUT_DIR}/\n")
    write_csv(OUTPUT_DIR / "datos_personales.csv", gen_datos_personales())
    write_csv(OUTPUT_DIR / "alumnos_guarani.csv",  gen_alumnos_guarani())
    write_csv(OUTPUT_DIR / "inscripciones.csv",    gen_inscripciones())
    print("\nListo.")


if __name__ == "__main__":
    main()
