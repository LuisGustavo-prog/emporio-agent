"""Caso de uso de informacoes da loja (horario atual, contatos).

Pode importar de: core
Nao deve importar de: tools, agent, cli
Fase de implementacao: F5
"""

from datetime import datetime
from datetime import date
from zoneinfo import ZoneInfo

from emporio_agent.core.constants import (
    STORE_ADDRESS, STORE_EMAIL, STORE_PHONE, STORE_POSTAL_CODE, STORE_TIMEZONE, STORE_WHATSAPP,
)
from emporio_agent.core.rules.hours import store_status


def current_store_status(now: datetime | None = None) -> dict:
    now = now or datetime.now(ZoneInfo(STORE_TIMEZONE))
    is_holiday = False
    holidays_set: frozenset[date] = frozenset()
    try:
        import holidays
        calendar = holidays.country_holidays("BR", subdiv="MS", years=[now.year, now.year + 1])
        holidays_set = frozenset(calendar)
        is_holiday = now.date() in holidays_set
    except ImportError:
        pass
    status = store_status(now, is_holiday, holidays_set)
    return {"is_open": status.is_open, "local_time": status.local_datetime.isoformat(),
            "next_opening": status.next_opening.isoformat() if status.next_opening else None,
            "timezone": STORE_TIMEZONE,
            "holiday_note": "Feriados municipais podem alterar o atendimento.",
            "address": STORE_ADDRESS,
            "postal_code": STORE_POSTAL_CODE,
            "phone": STORE_PHONE,
            "whatsapp": STORE_WHATSAPP,
            "email": STORE_EMAIL}
