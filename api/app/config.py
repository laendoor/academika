from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuración de la aplicación vía variables de entorno.

    Resolución (mayor a menor prioridad):
      1. Variable de entorno del sistema (ej: export JWT_SECRET_KEY=...)
      2. Archivo .env en el directorio de arranque de la app
      3. Default definido en esta clase (solo válido para dev/test local)

    Los nombres de campo se mapean a env vars en UPPER_SNAKE_CASE automáticamente.
    Por ejemplo, `jwt_secret_key` se lee de JWT_SECRET_KEY.

    Ver .env.example en la raíz del repo para las vars requeridas en producción.
    """

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+asyncpg://academika:academika@localhost:5432/academika"

    # Requerido en producción: JWT_SECRET_KEY debe ser un string aleatorio largo.
    # El default solo sirve para dev/test local — nunca deployar con él.
    jwt_secret_key: str = "dev-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7
    reset_token_expire_hours: int = 1
    invite_token_expire_hours: int = 72

    # Requerido en producción: RESEND_API_KEY. Sin él, el envío de emails falla en runtime.
    resend_api_key: str = ""
    resend_from_email: str = "noreply@academika.unq.edu.ar"
    frontend_url: str = "http://localhost:3000"


settings = Settings()
