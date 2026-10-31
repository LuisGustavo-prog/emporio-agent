"""Extrair o texto do PDF de politicas e dividir por secao e subsecao, guardando metadados de origem.

Pode importar de: config
Nao deve importar de: db, services, tools, agent, cli
Fase de implementacao: F5
"""

import re

from emporio_agent.core.models import PolicyChunk

HEADING_RE = re.compile(r"(?<!\w)(\d+(?:\.\d+)*)\.\s+([A-ZÀ-Ü][^.!?]{2,100})")


def chunk_text(pages: list[tuple[int, str]], max_words: int = 180, overlap: int = 30) -> list[PolicyChunk]:
    if max_words < 1 or overlap < 0 or overlap >= max_words:
        raise ValueError("Tamanho e sobreposicao dos trechos invalidos.")
    chunks: list[PolicyChunk] = []
    for page, content in pages:
        normalized = " ".join(content.split())
        matches = list(HEADING_RE.finditer(normalized))
        sections: list[tuple[str, str]] = []
        if matches:
            if matches[0].start() > 0:
                sections.append((f"Página {page}", normalized[:matches[0].start()].strip()))
            for index, match in enumerate(matches):
                end = matches[index + 1].start() if index + 1 < len(matches) else len(normalized)
                title = " ".join(match.group(2).split())[:80]
                sections.append((f"Seção {match.group(1)} — {title}", normalized[match.start():end].strip()))
        else:
            sections.append((f"Página {page}", normalized))
        for section, text in sections:
            words = text.split()
            start = 0
            while start < len(words):
                end = min(start + max_words, len(words))
                chunks.append(PolicyChunk(" ".join(words[start:end]), page, section))
                if end == len(words):
                    break
                start = end - overlap
    return chunks
