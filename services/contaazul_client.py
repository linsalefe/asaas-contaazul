import httpx
from loguru import logger
from config.settings import settings

class ContaAzulClient:
    def __init__(self, access_token: str | None = None):
        self.base = settings.CONTA_AZUL_API_URL.rstrip('/')
        self.token = access_token or settings.CONTA_AZUL_ACCESS_TOKEN
        if not self.token:
            logger.warning("CONTA_AZUL_ACCESS_TOKEN não configurado. Configure no .env para testes.")

    def _headers(self):
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

    async def baixar_parcela(self, parcela_id: str, valor_pago: float, data_pagamento: str, observacao: str = "") -> httpx.Response:
        url = f"{self.base}/v1/financeiro/eventos-financeiros/parcelas/{parcela_id}/baixa"
        payload = {
            "data_pagamento": data_pagamento,
            "valor_pago": valor_pago,
            "id_conta_financeira": settings.CONTA_AZUL_FIN_ACCOUNT_ID,
            "observacao": observacao[:255] if observacao else None,
        }
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(url, headers=self._headers(), json=payload)
            return resp