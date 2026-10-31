"""Persistir reclamacoes e gerar protocolo.

Pode importar de: core, db.connection
Nao deve importar de: core.rules, services, tools, agent, cli
Fase de implementacao: F6
"""

from datetime import datetime
from uuid import uuid4

from emporio_agent.core.models import Complaint


def create_complaint(conn, description: str, order_id: int | None = None,
                     customer_name: str | None = None, contact: str | None = None,
                     now: datetime | None = None) -> Complaint:
    now = now or datetime.now().astimezone()
    protocol = f"EMP-{now:%Y%m%d}-{uuid4().hex[:8].upper()}"
    created_at = now.isoformat()
    with conn:
        conn.execute(
            "INSERT INTO complaints(protocol,order_id,customer_name,contact,description,created_at) VALUES(?,?,?,?,?,?)",
            (protocol, order_id, customer_name, contact, description, created_at),
        )
    return Complaint(protocol, order_id, customer_name, contact, description, created_at)
