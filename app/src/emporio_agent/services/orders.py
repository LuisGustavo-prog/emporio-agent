"""Casos de uso de pedido: verificar identidade, consultar status, rastreio e previsao. A verificacao de identidade vive aqui, nao no prompt.

Pode importar de: core, db
Nao deve importar de: tools, agent, cli
Fase de implementacao: F4
"""

import re

from emporio_agent.config import Settings
from emporio_agent.core.errors import IdentityVerificationError
from emporio_agent.core.rules.order_status import describe_order_status
from emporio_agent.db.connection import open_connection
from emporio_agent.db.orders import get_order, get_order_customer, get_order_item_details


def _digits(value: str) -> str:
    return re.sub(r"\D", "", value)


def consult_order(settings: Settings, order_id: int, email: str | None = None, phone: str | None = None) -> dict:
    if not email and not phone:
        raise IdentityVerificationError("Informe o e-mail ou telefone usado no pedido.")
    with open_connection(settings) as conn:
        order = get_order(conn, order_id)
        owner = get_order_customer(conn, order_id)
        if order is None or owner is None:
            raise IdentityVerificationError("Nao foi possivel validar os dados do pedido. Confira o numero e o contato informado.")
        if email and email.strip().casefold() != owner.email.casefold():
            raise IdentityVerificationError("Os dados informados nao correspondem ao titular do pedido.")
        if phone and _digits(phone) != _digits(owner.phone):
            raise IdentityVerificationError("Os dados informados nao correspondem ao titular do pedido.")
        data = {
            "order_id": order.order_id,
            "customer_name": owner.name,
            "status": order.status.value,
            "status_message": describe_order_status(order.status),
            "total_brl": str(order.total_brl),
            "order_date": order.order_date.isoformat(),
            "tracking_code": order.tracking_code,
            "estimated_delivery": order.estimated_delivery.isoformat() if order.estimated_delivery else None,
            "notes": order.notes if order.status.value == "cancelled" else None,
            "items": get_order_item_details(conn, order_id),
        }
        if order.status.value in {"pending", "confirmed"}:
            data["cancellation_note"] = "Para solicitar cancelamento, vou encaminhar o pedido a um atendente."
        return data
