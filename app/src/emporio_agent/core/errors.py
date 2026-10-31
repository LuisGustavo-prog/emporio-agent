"""Excecoes do negocio.

Responsabilidade: erros tipados que as tools traduzem em respostas seguras
para o LLM, sem vazar detalhes internos.

Pode importar de: biblioteca padrao.
Nao deve importar de: nenhum outro modulo do projeto.
Fase de implementacao: F0 (pronto)
"""


class EmporioError(Exception):
    """Erro base do projeto."""


class NotFoundError(EmporioError):
    """Registro nao encontrado."""


class IdentityVerificationError(EmporioError):
    """E-mail ou telefone informado nao confere com o dono do pedido."""


class InvalidInputError(EmporioError):
    """Argumentos invalidos recebidos de uma tool."""
