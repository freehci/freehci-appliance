"""Applikasjonskonfigurasjon (12-factor via miljøvariabler)."""

from functools import lru_cache
from pathlib import Path

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "FreeHCI"
    debug: bool = False
    api_v1_prefix: str = "/api/v1"

    database_url: str = Field(
        default="sqlite:///./data/freehci.db",
        description="SQLAlchemy URL, f.eks. sqlite:///./data/freehci.db eller postgresql+psycopg://user:pass@db:5432/freehci",
    )

    cors_origins: str = Field(
        default="http://localhost:5173,http://127.0.0.1:5173",
        description="Kommaseparerte origins for CORS",
    )

    redis_url: str = Field(default="redis://redis:6379/0")

    celery_broker_url: str | None = Field(default=None)
    celery_result_backend: str | None = Field(default=None)

    # Katalog for dynamiske backend-plugins (Python-moduler / pakker)
    plugins_path: str | None = Field(
        default=None,
        description="Valgfri sti hvor ekstra .whl eller pakker kan ligge og importeres.",
    )

    # Hemmelighet for enkel API-nøkkel senere; brukes ikke i fase 1 utover struktur
    internal_api_secret: SecretStr | None = Field(default=None)

    jwt_secret: SecretStr = Field(
        default=SecretStr("dev-only-change-JWT_SECRET-in-production"),
        description="Hemmelighet for JWT (sett JWT_SECRET i miljø i produksjon)",
    )
    jwt_expire_minutes: int = Field(default=10080, ge=5, le=525600)  # 7 dager som standard

    freehci_skip_auth: bool = Field(
        default=False,
        description="FREEHCI_SKIP_AUTH=1 deaktiverer API-auth (kun automatiske tester)",
    )

    upload_root: str = Field(
        default="data/uploads",
        description="Rotkatalog for opplastede filer (logoer m.m.), relativ til arbeidskatalog eller absolutt sti",
    )

    mib_root: str = Field(
        default="data/mibs",
        description="Katalog for opplastede SNMP-MIB-filer (.mib/.txt), relativ eller absolutt sti",
    )

    mib_compiled_root: str = Field(
        default="data/mibs_compiled",
        description="Katalog for PySNMP-kompilerte MIB-moduler (.py), relativ eller absolutt sti",
    )

    mib_upload_max_bytes: int = Field(
        default=20 * 1024 * 1024,
        ge=1024 * 1024,
        le=100 * 1024 * 1024,
        description="Maks størrelse per opplastet MIB-fil (bytes), standard 20 MiB",
    )

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def effective_celery_broker(self) -> str:
        return self.celery_broker_url or self.redis_url

    @property
    def effective_celery_backend(self) -> str:
        return self.celery_result_backend or self.redis_url

    @property
    def upload_root_path(self) -> Path:
        return Path(self.upload_root).expanduser()

    @property
    def mib_root_path(self) -> Path:
        return Path(self.mib_root).expanduser()

    @property
    def mib_compiled_path(self) -> Path:
        return Path(self.mib_compiled_root).expanduser()


@lru_cache
def get_settings() -> Settings:
    return Settings()
