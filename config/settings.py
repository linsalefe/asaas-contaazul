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

    # Conta Azul - URLs corretas
    CONTA_AZUL_AUTH_URL: str = Field(default="https://auth.contaazul.com")
    CONTA_AZUL_API_URL: str = Field(default="https://api-v2.contaazul.com")
    CONTA_AZUL_ACCESS_TOKEN: str = Field(default="")
    CONTA_AZUL_FIN_ACCOUNT_ID: str = Field(default="")
    
    # OAuth2 Conta Azul
    CONTA_AZUL_CLIENT_ID: str = Field(default="")
    CONTA_AZUL_CLIENT_SECRET: str = Field(default="")
    CONTA_AZUL_REDIRECT_URI: str = Field(default="http://localhost:8000/oauth/callback")

settings = Settings()