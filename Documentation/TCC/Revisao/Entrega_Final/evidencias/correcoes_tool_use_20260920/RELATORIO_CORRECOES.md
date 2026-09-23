# Correções após validação independente — 20/09/2026

## Alterações

1. `tool_chat.py`: preserva o erro de validação retornado por ferramenta quando o modelo encerra sem cálculo válido. O wrapper recupera recursivamente mensagens de `ValueError` em grupos de exceções; falhas de transporte continuam com mensagem genérica. Uma venda recusada não é persistida.
2. `fiis.py` e `opcoes.py`: imposto calculado sobre `max(0, ganho_bruto - custos)`, arredondado para centavos. Com ganho bruto de R$ 100 e custos informados de R$ 22, FII resulta em R$ 15,60 e opções swing em R$ 11,70, em vez de R$ 20 e R$ 15. Custos superiores ao ganho produzem imposto zero.
3. `criptomoedas.py`: removido o ramo inalcançável de tributação no exterior e ajustada sua documentação. A recusa explícita de operações estrangeiras permanece; não se implementou apuração anual.
4. FII e opções também rejeitam custo médio ausente, zero, negativo ou não finito quando chamadas diretamente. O custo explicitamente informado tem prioridade. Corrigidos comentários que diziam haver isenção de R$ 20 mil em opções.

Fonte da dedução de despesas efetivamente pagas: Receita Federal, [Deduções](https://www.gov.br/receitafederal/pt-br/assuntos/meu-imposto-de-renda/pagamento/renda-variavel/bolsa-de-valores-1/deducoes), consulta em 20/09/2026. Custos de aquisição devem integrar o custo médio; o campo de custos desta operação é deduzido na venda. Estimativas legadas continuam sendo estimativas, não tarifas oficiais atualizadas.

## Verificação

- Suíte completa: **142 passed, 2 warnings, 15.25s**, conforme `pytest.txt`.
- Acréscimo de 22 casos sobre a suíte anterior de 120; verificações com servidor MCP real e respostas programadas de LLM, inclusive preservação da mensagem específica até a resposta do agente e ausência de chamada de gravação da venda.
- Ambiente Python já instalado, banco temporário, chave de API vazia. Sem chamadas pagas, novo benchmark com modelos reais ou nova captura do navegador.
- Avisos: depreciações de Starlette/httpx e configuração Pydantic. Aprovação não equivale a auditoria tributária independente nem certifica instalação limpa.
- Testes antigos de FII e opções foram ajustados para esperar imposto sobre a base líquida; o teste de resposta incompatível agora exige a mensagem específica em vez da genérica.

## Documentação e preservação

Relatórios, capturas e resultados históricos não foram sobrescritos. A monografia Word estava bloqueada por outro processo na verificação desta rodada. Word, PDF, modelo e manuscrito não foram alterados, para evitar perda de alterações não salvas ou divergência entre fontes. Sincronização documental pendente após fechar o Word. Nenhum commit realizado.
