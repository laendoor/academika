from datetime import date


def parse_date(value: str) -> date:
    return date(*reversed([int(p) for p in value.strip().split("/")]))


def date_to_year_term(d: date) -> tuple[int, str]:
    term = "2C" if d.month >= 7 else "1C"
    return d.year, term
