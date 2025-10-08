from fastapi import FastAPI, Request, HTTPException
from loguru import logger
from config.settings import settings
from utils.db import session_scope
from utils.idempotency import was_processed, mark_processed
from services.asaas_client import parse_asaas_webhook
from services.contaazul_client import ContaAzulClient

app = FastAPI(title="Asaas→ContaAzul MVP")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/asaas/webhook")
async def asaas_webhook(req: Request):
    # 1) Autenticação simples do webhook Asaas
    token = req.headers.get("asaas-access-token")
    if token != settings.ASAAS_WEBHOOK_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid webhook token")

    payload = await req.json()
    event, payment_id, external_ref, amount, payment_date = parse_asaas_webhook(payload)

    # 2) Idempotência
    with session_scope() as s:
        if was_processed(s, provider="asaas", event_type=event, event_id=f"{payment_id}:{event}"):
            return {"ok": True, "duplicate": True}

    # 3) Só atuamos em PAYMENT_RECEIVED
    if event != "PAYMENT_RECEIVED":
        logger.info(f"Ignorando evento {event} para payment {payment_id}")
        with session_scope() as s:
            mark_processed(s, "asaas", event, f"{payment_id}:{event}", payload)
        return {"ok": True, "ignored": event}

    if not external_ref:
        logger.error(f"Pagamento {payment_id} sem externalReference (parcela_id)")
        raise HTTPException(status_code=422, detail="externalReference ausente (esperado parcela_id)")

    parcela_id = external_ref
    data_pagamento = payment_date or "2025-01-01"

    # 4) Baixa na Conta Azul
    ca = ContaAzulClient()
    resp = await ca.baixar_parcela(
        parcela_id=parcela_id,
        valor_pago=float(amount),
        data_pagamento=data_pagamento,
        observacao=f"Asaas {payment_id}",
    )

    if resp.status_code // 100 != 2:
        logger.error(f"Erro ao baixar parcela {parcela_id} na Conta Azul: {resp.status_code} {resp.text}")
        raise HTTPException(status_code=502, detail={"conta_azul": resp.text})

    # 5) Marca processado
    with session_scope() as s:
        mark_processed(s, "asaas", event, f"{payment_id}:{event}", payload)

    return {"ok": True, "parcela_id": parcela_id}