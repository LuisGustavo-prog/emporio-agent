"""Caso de uso de devolucao e troca: carrega o pedido, verifica identidade e aplica core.rules.returns.

Pode importar de: core, db, services.orders
Nao deve importar de: tools, agent, cli
Fase de implementacao: F4
"""

from datetime import date

from emporio_agent.config import Settings
from emporio_agent.core.constants import REFUND_BUSINESS_DAYS
from emporio_agent.core.enums import OrderStatus
from emporio_agent.core.errors import IdentityVerificationError
from emporio_agent.core.rules.returns import evaluate_return
from emporio_agent.db.connection import open_connection
from emporio_agent.db.orders import get_order, get_order_customer
from emporio_agent.services.orders import _digits


def evaluate_order_return(settings: Settings, order_id: int, return_type: str, today: date,
                          email: str | None = None, phone: str | None = None,
                          received_date: date | None = None, online_purchase: bool = True) -> dict:
    if not email and not phone:
        raise IdentityVerificationError("Informe o e-mail ou telefone usado no pedido.")
    with open_connection(settings) as conn:
        order = get_order(conn, order_id)
        owner = get_order_customer(conn, order_id)
        if order is None or owner is None:
            raise IdentityVerificationError("Nao foi possivel validar os dados do pedido. Confira o numero e o contato informado.")
        if (email and email.strip().casefold() != owner.email.casefold()) or (phone and _digits(phone) != _digits(owner.phone)):
            raise IdentityVerificationError("Os dados informados nao correspondem ao titular do pedido.")
        is_regret = return_type == "arrependimento"
        approximate_receipt = False
        if is_regret:
            if received_date is not None:
                decision_date = received_date
            elif order.status is OrderStatus.DELIVERED and order.estimated_delivery:
                decision_date = order.estimated_delivery
                approximate_receipt = True
            else:
                decision_date = None
        else:
            decision_date = order.order_date
        if decision_date is None:
            raise ValueError("Nao ha data de recebimento registrada. Informe a data aproximada ou procure um atendente.")
        decision = evaluate_return(decision_date, today, return_type, online_purchase)
        return {"eligible": decision.eligible, "reason": decision.reason,
                "days_elapsed": decision.days_elapsed,
                "deadline": decision.deadline.isoformat() if decision.deadline else None,
                "human_review": decision.human_review,
                "receipt_date_approximate": approximate_receipt,
                "refund_in_business_days": REFUND_BUSINESS_DAYS if decision.eligible and is_regret else None,
                "return_shipping_paid_by_store": bool(decision.eligible and is_regret),
                "requirements": ["Embalagem original", "Sem sinais de uso", "Acessorios e manuais completos"] if decision.eligible else []}
