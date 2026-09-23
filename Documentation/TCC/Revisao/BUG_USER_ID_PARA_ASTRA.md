# Bug: identidade de usuário inconsistente entre escrita e leitura

Encontrado em 20/09/2026 por teste de interface (Chrome + backend real + frontend Angular real,
banco temporário). Nenhum teste automatizado detecta este defeito.

## Sintoma principal

Registrar uma venda pelo **chat** e depois abrir a aba **Histórico**: a operação não aparece, e o
painel de DARF mostra "Valor a pagar R$ 0,00 — Sem IR a recolher neste mês". A venda **está** gravada
no banco, com o IR correto.

Para um assistente tributário isso é grave porque falha em silêncio: o usuário vê o imposto calculado
na tela do chat e, ao conferir o DARF do mês, lê que não há nada a recolher.

## Sintoma secundário (mesma causa)

Comprar por um caminho e vender pelo outro **não encontra o custo médio**. `get_average_price` é
filtrado por `user_id`, então uma compra registrada pelo formulário é invisível para uma venda feita
pelo chat. O usuário recebe "O custo médio de aquisição de X não está disponível" mesmo tendo
registrado a compra.

## Causa

Três identidades diferentes convivem no mesmo app:

| Caminho | Arquivo | Envia `user_id`? | Grava/lê sob |
|---|---|---|---|
| Chat | `frontend/src/app/components/chat/chat.component.ts:26,84` | Sim, `'user123'` fixo no corpo | `user123` |
| Formulário | `frontend/src/app/services/api.service.ts:35-40` (`processTrade`) | **Não** | `default` |
| Histórico | `frontend/src/app/services/api.service.ts:55-58` | **Não** | `default` |
| Resumo mensal | `frontend/src/app/services/api.service.ts:67-74` | **Não** | `default` |
| DARF | `frontend/src/app/services/api.service.ts:90-97` | **Não** | `default` |

`chat.component.ts:26` tem `userId: string = 'user123'; // TODO: Get from auth service`.
As rotas do backend usam `Query(default="default")`, então tudo que não envia o parâmetro cai em
`default`.

## Reprodução

```
# 1. subir backend e frontend
# 2. no chat: "Comprei 50 cotas do HGLG11 a 100 reais hoje"
# 3. no chat: "Vendi as 50 cotas do HGLG11 a 110 reais hoje"   -> mostra IR R$ 99,63
# 4. aba Histórico -> setembro/2026 -> Carregar                -> "Nenhuma operação encontrada"
```

Confirmação direta pela API, mesmo mês e ano:

```
/api/trades/history?user_id=default&month=9&year=2026  -> []
/api/trades/history?user_id=user123&month=9&year=2026  -> 1 operação, ir_devido = 99.63
```

## Correção sugerida

Uma única fonte de verdade para a identidade, usada por **todos** os caminhos. O menor passo correto:

1. Mover a identidade para o `ApiService` (ou um `UserContextService` injetado nele), removendo o
   valor fixo de `chat.component.ts`.
2. Anexar `user_id` em **todas** as chamadas: como query param em `processTrade`, `getHistory`,
   `getSummary`, `getDarfInfo` (e qualquer outra rota que aceite o parâmetro), e no corpo do chat.
3. Manter o `TODO` de autenticação, mas em um lugar só.

Alternativa igualmente aceitável: remover a identidade do frontend e deixar todas as rotas usarem o
default do backend. O que **não** pode continuar é cada caminho escolhendo a sua.

## Critérios de aceitação

1. Venda pelo chat aparece no Histórico e no DARF do mês correspondente.
2. Venda pelo formulário continua aparecendo.
3. Compra pelo formulário + venda pelo chat encontram o mesmo custo médio, e vice-versa.
4. Um teste automatizado cobrindo escrita por um caminho e leitura por outro com a mesma identidade —
   hoje esse cruzamento não é coberto, que é o motivo de a suíte estar verde com o defeito presente.

## Observação

Isto reforça o que já consta na monografia: `user_id` não é autenticação. Hoje ele sequer é aplicado
de forma consistente entre os caminhos do próprio app. Vale conferir se o texto da monografia afirma
algo sobre histórico/DARF que dependa deste comportamento.
