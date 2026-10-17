from app.errors import BusinessError

ALLOWED_DOMAINS_KEY = "auth.allowed_domains"
ANY_DOMAIN = "*"
DEFAULT_ALLOWED_DOMAINS = ["@unq.edu.ar"]


def normalize_domains(value: object) -> list[str]:
    """Valida y normaliza el valor a guardar en `auth.allowed_domains`.

    Acepta lista de `@dominio` o `"*"`. Rechaza lo demás con BusinessError (422).
    """
    if not isinstance(value, list):
        raise BusinessError("Los dominios deben ser una lista")
    normalized = []
    for entry in value:
        if not isinstance(entry, str):
            raise BusinessError("Cada dominio debe ser un texto")
        clean = entry.strip().lower()
        if clean != ANY_DOMAIN and not clean.startswith("@"):
            raise BusinessError('Cada dominio debe empezar con @ (o ser "*")')
        normalized.append(clean)
    if not normalized:
        raise BusinessError('La lista no puede quedar vacía; usá "*" para permitir todos los dominios')
    return normalized


def is_domain_allowed(email: str, allowed: list[str]) -> bool:
    """True si el email puede entrar con la lista vigente (`"*"` = todos)."""
    if ANY_DOMAIN in allowed:
        return True
    normalized = email.strip().lower()
    return any(normalized.endswith(domain) for domain in allowed)
