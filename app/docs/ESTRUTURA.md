# Estrutura do projeto e divisão de responsabilidades

Este documento define onde cada coisa mora e quem pode depender de quem.

## Regra de dependência

As setas indicam quem pode importar quem. Nunca o contrário.

```
cli
 |
agent      (persona, loop de tool calling, memória, cliente Groq)
 |
tools      (contrato com o LLM: schema, validação, chamada ao service)
 |
services   (casos de uso: juntam core, db e rag)
 |
+-------+--------+
|       |        |
db     rag     core
 |               ^
 +--(usa)--------+
```

- `core` não depende de nada do projeto. É o miolo.
- `db` e `rag` dependem só de `core` (e de `config`).
- `services` junta `core`, `db` e `rag`.
- `config` não depende de ninguém.

## Responsabilidade de cada pasta

| Pasta | Responsabilidade | Não faz |
|---|---|---|
| `config.py` | Lê o ambiente e expõe Settings | Lógica de negócio |
| `core/` | O miolo do negócio: modelos, enums, erros, constantes da loja e regras (`core/rules/`) | Acessar banco, rede ou relógio. Tudo entra por argumento |
| `db/` | Tudo do banco: conexão, schema, carga dos CSVs, validação e consultas SQL parametrizadas | Regra de negócio, formatação de resposta |
| `rag/` | Dividir o manual em trechos e recuperar os relevantes | Decidir qual regra aplicar |
| `services/` | Casos de uso: juntam `core`, `db` e `rag` | Conhecer o LLM, o schema das tools ou a interface |
| `tools/` | Contrato com o LLM: schema, validação de argumentos, chamada ao service, erros seguros | SQL e regra de negócio |
| `agent/` | Persona do Tom, loop de tool calling, memória e cliente Groq | SQL e regra de negócio |
| `cli.py` | Entrada e saída com o usuário | Qualquer lógica além de chamar o agente |

## Princípios

1. **O LLM decide, o código executa.** O LLM só pede uma tool. Quem consulta o banco e calcula é o código Python.
2. **Regras puras.** Tudo em `core/rules/` é testável sem banco e sem rede. A data atual entra como argumento.
3. **Números da loja em um lugar só.** Descontos, prazos, frete e parcelas ficam em `core/constants.py`.
4. **Tools finas.** Uma tool valida, delega para um service e devolve JSON com campos prontos e avisos explícitos.
5. **Um único ponto por dependência externa.** Groq só em `agent/llm_client.py`, SQLite só em `db/connection.py`, ambiente só em `config.py`.
6. **Segurança no código, não no prompt.** A verificação de identidade acontece em `services/orders.py`.

## Mapa das tools

| Tool | Arquivo da tool | Service | Regras usadas | Acesso a dados |
|---|---|---|---|---|
| buscar_produtos | `tools/catalog.py` | `services/catalog.py` | pricing, stock | `db/products.py` |
| obter_produto | `tools/catalog.py` | `services/catalog.py`, `services/payments.py` | pricing, stock, payments | `db/products.py` |
| simular_pagamento | `tools/payments.py` | `services/payments.py` | pricing, payments | nenhum |
| consultar_pedido | `tools/orders.py` | `services/orders.py` | order_status | `db/orders.py` |
| avaliar_devolucao | `tools/returns.py` | `services/returns.py` | returns | `db/orders.py` |
| consultar_politica | `tools/policies.py` | `services/policies.py` | nenhuma | `rag/` |
| horario_atual_loja | `tools/store.py` | `services/store.py` | hours | nenhum |
| registrar_reclamacao | `tools/complaints.py` | `services/complaints.py` | nenhuma | `db/complaints.py` |
| simular_frete | `tools/shipping.py` | `services/shipping.py` | shipping | `db/products.py` |

## Árvore de arquivos

```
emporio-agent/
  README.md
  pyproject.toml
  .env.example
  .gitignore
  data/raw/                  CSVs e PDF originais (nomes simplificados)
  docs/                      ESTRUTURA.md e ai-workflow.md
  examples/conversas/        conversas de exemplo (F9)
  src/emporio_agent/
    config.py
    log.py
    cli.py
    core/
      models.py  enums.py  errors.py  constants.py
      rules/     pricing, payments, shipping, returns, hours, stock, order_status
    db/
      connection.py  schema.sql  loader.py  validators.py
      products.py  orders.py  conversations.py  complaints.py
    rag/
      chunker.py  retriever.py
    services/
      catalog  payments  orders  returns  policies  store  complaints
    tools/
      base.py  registry.py  catalog  payments  orders  returns  policies  store  complaints
    agent/
      prompts.py  llm_client.py  orchestrator.py  memory.py
  tests/
    unit/  integration/  evaluation/
```

## Convenções

- Commits pequenos no padrão `feat:`, `fix:`, `test:`, `docs:`, `chore:`.
- Cada arquivo começa com um docstring que diz a responsabilidade, o que pode importar e o que não deve importar.
- Nomes de arquivos e pastas sem acentos.
- Cada fase do plano (F0 a F10) corresponde a um ou mais commits.
