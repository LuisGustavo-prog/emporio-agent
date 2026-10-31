"""Caso de uso de consulta ao manual de politicas via RAG.

Pode importar de: rag
Nao deve importar de: tools, agent, cli
Fase de implementacao: F5
"""

from emporio_agent.config import POLICY_PDF
from emporio_agent.rag.retriever import load_policy_chunks, retrieve

_CACHED_CHUNKS = None


def search_policy(query: str, topic: str | None = None, limit: int = 4) -> list[dict]:
    global _CACHED_CHUNKS
    if _CACHED_CHUNKS is None:
        _CACHED_CHUNKS = load_policy_chunks(POLICY_PDF)
    search = f"{topic} {query}" if topic else query
    return [{"text": chunk.text, "page": chunk.page, "section": chunk.section}
            for chunk in retrieve(search, _CACHED_CHUNKS, limit)]
