# LEIA-ME — Entrega Final (revisão de 2026-09-13)

## O que está nesta pasta

- `Monografia_Revisada_para_Orientador.docx` — Word principal, sem comentários do Word, pronto para leitura do orientador. **54 páginas** (contagem real, ver `evidencias/document_structure_audit.json`). Inclui, na Seção 7.4, as 5 capturas de tela reais da interface como Figuras 5–9 (não ficaram só como arquivos soltos).
- `Monografia_Revisada_para_Orientador.pdf` — PDF correspondente, gerado a partir do docx acima via automação real do Microsoft Word (COM) e conferido página a página.
- `matriz_comentarios.csv` — os 124 comentários do orientador, cada um com status **Atendido / Parcial / Alternativa por solicitação do autor / Descrição corrigida conforme código / Pendente** e uma observação específica (não é mais um único status genérico repetido).
- `Reproducao_TCC_2026.zip` — código (baseline e revised), scripts do experimento, resultados brutos (benchmark, respostas, julgamentos, custos) e o próprio `manuscrito.md`, para reprodução integral.
- `evidencias/` — ver abaixo.

## O que foi feito nesta sessão (além do que já existia)

1. **Migração completa dos testes legados.** A suíte do código `revised` tinha 23 falhas após as mudanças de contrato (campos agora obrigatórios: `total_vendas_mes`, `preco_medio_informado`, `custos_operacao`, `irrf_informado`, `prazo_dias`, `classificacao`). Cada um dos 23 casos foi inspecionado individualmente — não apenas "consertado para passar" — e reescrito para exercitar o contrato atual. Um teste (`test_swing_trade_without_exemption`) na verdade validava o **próprio defeito antigo** (isenção nunca aplicada); a expectativa foi corrigida, não afrouxada. Resultado: **88/88 testes aprovados** (ver `evidencias/testes_e_calculadoras/`, com o "antes" e o "depois" preservados).

2. **Dois defeitos reais encontrados e corrigidos no código `revised`** (não no projeto original, que foi preservado):
   - `BDRCalculator` duplicava a lógica de `AcoesCalculator` mas não tinha recebido a mesma correção: preço médio nulo virava ganho zero silencioso, e a isenção de R$20.000 nunca era aplicada — apesar do próprio código dizer "regras idênticas às ações".
   - `FuturosCalculator` passou a **exigir** `custos_operacao` do usuário, mas nunca usava esse valor no cálculo — continuava estimando taxas B3 antigas. Corrigido para usar o custo real informado, como o próprio campo promete ("substitui estimativa de tarifas").
   - Ambos os defeitos **invalidavam silenciosamente** os números já publicados na Tabela 4 da monografia (verificação de 12 cenários). Após a correção, os números batem exatamente com o que já estava escrito (12/12), então a Tabela 4 continua válida — mas isso só foi confirmado nesta sessão, não presumido.

3. **Duas informações desatualizadas corrigidas nos textos que alimentam o RAG** (`revised/backend/data/regulations/`):
   - Empréstimo de ações citava só a Lei 13.043/2014; a **Lei nº 15.265/2025** (21/11/2025) trata especificamente da tributação do empréstimo de valores mobiliários no país e é a base legal mais direta — já estava corretamente citada na monografia, mas não no código/regulamento. Adicionada.
   - FIIs: o texto dizia "pelo menos 50 cotistas" para isenção de rendimento; a Lei 14.754/2023 elevou esse mínimo para **100 cotistas**. Corrigido.
   - Também corrigido um texto de empréstimo de ações que ainda descrevia o comportamento antigo ("assume a faixa mais conservadora quando o prazo não é informado"), quando o código já foi alterado para recusar o cálculo nesse caso — o assistente estaria descrevendo um comportamento que não é mais o seu.

4. **Execução real da aplicação** com dados sintéticos, contra um servidor FastAPI genuinamente em execução (não apenas testes unitários), em banco de dados isolado: isenção mensal de ações (dentro e fora do limite), criptoativo nacional (dentro e fora do limite de R$35.000), futuros WIN e WDO (multiplicadores conferidos: R$0,20/ponto e R$10,00/ponto), remuneração do doador em empréstimo de ações, e venda de FII. Ver `evidencias/execucao_real/`.

