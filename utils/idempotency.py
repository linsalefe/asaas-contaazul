from sqlalchemy import select
from models import ProcessedEvent

def was_processed(session, provider: str, event_type: str, event_id: str) -> bool:
    q = select(ProcessedEvent.id).where(
        ProcessedEvent.provider == provider,
        ProcessedEvent.event_type == event_type,
        ProcessedEvent.event_id == event_id,
    )
    return session.execute(q).scalar() is not None

def mark_processed(session, provider: str, event_type: str, event_id: str, payload: dict):
    pe = ProcessedEvent(
        provider=provider,
        event_type=event_type,
        event_id=event_id,
        payload=payload
    )
    session.add(pe)