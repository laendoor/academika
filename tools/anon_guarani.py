#!/usr/bin/env python
# ruff: noqa: E402  — imports after version/dependency checks are intentional
"""
anon_guarani.py — Anonimizador de planillas SIU Guaraní
Proyecto Finisterre / Académika

Uso:
    python anon_guarani.py planilla.csv
    python anon_guarani.py planilla.xlsx

Dependencias:
    pip install pandas openpyxl faker InquirerPy
"""

# ── Argument pre-check ───────────────────────────────────────────────────────

import sys

if len(sys.argv) < 2:
    print("Uso: python anon_guarani.py <archivo.csv|xlsx>\n")
    print("Ejemplo: python anon_guarani.py datos_personales.csv")
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

_DEPS = [
    ("pandas",     "pandas"),
    ("openpyxl",   "openpyxl"),
    ("faker",      "Faker"),
    ("InquirerPy", "InquirerPy"),
]
_missing = [pkg for mod, pkg in _DEPS if importlib.util.find_spec(mod) is None]
if _missing:
    print("Faltan dependencias. Instalá con:\n")
    print(f"  pip install {' '.join(_missing)}\n")
    sys.exit(1)

# ── Imports ───────────────────────────────────────────────────────────────────

import argparse
import hashlib
from collections.abc import Callable
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
from faker import Faker
from InquirerPy import inquirer

# ── Constants ─────────────────────────────────────────────────────────────────

_PRIME_P = 1_000_003   # prime multiplier para hash de IDs
_PRIME_K = 9_999_991   # prime aditivo para hash de IDs
_fake = Faker("es_AR")

_DATE_FORMATS = ["%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y", "%d/%m/%y", "%Y/%m/%d"]

# ── Helpers ───────────────────────────────────────────────────────────────────

def _int_seed(value: str) -> int:
    """Semilla entera determinística a partir de cualquier string."""
    return int(hashlib.sha256(str(value).strip().encode()).hexdigest()[:8], 16)

# ── Estrategias de ofuscación ─────────────────────────────────────────────────