4b. **Capturas de tela reais da interface Angular** (via Chrome, ativado pelo usuário no meio da sessão — inicialmente indisponível). Ver `evidencias/screenshots_interface_real/`. Isso revelou um **gap real de integração, não presumido**: o formulário estruturado (`Formulário`) não foi atualizado com os campos que o backend revisado agora exige:
   - **Funciona de ponta a ponta pela interface**: FII (compra + venda, `01`/`02`) e empréstimo de ações/doador (`05`/`06`) — nenhum dos dois exige `total_vendas_mes`, e o campo de prazo do contrato já existe no formulário. Opção deveria funcionar pelo mesmo motivo (não exige `total_vendas_mes`), desde que haja uma compra prévia registrada pela própria interface — não testado nesta sessão.
   - **Falha pela interface, com a mensagem real do backend** (não é bug meu, é o formulário desatualizado): ações (`04`) e futuro de índice/WIN (`03`) — mesmo registrando uma compra antes, o formulário não tem campo para `total_vendas_mes` (ações) nem para `custos_operacao`/`irrf_informado` (futuros), então a venda recusa com "Informe o custo médio ou registre a aquisição antes da venda." (ações, por faltar o total do mês) ou equivalente. BDR e cripto teriam a mesma falha (mesmas checagens no backend, `total_vendas_mes` obrigatório).
   - **Chat em linguagem natural** (`07`): 1 pergunta real ("Vendi FII por R$5 mil com lucro. A isenção de 20 mil serve?"), autorizada explicitamente pelo usuário nesta sessão porque envolve 1 chamada paga à API (Haiku para classificar a intenção + Sonnet para responder — da ordem de centavos). A resposta distinguiu corretamente FII de ações, citando a alíquota de 20% e a ausência de isenção de R$20 mil para FIIs.
   - Esse gap (formulário desatualizado para ações/futuros/cripto) não estava documentado antes e é uma limitação real da versão revisada — adicionei como pendência abaixo.
   - **As 5 capturas foram incorporadas ao corpo da monografia** (Seção 7.4, Figuras 5–9, com legenda e fonte indicando sessão real de 2026-09-13), não apenas guardadas como arquivos soltos. O texto da seção também foi atualizado para explicar o achado do gap de integração. Isso levou o documento de 51 para **54 páginas**.

5. **Verificação tributária contra fontes oficiais** (não apenas confiança no texto já escrito): multiplicadores WIN/WDO, tabela progressiva de ganho de capital "por faixa" (marginal, não sobre o total), isenção de R$35.000 para cripto nacional, regime do exterior (Lei 14.754/2023), mínimo de cotistas de FII, e a lei específica do empréstimo de ações (15.265/2025). Fontes citadas nas buscas ficaram registradas na conversa desta sessão.

6. **Renderização e verificação visual real.** O ambiente não tinha LibreOffice/pandoc, mas o **Microsoft Word estava disponível via automação COM**. O documento foi renderizado duas vezes (antes e depois de incorporar as 5 capturas de tela): sumário atualizado, paginação recalculada (51 páginas → **54 páginas** após as novas figuras, contagem real) e exportação para PDF. Quinze páginas representativas (capa, folha de rosto, início de capítulos, as 9 figuras — incluindo as 5 novas — fim das referências, fim dos dois apêndices) foram inspecionadas visualmente: nenhuma tabela cortada, nenhuma imagem ilegível, nenhum título órfão, nenhum marcador `[[FIG:]]`/`[[TABLE:]]`/`[[SCREENSHOTS]]` esquecido.

7. **Correção pontual pedida pelo orientador**: "São Paulo / 2026" na capa e folha de rosto agora está centralizado (comentário 1).

8. **Texto da monografia atualizado** para refletir o item 1 e 2 acima (Seções 6.5, 7.3, 8.2, 8.3 e Apêndice B) — os números publicados sobre a suíte de testes estavam desatualizados (diziam "23 falhas, migração não concluída") e agora refletem o estado real (88/88 aprovados).

