from typing import Any

from analytika.errors import MetricaParamError


def param(params: dict[str, Any], key: str) -> str | None:
    value = params.get(key)
    if value is None:
        return None
    if not isinstance(value, str):
        raise MetricaParamError(f"parámetro '{key}' repetido")
    value = value.strip()
    return value or None


def require_param(params: dict[str, Any], key: str) -> str:
    value = param(params, key)
    if value is None:
        raise MetricaParamError(f"falta el parámetro '{key}'")
    return value
