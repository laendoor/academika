class MetricaError(Exception):
    """Error de negocio de una métrica; clika lo muestra sin tumbar el REPL."""


class MetricaParamError(MetricaError):
    """Parámetro faltante, repetido o con formato inválido."""


class MetricaNotFoundError(MetricaError):
    """El recurso pedido por la métrica no existe."""
