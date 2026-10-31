# Registro de uso de IA

Preencha ao longo do projeto. Alimenta a seção de uso de assistentes de IA do README.

| Data | Ferramenta | O que foi pedido | O que foi aceito ou corrigido |
|---|---|---|---|
| 2026-10-31 | Codex | Implementar o agente completo a partir da estrutura, do manual de políticas e dos dados locais | Implementacao em camadas; preservar totais divergentes, validar titular pelo pedido, manter regras puras e documentar as suposicoes do documento de projeto. |
| 2026-10-31 | Codex | Analisar conversas reais do agente e corrigir a busca de produtos | A consulta por "violao" nao encontrava a categoria cadastrada como "Violões". Foi aceita a normalizacao de acentos e singular/plural na busca, com teste unitario cobrindo o caso. O prompt tambem foi ajustado para evitar saudacoes repetidas e informacoes nao solicitadas. |
| 2026-10-31 | Codex | Criar `requirements.txt` e reforcar o `.gitignore` | O arquivo de dependencias foi alinhado ao `pyproject.toml`, incluindo ferramentas de desenvolvimento. O `.gitignore` passou a excluir ambientes, arquivos locais de segredo, chaves, bancos, logs e backups, mantendo `.env.example`. |
| 2026-10-31 | Codex | Preparar o projeto para publicacao sem os dados originais de clientes e pedidos | Os CSVs locais de clientes, pedidos e itens foram excluidos do Git. Foram incluidos registros sinteticos em `data/sample` e um fallback no carregador para manter a demonstracao executavel sem expor os dados fornecidos localmente. |
