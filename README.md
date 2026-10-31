# Emporio da Musica — agente Tom

Agente de atendimento em portugues brasileiro com consulta ao catalogo, pedidos, pagamentos, devolucoes, politicas da loja e registro de reclamacoes. O LLM interpreta o pedido; dados e regras de negocio sao executados pelo codigo.

## Requisitos

- Python 3.11 ou superior
- Chave de API da Groq para conversar com o agente

## Instalacao

Execute os comandos de instalacao a partir da raiz do repositorio:

```powershell
Set-Location app
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -e .
Copy-Item .env.example .env
```

Edite `.env` e preencha `GROQ_API_KEY`. A configuracao permite selecionar modelo, banco SQLite e data de referencia; veja `.env.example`.

## Uso

Execute os comandos a seguir a partir da pasta `app`.

```powershell
# Validar os CSVs e carregar/atualizar o SQLite
python -m emporio_agent.db.loader

# Iniciar o atendimento
emporio-agent

# Ou carregar os dados com o comando principal
emporio-agent --load-data
```

O banco SQLite e criado automaticamente em `data/processed/emporio.db` ao iniciar o agente, se ainda nao existir. Se o banco nao tiver produtos, o agente tambem carrega os CSVs de `data/raw` automaticamente na primeira inicializacao. Para recarregar os dados manualmente, use `emporio-agent --load-data` ou `python -m emporio_agent.db.loader`. O comando de carga mostra avisos para inconsistencias conhecidas, preservando o valor original do pedido. Para encerrar o chat, digite `sair`.

Os arquivos originais de clientes e pedidos (`customers.csv`, `orders.csv` e `order_items.csv`) e o manual interno (`politicas_da_loja.pdf`) nao sao versionados. Se os CSVs de clientes e pedidos nao estiverem em `data/raw`, a carga usa os registros ficticios de `data/sample`, incluidos para permitir testar pedidos sem publicar os dados originais. Os arquivos locais em `data/raw` tem precedencia.

Ao iniciar, a CLI exibe o identificador da sessao. Para retomar o historico, use `emporio-agent --session-id <id>`.

## Estrutura

- `core/`: modelos, constantes e regras puras.
- `db/`: SQLite, carga, validacao e consultas parametrizadas.
- `rag/`: extracao, segmentacao e recuperacao lexical do PDF de politicas.
- `services/`: casos de uso.
- `tools/`: schemas, validacao e despacho para o agente.
- `agent/`: prompt, cliente Groq, memoria persistente e orquestracao.
- `tests/`: testes automatizados em `unit/`; `evaluation/cases.jsonl` registra cenarios manuais de avaliacao, e `integration/` fica reservado para evolucao.

As dependencias permitidas entre camadas e o mapa de ferramentas estao em [`app/docs/ESTRUTURA.md`](app/docs/ESTRUTURA.md).

## Decisoes tecnicas

- **Abordagem do agente:** Python proprio com function calling da API Groq, sem framework de agentes. Isso mantem o fluxo de chamadas explicito e permite validar argumentos e executar regras de negocio no codigo.
- **Modelo e provedor:** `openai/gpt-oss-120b` via Groq, configuravel por `GROQ_MODEL`. A escolha permite testar um modelo de chat com suporte a ferramentas; a API requer `GROQ_API_KEY` e seus limites/precos dependem da conta.
- **Dados operacionais:** SQLite para catalogo, pedidos e historico de conversa. Consultas SQL parametrizadas e servicos Python mantem os dados como fonte de verdade para preco, estoque, pedidos e calculos.
- **Politicas (RAG):** o PDF e dividido em trechos e recuperado por busca lexical com ponderacao IDF, sem embeddings ou servico vetorial externo. A abordagem e simples de executar localmente e devolve pagina/secao para fundamentar respostas; pode perder relevancia em perguntas com vocabulario distante do manual.
- **Prompt e ferramentas:** o prompt define persona, escopo e regras de atendimento; tools fazem consultas e validacoes. O prompt orienta o modelo, mas validacoes de identidade e calculos sensiveis ficam no codigo.
- **Interface:** CLI para manter a entrega focada no agente de mensagens de texto, como permitido pelo enunciado. Uma interface web ou integracao com canal de mensagens seria um proximo passo.

## Decisoes e limitacoes conhecidas

- O manual diz frete gratis **acima** de R$ 500 na regiao metropolitana. Em Campo Grande, abaixo ou igual a esse valor, o frete e R$ 35; para outras cidades o valor depende de CEP, peso e dimensoes e deve ser calculado no checkout. Itens grandes podem exigir cotacao especial.
- Para envio fora da regiao metropolitana, as modalidades e prazos estimados sao PAC (5–12 dias uteis), SEDEX (2–5) e Jadlog (3–8). O agente nao inventa o valor do frete.
- Horarios: segunda a sexta, 9h–18h; sabado, 9h–13h; domingos e feriados, fechado. O calendario cobre feriados nacionais e estaduais; feriados municipais podem variar.
- O modelo padrao e `openai/gpt-oss-120b`, consultado em 31/10/2026. Precos e disponibilidade do provedor podem mudar.
- O manual lista dois telefones em secoes diferentes: (67) 3341-4444 para telefone da loja e (67) 3321-4500 para WhatsApp. O e-mail com acento aparece em uma secao; adota-se `contato@emporiodamusica.com.br`.
- O CSV tem 65 produtos, embora o manual diga mais de 300 instrumentos. Se nao encontrar um item, o agente diz que ele nao consta no sistema.
- Pedidos 3 e 20 têm total diferente da soma dos itens. O total exibido e sempre o campo `total_brl` original. Clientes 11 e 43 compartilham e-mail; identidade e verificada contra o titular do pedido informado.
- O recebimento nao esta registrado separadamente. Para arrependimento em pedidos entregues, `estimated_delivery` e usado como aproximacao, salvo se a pessoa informar a data real.
- O catalogo nao registra todas as condicoes de elegibilidade (embalagem, sinais de uso, venda final, personalizacao ou boquilhas). A ferramenta lista os requisitos e encaminha excecoes a atendente humano.
- Feriados locais, valores de CEP e cotacoes de instrumentos grandes exigem confirmacao humana ou do checkout.

### Proximos passos com mais tempo

- Ampliar testes de integracao e avaliacao com conversas representativas, incluindo limites e erros do provedor LLM.
- Criar uma interface web ou integrar o agente a um canal de mensagens, mantendo a CLI como ferramenta de desenvolvimento.
- Melhorar a recuperacao de politicas com avaliacao de relevancia e, se os resultados justificarem, busca semantica.
- Adicionar observabilidade e tratamento operacional para limites temporarios da API, sem expor dados pessoais nos logs.

## Desenvolvimento

Execute estes comandos a partir da raiz do repositorio.

```powershell
Set-Location app
python -m pip install -e ".[dev]"
pytest
ruff check src tests
```

## Seguranca e dados

- A consulta de pedidos valida o contato diretamente contra o titular do pedido. E-mails nunca sao usados para localizar um cliente.
- A chave Groq e lida do ambiente e nao deve ser commitada.
- O SQL e parametrizado; tools aceitam apenas argumentos definidos e retornam erros controlados.
- A carga e transacional e pode ser repetida. Ela nao recalcula o total de pedidos.

## Uso de assistentes de IA

O registro de uso e decisoes esta em [`app/docs/ai-workflow.md`](app/docs/ai-workflow.md).
