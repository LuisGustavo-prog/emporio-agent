"""Traducao de status de pedido para linguagem de cliente.

Pode importar de: core.constants, core.enums, core.models
Nao deve importar de: db, rag, services, tools, agent, cli
Fase de implementacao: F4
Funcoes puras, sem I/O. Data e hora entram como argumento.
"""

from emporio_agent.core.enums import OrderStatus

_STATUS_MESSAGES = {
    OrderStatus.PENDING: "Seu pedido esta aguardando confirmacao.",
    OrderStatus.CONFIRMED: "Seu pedido foi confirmado e esta sendo preparado.",
    OrderStatus.SHIPPED: "Seu pedido foi enviado.",
    OrderStatus.DELIVERED: "Seu pedido consta como entregue.",
    OrderStatus.CANCELLED: "Seu pedido foi cancelado.",
}


def describe_order_status(status: OrderStatus | str) -> str:
    try:
        return _STATUS_MESSAGES[OrderStatus(status)]
    except (ValueError, KeyError) as exc:
        raise ValueError("Status de pedido desconhecido.") from exc
