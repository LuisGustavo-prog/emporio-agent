"""Regras de troca e devolucao: arrependimento, defeito, preferencia, itens nao elegiveis, prazos.

Pode importar de: core.constants, core.enums, core.models
Nao deve importar de: db, rag, services, tools, agent, cli
Fase de implementacao: F2
Funcoes puras, sem I/O. Data e hora entram como argumento.
"""

from dataclasses import dataclass
from datetime import date

from emporio_agent.core.constants import DEFECT_EXCHANGE_DAYS, LEGAL_WARRANTY_DAYS, RETURN_WINDOW_DAYS
from emporio_agent.core.enums import ReturnType


@dataclass(frozen=True, slots=True)
class ReturnDecision:
    eligible: bool
    reason: str
    days_elapsed: int
    deadline: date | None
    human_review: bool = False


def evaluate_return(purchase_date: date, request_date: date, return_type: ReturnType | str,
                    online_purchase: bool = True) -> ReturnDecision:
    if request_date < purchase_date:
        raise ValueError("A data da solicitacao nao pode anteceder a compra.")
    try:
        return_type = ReturnType(return_type)
    except ValueError as exc:
        raise ValueError("Tipo de devolucao nao reconhecido.") from exc
    elapsed = (request_date - purchase_date).days
    if return_type is ReturnType.ARREPENDIMENTO and not online_purchase:
        return ReturnDecision(False, "Arrependimento aplica-se a compras online; encaminhar compra presencial ao atendente.", elapsed, None, True)
    if return_type is ReturnType.PREFERENCIA:
        deadline = purchase_date.fromordinal(purchase_date.toordinal() + RETURN_WINDOW_DAYS)
        eligible = elapsed <= RETURN_WINDOW_DAYS
        reason = "Troca por preferencia em ate 7 dias, sujeita a disponibilidade e condicao do produto." if eligible else "Prazo de troca por preferencia encerrado."
        return ReturnDecision(eligible, reason, elapsed, deadline, eligible)
    if return_type is ReturnType.ARREPENDIMENTO:
        deadline = purchase_date.fromordinal(purchase_date.toordinal() + RETURN_WINDOW_DAYS)
        eligible = elapsed <= RETURN_WINDOW_DAYS
        return ReturnDecision(eligible, "Dentro do prazo de arrependimento." if eligible else "Prazo de arrependimento encerrado.", elapsed, deadline)
    deadline = purchase_date.fromordinal(purchase_date.toordinal() + DEFECT_EXCHANGE_DAYS)
    eligible = elapsed <= DEFECT_EXCHANGE_DAYS
    reason = "Dentro do prazo para troca por defeito." if eligible else "Prazo de troca encerrado; acionar garantia do fabricante e encaminhar ao atendente."
    return ReturnDecision(eligible, reason, elapsed, deadline, not eligible and elapsed <= LEGAL_WARRANTY_DAYS)
