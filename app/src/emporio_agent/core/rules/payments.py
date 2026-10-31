"""Regras de parcelamento (minimos por faixa), combinacao de formas de pagamento e boleto.

Pode importar de: core.constants, core.enums, core.models
Nao deve importar de: db, rag, services, tools, agent, cli
Fase de implementacao: F2
Funcoes puras, sem I/O. Data e hora entram como argumento.
"""

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP

from emporio_agent.core.constants import (
    BOLETO_SETTLEMENT_BUSINESS_DAYS,
    INSTALLMENT_TIERS,
    PIX_DISCOUNT_PERCENT,
    SPLIT_PAYMENT_MIN_BRL,
)
from emporio_agent.core.enums import PaymentMethod

CENT = Decimal("0.01")


@dataclass(frozen=True, slots=True)
class PaymentQuote:
    method: PaymentMethod
    original_total_brl: Decimal
    total_brl: Decimal
    installments: int
    installment_brl: Decimal | None
    discount_brl: Decimal = Decimal("0.00")
    settlement_in_business_days: int | None = None
    split_payment_allowed: bool = False


def allowed_installments(total_brl: Decimal) -> tuple[int, ...]:
    """Lista parcelas disponiveis, considerando valor minimo por parcela."""
    if total_brl <= 0:
        raise ValueError("O total deve ser maior que zero.")
    if total_brl < Decimal(INSTALLMENT_TIERS[0][1]):
        return ()
    max_available = 1
    for max_installments, minimum in INSTALLMENT_TIERS:
        if total_brl / max_installments >= Decimal(minimum):
            max_available = max(max_available, max_installments)
    return tuple(range(1, max_available + 1))


def simulate_payment(
    total_brl: Decimal,
    method: PaymentMethod | str,
    installments: int = 1,
    promotion_active: bool = False,
) -> PaymentQuote:
    if not total_brl.is_finite() or total_brl <= 0:
        raise ValueError("O total deve ser maior que zero.")
    try:
        method = PaymentMethod(method)
    except ValueError as exc:
        raise ValueError("Forma de pagamento nao suportada.") from exc

    if method is PaymentMethod.CREDIT:
        allowed = allowed_installments(total_brl)
        if installments not in allowed:
            raise ValueError(f"Parcelamento indisponivel. Opcoes: {', '.join(map(str, allowed)) or 'a vista'}.")
        installment_value = (total_brl / installments).quantize(CENT, rounding=ROUND_HALF_UP)
        total = total_brl.quantize(CENT)
        return PaymentQuote(method, total, total, installments, installment_value,
                            split_payment_allowed=total_brl > SPLIT_PAYMENT_MIN_BRL)

    if installments != 1:
        raise ValueError("Parcelamento so esta disponivel no cartao de credito.")
    discount = Decimal("0")
    final_total = total_brl
    if method is PaymentMethod.PIX and not promotion_active:
        discount = (total_brl * Decimal(PIX_DISCOUNT_PERCENT) / Decimal(100)).quantize(CENT, rounding=ROUND_HALF_UP)
        final_total = total_brl - discount
    return PaymentQuote(
        method=method,
        original_total_brl=total_brl.quantize(CENT),
        total_brl=final_total.quantize(CENT),
        installments=1,
        installment_brl=None,
        discount_brl=discount,
        settlement_in_business_days=BOLETO_SETTLEMENT_BUSINESS_DAYS if method is PaymentMethod.BOLETO else None,
    )
