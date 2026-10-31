"""Indexar os trechos (BM25) e devolver os mais relevantes para uma pergunta.

Pode importar de: rag.chunker
Nao deve importar de: db, services, tools, agent, cli
Fase de implementacao: F5
"""

import re
from pathlib import Path

from emporio_agent.core.models import PolicyChunk
from emporio_agent.rag.chunker import chunk_text

TOKEN_RE = re.compile(r"[\wÀ-ÿ]+", re.UNICODE)


def load_policy_chunks(path: Path) -> list[PolicyChunk]:
    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise RuntimeError("Instale as dependencias do projeto para ler o manual PDF.") from exc
    reader = PdfReader(str(path))
    pages = [(index + 1, page.extract_text() or "") for index, page in enumerate(reader.pages)]
    return chunk_text(pages)


def retrieve(query: str, chunks: list[PolicyChunk], limit: int = 4) -> list[PolicyChunk]:
    """Busca lexical com IDF para manter a recuperacao sem estado e reproduzivel."""
    if limit < 1:
        return []
    query_terms = {term.casefold() for term in TOKEN_RE.findall(query)}
    if not query_terms:
        return []
    tokenized = [[term.casefold() for term in TOKEN_RE.findall(chunk.text)] for chunk in chunks]
    document_frequency = {term: sum(term in terms for terms in tokenized) for term in query_terms}
    total = max(len(chunks), 1)
    average_length = sum(len(terms) for terms in tokenized) / total if chunks else 1
    scored = []
    for index, terms in enumerate(tokenized):
        counts = {term: terms.count(term) for term in query_terms}
        length_factor = 1 - 0.75 + 0.75 * len(terms) / max(average_length, 1)
        score = sum(
            ((total - document_frequency[term] + 0.5) / (document_frequency[term] + 0.5))
            * (counts[term] * 2.5 / (counts[term] + 1.5 * length_factor))
            for term in query_terms if counts[term]
        )
        if score:
            scored.append((score, index))
    scored.sort(key=lambda pair: (-pair[0], pair[1]))
    return [chunks[index] for _, index in scored[:limit]]
