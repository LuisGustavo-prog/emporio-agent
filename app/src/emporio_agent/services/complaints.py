"""Caso de uso de registro de reclamacao e retorno do protocolo.

Pode importar de: core, db
Nao deve importar de: tools, agent, cli
Fase de implementacao: F6
"""

from emporio_agent.config import Settings
from emporio_agent.core.constants import COMPLAINT_RETURN_BUSINESS_HOURS
from emporio_agent.core.errors import InvalidInputError
from emporio_agent.db.complaints import create_complaint
from emporio_agent.db.connection import open_connection


def register_complaint(settings: Settings, description: str, order_id: int | None = None,
                       customer_name: str | None = None, contact: str | None = None) -> dict:
    description = description.strip()
    if len(description) < 10:
        raise InvalidInputError("A descricao deve ter pelo menos 10 caracteres.")
    with open_connection(settings) as conn:
        complaint = create_complaint(conn, description, order_id, customer_name, contact)
    return {"protocol": complaint.protocol, "created_at": complaint.created_at,
            "response_sla_business_hours": COMPLAINT_RETURN_BUSINESS_HOURS}
