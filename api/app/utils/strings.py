def or_none(value: str) -> str | None:
    stripped = value.strip()
    return stripped if stripped else None


def is_integer(value: str) -> bool:
    try:
        int(value.strip())
        return True
    except ValueError:
        return False
