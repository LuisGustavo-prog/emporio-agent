"""Configurar o logging da aplicacao (formato e nivel).

Pode importar de: config
Nao deve importar de: qualquer outra camada
Fase de implementacao: F0
"""

import logging


def configure_logging(level: str = "INFO") -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
