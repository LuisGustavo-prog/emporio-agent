"""Wrapper do cliente Groq: chamada de chat com tools, retry com backoff e tratamento de erros do provedor. Unico modulo que conhece o SDK.

Pode importar de: config
Nao deve importar de: db, services, tools, cli
Fase de implementacao: F6
"""

import random
import time

from emporio_agent.config import Settings


class LLMClient:
    def __init__(self, settings: Settings):
        self.settings = settings
        try:
            from groq import Groq
        except ImportError as exc:
            raise RuntimeError("Instale as dependencias do projeto com pip install -e .") from exc
        self.client = Groq(api_key=settings.require_api_key())

    def chat(self, messages: list[dict], tools: list[dict] | None = None):
        last_error = None
        for attempt in range(3):
            try:
                return self.client.chat.completions.create(
                    model=self.settings.groq_model,
                    messages=messages,
                    tools=tools or None,
                    temperature=self.settings.llm_temperature,
                )
            except Exception as exc:
                last_error = exc
                status_code = getattr(exc, "status_code", None)
                if status_code is not None and status_code < 500 and status_code != 429:
                    break
                if attempt == 2:
                    break
                time.sleep((2 ** attempt) + random.random() * 0.25)
        raise RuntimeError("Nao foi possivel obter resposta do provedor LLM.") from last_error
