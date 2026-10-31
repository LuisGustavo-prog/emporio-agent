"""Contrato comum das tools: schema JSON enviado ao LLM, validacao de argumentos e conversao de erros em respostas seguras.

Pode importar de: core.errors
Nao deve importar de: db, services, agent, cli
Fase de implementacao: F3
"""

import json
import logging
import sqlite3
from dataclasses import dataclass
from typing import Any, Callable

from emporio_agent.config import Settings
from emporio_agent.core.errors import EmporioError

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class Tool:
    name: str
    description: str
    parameters: dict[str, Any]
    handler: Callable[[Settings, dict[str, Any]], Any]

    def schema(self) -> dict[str, Any]:
        return {"type": "function", "function": {
            "name": self.name, "description": self.description, "parameters": self.parameters,
        }}

    def invoke(self, settings: Settings, arguments: str | dict[str, Any]) -> str:
        try:
            payload = json.loads(arguments) if isinstance(arguments, str) else arguments
            if not isinstance(payload, dict):
                raise ValueError("Os argumentos devem ser um objeto JSON.")
            result = self.handler(settings, payload)
            response = {"ok": True, "data": result}
        except (EmporioError, ValueError, TypeError, KeyError) as exc:
            response = {"ok": False, "error": str(exc)}
        except (FileNotFoundError, RuntimeError):
            response = {"ok": False, "error": "Servico temporariamente indisponivel."}
        except sqlite3.Error:
            logger.exception("Erro de banco durante execucao da tool %s", self.name)
            response = {"ok": False, "error": "Servico temporariamente indisponivel."}
        except Exception:
            logger.exception("Erro interno durante execucao da tool %s", self.name)
            response = {"ok": False, "error": "Nao foi possivel concluir a consulta."}
        return json.dumps(response, ensure_ascii=False, default=str)


def required_text(args: dict[str, Any], name: str, max_length: int = 500) -> str:
    value = args.get(name)
    if not isinstance(value, str) or not value.strip() or len(value) > max_length:
        raise ValueError(f"'{name}' deve ser texto com ate {max_length} caracteres.")
    return value.strip()


def required_int(args: dict[str, Any], name: str, minimum: int = 1, maximum: int = 10**9) -> int:
    value = args.get(name)
    if isinstance(value, bool) or not isinstance(value, int) or not minimum <= value <= maximum:
        raise ValueError(f"'{name}' deve ser um inteiro entre {minimum} e {maximum}.")
    return value
