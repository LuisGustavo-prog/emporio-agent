# Emporio da Musica — Tom Support Agent

A Brazilian Portuguese customer support agent for product catalog, orders, payments, returns, store policies, and complaint registration. The LLM interprets customer requests; application code handles operational data and business rules.

## Requirements

- Python 3.11 or newer
- A Groq API key to chat with the agent

## Installation

From the repository root, create and activate a virtual environment, install the project, and copy the environment template.

### PowerShell

```powershell
Set-Location app
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -e .
Copy-Item .env.example .env
```

### Command Prompt (CMD)

```bat
cd /d app
py -3.11 -m venv .venv
call .venv\Scripts\activate.bat
python -m pip install -e .
copy .env.example .env
```

Edit `.env` and set `GROQ_API_KEY`. You can also configure the model, SQLite database path, and reference date there; see `.env.example`.

## Run the agent

Run these commands from the `app` directory.

```powershell
# Validate the CSV files and load or update SQLite
python -m emporio_agent.db.loader

# Start a support session
emporio-agent

# Or load the data when starting the agent
emporio-agent --load-data
```

The SQLite database is created automatically at `data/processed/emporio.db` when the agent starts. If it has no products, the agent loads CSV files from `data/raw` on first startup. The loader reports known inconsistencies and preserves recorded order totals. Type `sair` to end a chat session.

The original customer and order files (`customers.csv`, `orders.csv`, and `order_items.csv`) and the store's internal policy manual (`politicas_da_loja.pdf`) are excluded from Git. When the original customer and order files are absent, the loader uses the synthetic records in `data/sample`, which allow order-related demonstrations without publishing the original records. Local files in `data/raw` take precedence. To enable answers grounded in the policy manual, place a local copy at `data/raw/politicas_da_loja.pdf`.

The CLI displays a session ID at startup. Resume a conversation with `emporio-agent --session-id <id>`.

## Project structure

- `app/src/emporio_agent/core/`: models, constants, and pure business rules.
- `app/src/emporio_agent/db/`: SQLite schema, loading, validation, and parameterized queries.
- `app/src/emporio_agent/rag/`: PDF extraction, chunking, and lexical retrieval for store policies.
- `app/src/emporio_agent/services/`: application use cases.
- `app/src/emporio_agent/tools/`: tool schemas, validation, and dispatch.
- `app/src/emporio_agent/agent/`: system prompt, Groq client, persistent memory, and orchestration.
- `app/tests/`: unit tests and manual evaluation scenarios in `evaluation/cases.jsonl`.

See [`app/docs/ESTRUTURA.md`](app/docs/ESTRUTURA.md) for layer dependencies and the tool map.

## Technical decisions

- **Agent approach:** Python with Groq function calling and no agent framework. This keeps the call flow explicit and lets the application validate arguments and run business rules in code.
- **Model and provider:** `openai/gpt-oss-120b` via Groq, configurable with `GROQ_MODEL`. The API requires `GROQ_API_KEY`; provider limits and pricing depend on the account and may change.
- **Operational data:** SQLite stores the catalog, orders, and conversation history. Parameterized SQL and Python services keep the database as the source of truth for prices, stock, orders, and calculations.
- **Policy retrieval (RAG):** the PDF is split into chunks and searched lexically with IDF weighting. No embeddings or external vector service are used. Retrieved results include page or section context, but lexical search may miss relevant passages when wording differs significantly.
- **Prompt and tools:** the prompt defines the persona, scope, and response guidance. Tools perform lookups and validation. Identity checks and sensitive calculations are enforced by code rather than relying on prompt instructions alone.
- **Interface:** a CLI keeps the implementation focused on the text agent described in the challenge. A web interface or messaging channel could be added later.

## Known assumptions and limitations

- The manual offers free delivery **above** R$ 500 in the metropolitan area. In Campo Grande, orders of R$ 500 or less cost R$ 35 to deliver. Other cities require a checkout quote based on postal code, weight, and dimensions. Large instruments may need a special quote.
- For deliveries outside the metropolitan area, the manual estimates 5–12 business days for PAC, 2–5 for SEDEX, and 3–8 for Jadlog. The agent does not invent shipping prices.
- Store hours are Monday through Friday, 9:00–18:00; Saturday, 9:00–13:00; closed on Sundays and holidays. The calendar covers national and state holidays; municipal holidays may vary.
- The default model was checked on 2026-10-31. Model availability and provider pricing can change.
- The manual lists two phone numbers in different sections: (67) 3341-4444 for the store and (67) 3321-4500 for WhatsApp. One section accents the email address; the project uses `contato@emporiodamusica.com.br`.
- The catalog CSV contains 65 products, while the manual describes more than 300 instruments. If a product is not in the available data, the agent says it cannot find it in the system.
- Some recorded order totals differ from the sum of their items. The agent always reports the recorded `total_brl`. The source data also contains a repeated customer email, so identity is checked against the owner of the specified order.
- The actual receipt date is not stored separately. For delivered orders, `estimated_delivery` is used as an approximation unless the customer provides the actual date.
- The catalog does not record every return eligibility condition, such as packaging, signs of use, final-sale status, custom adjustments, or mouthpieces. The tool explains the known requirements and refers exceptions to a human attendant.
- Local holidays, postal-code prices, and special quotes for large instruments require confirmation by a person or at checkout.

### What I would improve with more time

- Expand integration tests and agent evaluations with representative conversations, including provider limits and API errors.
- Add a web interface or messaging integration while keeping the CLI for development.
- Evaluate policy retrieval quality and consider semantic search if results justify it.
- Add operational observability and handling for temporary API limits without exposing personal data in logs.

## Development

Run these commands from the `app` directory:

```powershell
python -m pip install -e ".[dev]"
pytest
ruff check src tests
```

## Security and data handling

- Order lookups verify the supplied contact against the owner of that order. Email addresses are never used to search for a customer.
- The Groq API key is read from the environment and must not be committed.
- SQL queries are parameterized; tools accept only defined arguments and return controlled errors.
- Data loading is transactional and can be repeated. It does not recalculate recorded order totals.

## Use of AI coding assistants

OpenAI Codex was used to review the project materials, implement and refine the agent in layers, analyze conversations, and document decisions. Suggestions were reviewed and adjusted during development; business rules and sensitive calculations remain implemented in application code. The detailed activity log is in [`app/docs/ai-workflow.md`](app/docs/ai-workflow.md).
