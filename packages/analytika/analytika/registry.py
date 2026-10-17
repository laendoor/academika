from analytika.base import MetricaBase

REGISTRY: dict[str, MetricaBase] = {}


def register(metrica: MetricaBase) -> MetricaBase:
    if metrica.key in REGISTRY:
        raise ValueError(f"métrica '{metrica.key}' ya registrada")
    REGISTRY[metrica.key] = metrica
    return metrica


def find_metric(key: str) -> MetricaBase | None:
    return REGISTRY.get(key)


def list_metrics() -> list[MetricaBase]:
    return list(REGISTRY.values())
