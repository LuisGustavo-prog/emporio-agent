"""Regras de horario de funcionamento e feriados.

Pode importar de: core.constants, core.enums, core.models
Nao deve importar de: db, rag, services, tools, agent, cli
Fase de implementacao: F2
Funcoes puras, sem I/O. Data e hora entram como argumento.
"""

from dataclasses import dataclass
from datetime import date, datetime, time
from zoneinfo import ZoneInfo

from emporio_agent.core.constants import STORE_SATURDAY_HOURS, STORE_TIMEZONE, STORE_WEEKDAY_HOURS


@dataclass(frozen=True, slots=True)
class StoreHours:
    is_open: bool
    local_datetime: datetime
    next_opening: datetime | None


def is_store_open(local_datetime: datetime, is_holiday: bool = False) -> bool:
    if local_datetime.tzinfo is None:
        raise ValueError("Informe data e hora com fuso horario.")
    if is_holiday or local_datetime.weekday() == 6:
        return False
    opening, closing = STORE_SATURDAY_HOURS if local_datetime.weekday() == 5 else STORE_WEEKDAY_HOURS
    current = local_datetime.timetz().replace(tzinfo=None)
    return time(opening) <= current < time(closing)


def store_status(now: datetime, is_holiday: bool = False, holidays: frozenset[date] = frozenset()) -> StoreHours:
    local = now.astimezone(ZoneInfo(STORE_TIMEZONE)) if now.tzinfo else now.replace(tzinfo=ZoneInfo(STORE_TIMEZONE))
    opened = is_store_open(local, is_holiday)
    if opened:
        return StoreHours(True, local, None)
    next_day = local.date()
    for _ in range(8):
        next_day = date.fromordinal(next_day.toordinal() + 1)
        if next_day.weekday() == 6 or next_day in holidays:
            continue
        opening = STORE_SATURDAY_HOURS[0] if next_day.weekday() == 5 else STORE_WEEKDAY_HOURS[0]
        candidate = datetime.combine(next_day, time(opening), tzinfo=local.tzinfo)
        return StoreHours(False, local, candidate)
    return StoreHours(False, local, None)
