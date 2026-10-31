"""Configuracao da aplicacao.

Responsabilidade: ler variaveis de ambiente (.env) e expor um objeto Settings
imutavel. E o unico modulo que le o ambiente.

Pode importar de: biblioteca padrao e python-dotenv.
Nao deve importar de: nenhum outro modulo do projeto.
Fase de implementacao: F0 (pronto)
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import date
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:  # allows local database utilities before optional app dependencies are installed
    def load_dotenv(path: Path) -> None:
        if not path.is_file():
            return
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip("\"'"))

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
SAMPLE_DATA_DIR = PROJECT_ROOT / "data" / "sample"
POLICY_PDF = RAW_DATA_DIR / "politicas_da_loja.pdf"


@dataclass(frozen=True)
class Settings:
    groq_api_key: str
    groq_model: str
    llm_temperature: float
    max_tool_rounds: int
    history_window: int
    db_path: Path
    reference_date: date | None
    log_level: str

    @classmethod
    def load(cls) -> "Settings":
        load_dotenv(PROJECT_ROOT / ".env")
        ref = os.getenv("REFERENCE_DATE", "").strip()
        db_path = Path(os.getenv("DB_PATH", "data/processed/emporio.db"))
        if not db_path.is_absolute():
            db_path = PROJECT_ROOT / db_path
        try:
            temperature = float(os.getenv("LLM_TEMPERATURE", "0.2"))
            max_tool_rounds = int(os.getenv("MAX_TOOL_ROUNDS", "5"))
            history_window = int(os.getenv("HISTORY_WINDOW", "20"))
            reference_date = date.fromisoformat(ref) if ref else None
        except ValueError as exc:
            raise ValueError("Configuracao invalida: verifique LLM_TEMPERATURE, MAX_TOOL_ROUNDS, HISTORY_WINDOW e REFERENCE_DATE.") from exc
        if not 0 <= temperature <= 2 or max_tool_rounds < 1 or history_window < 2:
            raise ValueError("Temperatura deve estar entre 0 e 2; rodadas >= 1; historico >= 2.")
        return cls(
            groq_api_key=os.getenv("GROQ_API_KEY", "").strip(),
            groq_model=os.getenv("GROQ_MODEL", "openai/gpt-oss-120b").strip(),
            llm_temperature=temperature,
            max_tool_rounds=max_tool_rounds,
            history_window=history_window,
            db_path=db_path,
            reference_date=reference_date,
            log_level=os.getenv("LOG_LEVEL", "INFO").strip().upper(),
        )

    def require_api_key(self) -> str:
        if not self.groq_api_key:
            raise RuntimeError("GROQ_API_KEY nao definida. Preencha o arquivo .env.")
        return self.groq_api_key
