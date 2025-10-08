from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')

    # Geral
    ENV: str = Field(default="dev")
    LOG_LEVEL: str = Field(default="INFO")

    # Banco (MVP: SQLite; Produção: Postgres)
    DATABASE_URL: str = Field(default="sqlite:///./data.db")

    # Segurança do webhook Asaas
    ASAAS_WEBHOOK_TOKEN: str = Field(default="changeme")

    # Conta Azul (MVP: token manual)
    CONTA_AZUL_BASE_URL: str = Field(default="https://api.contaazul.com")
    CONTA_AZUL_ACCESS_TOKEN: str = Field(default="")
    CONTA_AZUL_FIN_ACCOUNT_ID: str = Field(default="")

settings = Settings()