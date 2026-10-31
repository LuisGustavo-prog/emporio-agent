from emporio_agent.config import Settings


def test_settings_defaults(monkeypatch):
    monkeypatch.delenv("GROQ_MODEL", raising=False)
    monkeypatch.delenv("REFERENCE_DATE", raising=False)
    s = Settings.load()
    assert s.groq_model == "openai/gpt-oss-120b"
    assert s.max_tool_rounds == 5
    assert s.reference_date is None