9. **Introdução reescrita com contexto real e referências que faltavam** (a pedido do usuário, que notou que a reestruturação anterior havia esvaziado bastante o Capítulo 1). Mantive a estrutura atual (1.1/1.2/1.3) em vez de reverter para a estrutura original — o conteúdo de LLM/RAG que estava na introdução original foi propositalmente movido para o Capítulo 2 na reestruturação, o que já atendia ao pedido geral do orientador de reduzir fragmentação. Dentro dessa estrutura:
   - **Seção 1.1**: adicionado parágrafo com número real e verificável — 5,4 milhões de investidores pessoa física em renda variável e R$588,3 bilhões investidos no 2º trimestre de 2025, fonte primária B3 (2025), atendendo ao comentário 9 (que pedia números de mercado).
   - **Seção 1.2**: objetivos específicos reescritos como lista a)-e) em linhas separadas (comentário 18, que pedia isso explicitamente e não tinha sido aplicado).
   - **Seção 1.3**: frase de organização dos capítulos reescrita em voz passiva ("Nos capítulos seguintes são apresentados...") seguindo o exemplo literal dado pelo comentário 19.
   - **Seção 2.1** (onde o conteúdo de LLM hoje vive, após a reestruturação): adicionadas as referências **Brown et al. (2020)** — treinamento em bilhões de documentos — e **Bender et al. (2021)** — risco de alucinação/desatualização, que já existia no documento original e havia se perdido na reestruturação. Isso atende aos comentários 10 e 11, que pediam exatamente essas referências.
   - Todas as fontes novas são verificáveis e foram adicionadas às Referências do documento (agora 23, eram 20).
   - Matriz de comentários atualizada: 100 atendidos (eram 98), 18 parciais (eram 19), 1 pendente (era 2) — restou só o comentário 111 (extração assistida de documentos como trabalho futuro).

## Pendências reais (não resolvidas nesta sessão — favor não apresentar como concluídas)

- **Formulário estruturado desatualizado**: para ações, BDR, futuros (WIN/WDO) e cripto, a interface Angular não tem campos para `preco_medio_informado`, `total_vendas_mes`, `custos_operacao`, `irrf_informado`, `classificacao` nem `exchange_estrangeira` — descoberto ao testar de verdade pela interface (ver item 4b e `evidencias/screenshots_interface_real/03` e `/04`). Confirmadamente funcionam pela interface hoje: FII e empréstimo de ações. Isso não estava documentado antes desta sessão.
- **1 comentário do orientador ainda pendente** (marcado "Pendente" na matriz): id 111 (extração assistida de documentos como trabalho futuro — não está nem no corpo nem em Trabalhos Futuros).
- **18 comentários parcialmente atendidos** — cada um com observação específica na matriz (ex.: parágrafo de "sistemas comparáveis" no Capítulo 4, diagrama específico do fluxo de RAG, seção dedicada ao frontend Angular).
- **Validação por especialista tributário e pelo orientador**: nada nesta revisão substitui isso. O documento é explícito sobre não ser apuração fiscal completa.
- **Gabaritos do benchmark**: continuam assistidos por IA, sem homologação de especialista — declarado no próprio documento (Apêndice A/B) e nos resultados registrados anteriormente (`results_summary.json`).
- **Live-project separado**: durante esta mesma sessão, antes desta tarefa começar, uma funcionalidade de criptomoedas foi adicionada ao projeto em `D:\Projects\BrazilianFinancialAssistant` (fora da pasta `tcc_revisao`). Essa calculadora usa uma alíquota única por faixa (não marginal/"por parcela"), diferente da versão em `revised/` usada nesta monografia, que já implementa a regra correta (marginal). Isso não foi corrigido no projeto original nesta sessão — fica como pendência separada, fora do escopo desta entrega.

## Não fiz

- Não sobrescrevi nem apaguei `original_comentado.docx`, a pasta `baseline/` ou qualquer artefato do projeto original em `D:\Projects\BrazilianFinancialAssistant`.
- Não fiz novas chamadas pagas ao benchmark, julgamento ou geração de respostas em massa. Fiz **1 chamada nova**, explicitamente autorizada pelo usuário nesta sessão, para capturar a resposta real do chat sobre FII (item 4b) — ordem de centavos, fora do escopo do `api_ledger.jsonl` de ~US$ 4,89 já registrado (que não foi alterado).
- Não apresento este documento como "pronto para a banca" — as pendências acima são reais e devem ser resolvidas antes da defesa.
