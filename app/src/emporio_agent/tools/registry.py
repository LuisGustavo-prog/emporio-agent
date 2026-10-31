"""Registrar as tools, expor a lista de schemas para o LLM e despachar a chamada pelo nome.

Pode importar de: tools.*
Nao deve importar de: db, agent, cli
Fase de implementacao: F3
"""

from emporio_agent.config import Settings
from emporio_agent.tools.base import Tool
from emporio_agent.tools.catalog import TOOLS as CATALOG_TOOLS
from emporio_agent.tools.complaints import TOOL as COMPLAINTS_TOOL
from emporio_agent.tools.orders import TOOL as ORDERS_TOOL
from emporio_agent.tools.payments import TOOL as PAYMENTS_TOOL
from emporio_agent.tools.policies import TOOL as POLICIES_TOOL
from emporio_agent.tools.returns import TOOL as RETURNS_TOOL
from emporio_agent.tools.store import TOOL as STORE_TOOL
from emporio_agent.tools.shipping import TOOL as SHIPPING_TOOL

TOOLS: tuple[Tool, ...] = (*CATALOG_TOOLS, PAYMENTS_TOOL, ORDERS_TOOL, RETURNS_TOOL,
                           POLICIES_TOOL, STORE_TOOL, COMPLAINTS_TOOL, SHIPPING_TOOL)
_BY_NAME = {tool.name: tool for tool in TOOLS}


def schemas() -> list[dict]:
    return [tool.schema() for tool in TOOLS]


def dispatch(settings: Settings, name: str, arguments: str | dict) -> str:
    tool = _BY_NAME.get(name)
    if tool is None:
        return '{"ok":false,"error":"Ferramenta desconhecida."}'
    return tool.invoke(settings, arguments)
