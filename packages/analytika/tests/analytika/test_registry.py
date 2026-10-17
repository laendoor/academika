import pytest
from analytika import find_metric, list_metrics
from analytika.registry import REGISTRY, register
from analytika.smoke import SmokeMetrica


@pytest.fixture
def registry_snapshot():
    snapshot = dict(REGISTRY)
    yield
    REGISTRY.clear()
    REGISTRY.update(snapshot)


def test_smoke_registrada_al_importar():
    metrica = find_metric("smoke")
    assert isinstance(metrica, SmokeMetrica)
    assert "smoke" in [m.key for m in list_metrics()]


def test_register_duplicada_falla(registry_snapshot):
    with pytest.raises(ValueError, match="smoke"):
        register(SmokeMetrica())


def test_find_desconocida_es_none(registry_snapshot):
    assert find_metric("no-existe") is None
