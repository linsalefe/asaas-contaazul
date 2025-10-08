from sqlalchemy import Column, BigInteger, Text, JSON, DateTime
from sqlalchemy.sql import func
from utils.db import Base, engine

class ProcessedEvent(Base):
    __tablename__ = "processed_events"
    id = Column(BigInteger, primary_key=True)
    provider = Column(Text, nullable=False)
    event_type = Column(Text, nullable=False)
    event_id = Column(Text, nullable=False)
    payload = Column(JSON, nullable=False)
    processed_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

class PaymentLink(Base):
    __tablename__ = "payment_links"
    id = Column(BigInteger, primary_key=True)
    asaas_payment_id = Column(Text, unique=True)
    asaas_external_ref = Column(Text)
    contaazul_parcela_id = Column(Text)
    status = Column(Text, nullable=False, default="pending")

# Cria tabelas automaticamente no MVP
Base.metadata.create_all(bind=engine)