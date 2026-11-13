from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/codemaster"
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"
    log_level: str = "INFO"
    session_ttl_hours: int = 24 * 7
    verification_ttl_hours: int = 24
    reset_ttl_minutes: int = 30
    cookie_secure: bool = False
    cookie_samesite: str = "lax"
    app_base_url: str = "http://localhost:3000"
    mailer_mode: str = "console"
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_tls: bool = True
    mail_from: str = "no-reply@codemaster.local"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    @property
    def cors_origin_list(self) -> list[str]:
        return [v.strip() for v in self.cors_origins.split(",") if v.strip()]
settings = Settings()
