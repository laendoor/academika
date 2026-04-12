#!/usr/bin/env python
# ruff: noqa: E402  — imports after version/dependency checks are intentional
"""
anon_guarani.py — Anonimizador de planillas SIU Guaraní
Proyecto Finisterre / Académika

Anonimiza automáticamente: legajo, DNI, nombre y apellido.
Las fechas NO se modifican — son datos académicos por cohorte, no datos personales.

Uso:
    python anon_guarani.py planilla.csv
    python anon_guarani.py file1.csv file2.xlsx file3.xls

Dependencias:
    pip install pandas openpyxl faker
"""

# ── Argument pre-check ───────────────────────────────────────────────────────

import sys

if len(sys.argv) < 2:
    print("Uso: python anon_guarani.py <archivo.csv|xlsx> [archivo2 ...]\n")
    print("Ejemplo: python anon_guarani.py datos.csv notas.xlsx")
    sys.exit(1)

# ── Version check ────────────────────────────────────────────────────────────

_MIN_PYTHON = (3, 11)
if sys.version_info < _MIN_PYTHON:
    print(
        f"Python {_MIN_PYTHON[0]}.{_MIN_PYTHON[1]} o superior requerido. "
        f"Versión actual: {sys.version_info.major}.{sys.version_info.minor}"
    )
    sys.exit(1)

# ── Dependency check ──────────────────────────────────────────────────────────

import importlib.util

_DEPS = [("pandas", "pandas"), ("openpyxl", "openpyxl"), ("faker", "Faker")]
_missing = [pkg for mod, pkg in _DEPS if importlib.util.find_spec(mod) is None]
if _missing:
    print(f"Faltan dependencias. Instalá con:\n\n  pip install {' '.join(_missing)}\n")
    sys.exit(1)

# ── Imports ───────────────────────────────────────────────────────────────────

import argparse
import hashlib
from pathlib import Path

import pandas as pd
from faker import Faker

# ── Constants ─────────────────────────────────────────────────────────────────

_PRIME_P = 1_000_003   # prime multiplier para hash de IDs
_PRIME_K = 9_999_991   # prime aditivo para hash de IDs
_fake = Faker("es_AR")

# Columnas sensibles reconocidas (case-insensitive).
# Nota: "nombre" solo se anonimiza si "apellido" también está presente
# (en planillas de materias/planes, "Nombre" refiere al nombre de la materia).
_SENSITIVE: dict[str, str] = {
    "legajo":   "id",
    "dni":      "id",
    "apellido": "apellido",
    "nombre":   "nombre",
}

# ── Estrategias de ofuscación ─────────────────────────────────────────────────

def _int_seed(value: str) -> int:
    """Semilla entera determinística a partir de cualquier string."""
    return int(hashlib.sha256(str(value).strip().encode()).hexdigest()[:8], 16)


def ofuscar_id(value: str) -> str:
    """
    Hash determinístico para DNI / legajo.
    Output: len(input) + 1 dígitos → preserva el "tamaño" del identificador
    y garantiza que no coincida con ningún valor real.
    """
    clean = str(value).strip().replace(".", "").replace("-", "").replace(" ", "")
    if not clean.isdigit():
        return value
    n = int(clean)
    digits = len(clean)
    hashed = (n * _PRIME_P + _PRIME_K) % 10**digits
    prefix = (sum(int(d) for d in str(hashed)) % 9) + 1
    return str(prefix) + str(hashed).zfill(digits)


def ofuscar_nombre(value: str) -> str:
    """Nombre falso determinístico (locale argentina)."""
    _fake.seed_instance(_int_seed(str(value)))
    return _fake.first_name()


def ofuscar_apellido(value: str) -> str:
    """Apellido falso determinístico (locale argentina)."""
    _fake.seed_instance(_int_seed(str(value)))
    return _fake.last_name()


_STRATEGIES = {
    "id":       ofuscar_id,
    "nombre":   ofuscar_nombre,
    "apellido": ofuscar_apellido,
}

# ── Detección de columnas ─────────────────────────────────────────────────────

def detect_sensitive_columns(cols: list[str]) -> dict[str, str]:
    """Retorna {col_original: strategy} para las columnas sensibles detectadas."""
    normalized = {c.lower().strip(): c for c in cols}
    has_apellido = "apellido" in normalized
    result: dict[str, str] = {}
    for norm, original in normalized.items():
        strategy = _SENSITIVE.get(norm)
        if strategy is None:
            continue
        if norm == "nombre" and not has_apellido:
            continue
        result[original] = strategy
    return result

# ── I/O de archivos ───────────────────────────────────────────────────────────

def load_file(path: Path) -> pd.DataFrame:
    ext = path.suffix.lower()
    if ext == ".csv":
        sample = path.read_text(errors="replace")[:4096]
        sep = ";" if sample.count(";") > sample.count(",") else ","
        return pd.read_csv(path, sep=sep, dtype=str)
    elif ext in (".xlsx", ".xls"):
        return pd.read_excel(path, dtype=str)
    else:
        print(f"Formato no soportado: {path.suffix}")
        sys.exit(1)


def save_file(df: pd.DataFrame, original: Path) -> Path:
    out = original.with_stem(original.stem + "_anon")
    if original.suffix.lower() == ".csv":
        df.to_csv(out, sep=";", index=False)
    else:
        df.to_excel(out, index=False)
    return out

# ── Flujo principal ───────────────────────────────────────────────────────────

def run(path: Path) -> None:
    df = load_file(path)
    cols = list(df.columns)

    print(f"\n{path.name}  →  {len(df)} filas, {len(cols)} columnas")

    col_strategies = detect_sensitive_columns(cols)

    if not col_strategies:
        print("  Sin columnas sensibles detectadas — omitido.\n")
        return

    print("Columnas anonimizadas:")
    for col in col_strategies:
        print(f"  {col}")

    result = df.copy()
    for col, strategy in col_strategies.items():
        result[col] = df[col].apply(_STRATEGIES[strategy])

    out = save_file(result, path)
    print(f"\nGuardado en: {out}\n")

# ── Entry point ───────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Anonimizador de planillas SIU Guaraní — Proyecto Finisterre"
    )
    parser.add_argument(
        "archivos",
        nargs="+",
        help="CSV o Excel a anonimizar (.csv, .xlsx, .xls) — se pueden pasar varios",
    )
    args = parser.parse_args()

    missing = [f for f in args.archivos if not Path(f).exists()]
    if missing:
        for f in missing:
            print(f"Archivo no encontrado: {f}")
        sys.exit(1)

    for archivo in args.archivos:
        run(Path(archivo))


if __name__ == "__main__":
    main()
