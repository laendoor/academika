from analytika.base import MetricaBase
from analytika.metricas.avance_metrica import AvanceMetrica
from analytika.metricas.historia_metrica import HistoriaMetrica
from analytika.metricas.promedios_metrica import PromediosMetrica
from analytika.registry import register
from analytika.smoke import SmokeMetrica

METRICAS: tuple[MetricaBase, ...] = (SmokeMetrica(), HistoriaMetrica(), PromediosMetrica(), AvanceMetrica())


def register_metricas() -> None:
    """Registra las métricas del motor; se llama una vez al importar `analytika`."""
    for metrica in METRICAS:
        register(metrica)
