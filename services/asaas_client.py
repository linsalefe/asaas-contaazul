from typing import Optional, Tuple

def parse_asaas_webhook(payload: dict) -> Tuple[str, str, Optional[str], float, Optional[str]]:
    """
    Retorna (event, payment_id, external_ref, amount, payment_date)
    """
    event = payload.get("event")
    p = payload.get("payment") or {}
    payment_id = p.get("id")
    external_ref = p.get("externalReference")
    amount = float(p.get("value") or p.get("netValue") or 0.0)
    payment_date = p.get("paymentDate")
    return event, payment_id, external_ref, amount, payment_date