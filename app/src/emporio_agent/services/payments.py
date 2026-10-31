"""Caso de uso de simulacao de pagamento (PIX, debito, boleto, parcelas).

Pode importar de: core
Nao deve importar de: tools, agent, cli
Fase de implementacao: F3
"""

from decimal import Decimal

from emporio_agent.core.constants import BOLETO_SETTLEMENT_BUSINESS_DAYS, SPLIT_PAYMENT_MIN_BRL
from emporio_agent.core.enums import PaymentMethod
from emporio_agent.core.rules.payments import allowed_installments, simulate_payment


def quote_payment(total_brl: str | int | float | Decimal, method: str, installments: int = 1,
                  promotion_active: bool = False) -> dict:
    quote = simulate_payment(Decimal(str(total_brl)), method, installments, promotion_active)
    return {
        "method": quote.method.value,
        "original_total_brl": str(quote.original_total_brl),
        "total_brl": str(quote.total_brl),
        "installments": quote.installments,
        "installment_brl": str(quote.installment_brl) if quote.installment_brl is not None else None,
        "discount_brl": str(quote.discount_brl),
        "settlement_in_business_days": quote.settlement_in_business_days,
        "split_payment_allowed": quote.split_payment_allowed,
        "available_installments": list(allowed_installments(quote.total_brl)) if quote.method is PaymentMethod.CREDIT else [],
        "interest": "sem juros" if quote.method is PaymentMethod.CREDIT else None,
    }


def payment_options(total_brl: str | int | float | Decimal, promotion_active: bool = False) -> dict:
    total = Decimal(str(total_brl))
    if not total.is_finite() or total <= 0:
        raise ValueError("O total deve ser maior que zero.")
    pix = simulate_payment(total, PaymentMethod.PIX, promotion_active=promotion_active)
    installments = allowed_installments(total)
    return {
        "original_total_brl": str(total.quantize(Decimal("0.01"))),
        "promotion_active": promotion_active,
        "pix": {"total_brl": str(pix.total_brl), "discount_brl": str(pix.discount_brl)},
        "debit": {"total_brl": str(total.quantize(Decimal("0.01")))},
        "boleto": {"total_brl": str(total.quantize(Decimal("0.01"))),
                   "settlement_in_business_days": BOLETO_SETTLEMENT_BUSINESS_DAYS},
        "credit": {"total_brl": str(total.quantize(Decimal("0.01"))),
                   "interest": "sem juros", "installments": list(installments),
                   "installment_values_brl": {str(n): str((total / n).quantize(Decimal("0.01"))) for n in installments}},
        "split_payment_allowed": total > Decimal(SPLIT_PAYMENT_MIN_BRL),
    }