def ofuscar_id(value: str) -> str:
    """
    Hash determinístico para DNI / legajo.
    Output: len(input) + 1 dígitos → preserva el "tamaño" del identificador
    y garantiza que no coincida con ningún valor real.

    Fórmula:
        hashed = (n × P + K) mod 10^len(input)   → misma cantidad de dígitos
        prefijo = (suma_dígitos(hashed) mod 9) + 1 → siempre 1-9
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


def ofuscar_email(value: str) -> str:
    """Email falso determinístico."""
    _fake.seed_instance(_int_seed(str(value)))
    return _fake.email()


def ofuscar_fecha(value: str, ref_id: str) -> str:
    """
    Corrimiento determinístico de fechas:
      - Offset de años = (seed(ref_id) % 5) + 1
        → mismo valor para todas las fechas del mismo estudiante
        → la trayectoria académica se preserva, solo cambia el año
      - El día se ajusta ±3 días como máximo para caer en el mismo día de semana
        → se preserva la estacionalidad (marzo = inicio, julio = exámenes, etc.)

    Maneja edge case 29-Feb: si el año destino no es bisiesto, usa 28-Feb.
    """
    raw = str(value).strip()
    parsed = None
    fmt_used = None
    for fmt in _DATE_FORMATS:
        try:
            parsed = datetime.strptime(raw, fmt).date()
            fmt_used = fmt
            break
        except ValueError:
            continue

    if parsed is None or fmt_used is None:
        return value  # formato no reconocido → sin cambios

    original_weekday = parsed.weekday()
    year_offset = (_int_seed(str(ref_id)) % 5) + 1

    try:
        shifted = parsed.replace(year=parsed.year + year_offset)
    except ValueError:
        # 29-Feb en año destino no bisiesto
        shifted = parsed.replace(year=parsed.year + year_offset, day=28)

    # Ajuste ±3 días para preservar día de semana
    delta = (original_weekday - shifted.weekday()) % 7
    if delta > 3:
        delta -= 7
    shifted += timedelta(days=delta)

    return shifted.strftime(fmt_used)


def ofuscar_anio(value: str, ref_id: str) -> str:
    """
    Corrimiento determinístico de un año suelto (ej: 2015 → 2017).
    Usa el mismo offset que ofuscar_fecha para que anio_ingreso y fecha_ingreso sean coherentes.
    """
    try:
        year = int(str(value).strip())
    except ValueError:
        return value
    year_offset = (_int_seed(str(ref_id)) % 5) + 1
    return str(year + year_offset)


def ofuscar_texto(value: str) -> str:
    """Texto genérico determinístico estilo lorem ipsum (catch-all)."""
    _fake.seed_instance(_int_seed(str(value)))
    return _fake.sentence(nb_words=4).rstrip(".")


# ── Registro de estrategias ───────────────────────────────────────────────────
# Formato: (label, descripción, función)   — fecha/anio tienen fn=None (requieren ref_id)

StrFn = Callable[[str], str]

STRATEGIES: dict[str, tuple[str, str, StrFn | None]] = {
    "id":      ("ID (DNI / legajo)", "hash numérico determinístico, mismo largo +1 dígito",           ofuscar_id),
    "nombre":  ("Nombre",            "nombre falso determinístico (locale argentina)",                 ofuscar_nombre),
    "apellido":("Apellido",          "apellido falso determinístico (locale argentina)",               ofuscar_apellido),
    "email":   ("Email",             "email falso determinístico (independiente de nombre/apellido)",  ofuscar_email),
    "fecha":   ("Fecha",             "corrimiento de fecha preservando trayectoria (pide ref. ID)",    None),
    "anio":    ("Año",               "corrimiento de año coherente con Fecha (pide ref. ID)",          None),
    "texto":   ("Texto genérico",    "lorem ipsum determinístico — catch-all para campos libres",      ofuscar_texto),
}

# ── Auto-detección de columnas sensibles conocidas ───────────────────────────
# Basado en los headers reales de las planillas del SIU Guaraní (proyecto nachoyegro).
# Claves en minúsculas normalizadas; la detección es case-insensitive.
#
# Nota: "nombre" se trata como nombre de persona solo si "apellido" también está
# presente en los headers (en planes/materias, "Nombre" refiere a la materia).

_KNOWN_SENSITIVE: dict[str, str] = {
    "legajo":            "id",
    "dni":               "id",
    "apellido":          "apellido",
    "nombre":            "nombre",       # ver nota arriba
    "email":             "email",
    "mail":              "email",
    "fecha":             "fecha",
    "fecha_ingreso":     "fecha",
    "fecha_cursada":     "fecha",
    "fecha_inscripcion": "fecha",
}

# Preferencia para auto-seleccionar el ref_id de fechas/años
_REF_ID_PREFERENCE = ["legajo", "dni"]


def detect_sensitive_columns(cols: list[str]) -> dict[str, str]:
    """
    Retorna {col_original: strategy} para las columnas reconocidas como sensibles.
    Aplica la heurística de 'nombre': solo se anonimiza si 'apellido' también está
    (en planes/materias, "Nombre" refiere a la materia, no a una persona).
    """
    normalized = {c.lower().strip(): c for c in cols}
    has_apellido = "apellido" in normalized

    result: dict[str, str] = {}
    for norm, original in normalized.items():
        strategy = _KNOWN_SENSITIVE.get(norm)
        if strategy is None:
            continue
        if norm == "nombre" and not has_apellido:
            continue
        result[original] = strategy
    return result


def auto_ref_col(cols: list[str], auto_cols: dict[str, str]) -> str | None:
    """
    Elige automáticamente la columna ref_id para fechas/años.
    Preferencia: legajo > dni. Si no hay ninguno, retorna None (habrá que preguntar).
    """
    normalized = {c.lower().strip(): c for c in cols}
    for pref in _REF_ID_PREFERENCE:
        if pref in normalized and normalized[pref] in auto_cols:
            return normalized[pref]
    return None


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


# ── Aplicar transformaciones ──────────────────────────────────────────────────

def apply_strategies(
    df: pd.DataFrame,
    col_strategies: dict[str, str],
    ref_col: str | None,
) -> pd.DataFrame:
    result = df.copy()
    for col, strategy in col_strategies.items():
        if strategy == "fecha":
            result[col] = [ofuscar_fecha(v, r) for v, r in zip(df[col], df[ref_col])]
        elif strategy == "anio":
            result[col] = [ofuscar_anio(v, r) for v, r in zip(df[col], df[ref_col])]
        else:
            fn = STRATEGIES[strategy][2]
            assert fn is not None
            result[col] = df[col].apply(fn)
    return result


# ── Flujo interactivo ─────────────────────────────────────────────────────────

def run(path: Path) -> None:
    df = load_file(path)
    cols = list(df.columns)

    print(f"\n{path.name}  →  {len(df)} filas, {len(cols)} columnas")
    print(f"Columnas: {', '.join(cols)}\n")

    # Paso 1: auto-detectar columnas sensibles conocidas y sus estrategias
    col_strategies = detect_sensitive_columns(cols)

    if col_strategies:
        print("Columnas sensibles detectadas automáticamente:")
        for col, strategy in col_strategies.items():
            print(f"  {col:25s} → {STRATEGIES[strategy][0]}")
        print()
    else:
        print("No se detectaron columnas sensibles conocidas.\n")

    # Paso 2: auto-detectar ref_id para fechas/años; preguntar solo si no hay ninguno
    needs_ref = any(s in ("fecha", "anio") for s in col_strategies.values())
    ref_col: str | None = None
    if needs_ref:
        ref_col = auto_ref_col(cols, col_strategies)
        if ref_col:
            print(f"Columna de referencia para fechas: {ref_col}\n")
        else:
            id_cols = [c for c, s in col_strategies.items() if s == "id"] or cols
            ref_col = inquirer.select(  # pyright: ignore[reportPrivateImportUsage]
                message="¿Qué columna usar como referencia para el corrimiento de fechas?",
                choices=id_cols,
                instruction="(garantiza el mismo corrimiento para todas las fechas del mismo estudiante)",
            ).execute()

    # Paso 3: columnas restantes — el usuario puede agregar más si quiere
    remaining = [c for c in cols if c not in col_strategies]
    if remaining:
        extra: list[str] = inquirer.checkbox(  # pyright: ignore[reportPrivateImportUsage]
            message="¿Querés anonimizar alguna columna adicional?",
            choices=remaining,
            instruction="(espacio para marcar, enter para continuar sin seleccionar)",
        ).execute()

        if extra:
            strategy_choices = [
                {"name": f"{label}  —  {desc}", "value": key}
                for key, (label, desc, _) in STRATEGIES.items()
            ]
            for col in extra:
                strategy = inquirer.select(  # pyright: ignore[reportPrivateImportUsage]
                    message=f"Estrategia para '{col}':",
                    choices=strategy_choices,
                ).execute()
                col_strategies[col] = strategy

                if strategy in ("fecha", "anio") and ref_col is None:
                    id_cols = [c for c, s in col_strategies.items() if s == "id"] or cols
                    ref_col = inquirer.select(  # pyright: ignore[reportPrivateImportUsage]
                        message="¿Qué columna usar como referencia para el corrimiento de fechas?",
                        choices=id_cols,
                    ).execute()

    # Paso 4: preview + confirmar y guardar
    result = apply_strategies(df, col_strategies, ref_col)

    anon_cols = list(col_strategies.keys())
    print("\nPrevia — primeras 3 filas (columnas anonimizadas):\n")
    print(result[anon_cols].head(3).to_string(index=False))

    if inquirer.confirm(message="\n¿Guardar archivo?", default=True).execute():  # pyright: ignore[reportPrivateImportUsage]
        out = save_file(result, path)
        print(f"\nGuardado en: {out}\n")
    else:
        print("\nCancelado.\n")


# ── Entry point ───────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Anonimizador de planillas SIU Guaraní — Proyecto Finisterre"
    )
    parser.add_argument("archivo", help="CSV o Excel a anonimizar (.csv, .xlsx, .xls)")
    args = parser.parse_args()

    path = Path(args.archivo)
    if not path.exists():
        print(f"Archivo no encontrado: {path}")
        sys.exit(1)

    run(path)


if __name__ == "__main__":
    main()
