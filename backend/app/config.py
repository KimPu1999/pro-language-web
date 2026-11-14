from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_env: str = "development"
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
    redis_url: str = "redis://localhost:6379/0"
    db_pool_size: int = 5
    db_max_overflow: int = 10
    db_pool_timeout_seconds: int = 15
    db_pool_recycle_seconds: int = 1800
    db_connect_timeout_seconds: int = 5
    slow_request_ms: int = 500
    runner_enabled: bool = False
    runner_queue_name: str = "codemaster:execution"
    max_source_code_bytes: int = 100_000
    ai_provider: str = "disabled"
    ai_model: str = "disabled"
    ai_enabled: bool = False
    ai_request_timeout_seconds: int = 30
    ai_daily_request_limit: int = 20
    ai_max_input_chars: int = 12000
    video_provider: str = "disabled"
    video_enabled: bool = False
    video_token_ttl_seconds: int = 900
    collaboration_enabled: bool = False
    collaboration_max_message_bytes: int = 262144
    github_enabled: bool = False
    github_app_id: str = ""
    github_client_id: str = ""
    github_webhook_secret: str = ""
    github_token_key: str = ""
    oidc_enabled: bool = False
    oidc_issuer: str = ""
    oidc_client_id: str = ""
    oidc_client_secret: str = ""
    saml_enabled: bool = False
    saml_entity_id: str = ""
    saml_certificate: str = ""
    webauthn_enabled: bool = False
    webauthn_rp_id: str = "localhost"
    webauthn_origin: str = "http://localhost:3000"
    scim_enabled: bool = False
    security_audit_retention_days: int = 365
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    @property
    def cors_origin_list(self) -> list[str]:
        return [v.strip() for v in self.cors_origins.split(",") if v.strip()]
settings = Settings()
