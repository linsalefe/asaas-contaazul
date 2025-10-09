import httpx
from datetime import datetime, timedelta
from loguru import logger
from config.settings import settings
from utils.db import session_scope
from models import OAuthToken
from sqlalchemy import select

class ContaAzulOAuth:
    def __init__(self):
        self.auth_base = settings.CONTA_AZUL_AUTH_URL.rstrip('/')
        self.client_id = settings.CONTA_AZUL_CLIENT_ID
        self.client_secret = settings.CONTA_AZUL_CLIENT_SECRET
        self.redirect_uri = settings.CONTA_AZUL_REDIRECT_URI

    def get_authorization_url(self, state: str = "random_state_123") -> str:
        """Retorna a URL para o usuário autorizar o app"""
        scope = "openid+profile+aws.cognito.signin.user.admin"
        return (
            f"{self.auth_base}/oauth2/authorize?"
            f"response_type=code&"
            f"client_id={self.client_id}&"
            f"redirect_uri={self.redirect_uri}&"
            f"state={state}&"
            f"scope={scope}"
        )

    async def exchange_code_for_token(self, code: str) -> dict:
        """Troca o code por access_token e refresh_token"""
        url = f"{self.auth_base}/oauth2/token"
        
        # Basic Auth (Base64 de client_id:client_secret)
        import base64
        credentials = f"{self.client_id}:{self.client_secret}"
        b64_credentials = base64.b64encode(credentials.encode()).decode()
        
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Basic {b64_credentials}"
        }
        
        payload = {
            "grant_type": "authorization_code",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": self.redirect_uri,
            "code": code,
        }
        
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(url, headers=headers, data=payload)
            resp.raise_for_status()
            return resp.json()

    async def refresh_access_token(self, refresh_token: str) -> dict:
        """Renova o access_token usando o refresh_token"""
        url = f"{self.auth_base}/oauth2/token"
        
        import base64
        credentials = f"{self.client_id}:{self.client_secret}"
        b64_credentials = base64.b64encode(credentials.encode()).decode()
        
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Basic {b64_credentials}"
        }
        
        payload = {
            "grant_type": "refresh_token",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "refresh_token": refresh_token,
        }
        
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(url, headers=headers, data=payload)
            resp.raise_for_status()
            return resp.json()

    def save_token(self, token_data: dict):
        """Salva o token no banco"""
        expires_in = token_data.get("expires_in", 3600)
        expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
        
        with session_scope() as s:
            # Remove token antigo
            s.query(OAuthToken).filter_by(provider="contaazul").delete()
            
            # Salva novo token
            token = OAuthToken(
                provider="contaazul",
                access_token=token_data["access_token"],
                refresh_token=token_data.get("refresh_token"),
                expires_at=expires_at,
            )
            s.add(token)

    def get_valid_token(self) -> str | None:
        """Retorna um access_token válido ou None"""
        with session_scope() as s:
            stmt = select(OAuthToken).where(OAuthToken.provider == "contaazul")
            token = s.execute(stmt).scalar_one_or_none()
            
            if not token:
                return None
            
            # Se expirou, tenta renovar
            if token.expires_at and token.expires_at < datetime.utcnow():
                logger.info("Token expirado, renovando...")
                return None
            
            return token.access_token