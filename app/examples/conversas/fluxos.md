# Fluxos de exemplo

Use estes fluxos para demonstracao manual. Os dados de pedido sao ficticios e nao devem ser usados para inferir informacoes reais.

## Catalogo

Cliente: Voces tem violao de nylon?

Esperado: chamar `buscar_produtos`, informar produtos encontrados, preco e disponibilidade.

## Pagamento

Cliente: Quanto fica R$ 900 em 6 vezes no cartao?

Esperado: chamar `simular_pagamento` com total, forma `credit` e 6 parcelas; informar parcela e total sem inventar condicoes.

## Pedido

Cliente: Quero acompanhar o pedido 1.

Esperado: pedir e-mail ou telefone do titular antes de chamar `consultar_pedido`; nunca consultar cliente pelo e-mail.

## Politica

Cliente: Qual o prazo para devolver uma compra?

Esperado: consultar `consultar_politica` e apoiar a resposta nos trechos encontrados, citando a pagina.

## Reclamacao

Cliente: Quero reclamar que meu produto chegou danificado.

Esperado: coletar nome, contato e descricao; registrar pela tool e confirmar somente depois de receber o protocolo.
