<!-- Fonte editorial única. Preserve IDs; capas, tabelas e figuras são mantidas no modelo. -->

<!-- p:2 -->
UNIVERSIDADE DE SÃO PAULO

<!-- p:3 -->
Instituto de Ciências Matemáticas e de Computação

<!-- p:51 -->
USP - São Carlos

<!-- p:52 -->
2026

<!-- p:54 -->
ANDRE KHENAIFES

<!-- p:60 -->
ASSISTENTE INTELIGENTE PARA APOIO EM TRIBUTAÇÃO E REGULAÇÃO NO MERCADO FINANCEIRO BRASILEIRO

<!-- p:65 -->
Trabalho de conclusão de curso apresentado ao Departamento de Ciências de Computação do Instituto de Ciências Matemáticas e de Computação da Universidade de São Paulo — ICMC/USP, como parte dos requisitos para obtenção do título de Especialista em Inteligência Artificial e Big Data.

<!-- p:66 -->
Orientador: Rafael Rossi

<!-- p:73 -->
USP – São Carlos

<!-- p:74 -->
2026

<!-- p:76 -->
# RESUMO

<!-- p:77 -->
KHENAIFES, Andre. Assistente inteligente para apoio em tributação e regulação no mercado financeiro brasileiro. 2026. Monografia (Especialização em Inteligência Artificial e Big Data) — Instituto de Ciências Matemáticas e de Computação, Universidade de São Paulo, São Carlos, 2026.

<!-- p:78 -->
O mercado financeiro brasileiro é regulado por normas tributárias e prudenciais extensas, atualizadas com frequência e distribuídas entre diferentes órgãos. Essa característica impõe custos de busca, interpretação e conferência a investidores e profissionais. Este trabalho apresenta o projeto e a implementação de um assistente inteligente para apoio à tributação e à regulação no mercado financeiro brasileiro. A solução combina Geração Aumentada por Recuperação (Retrieval-Augmented Generation — RAG), calculadoras determinísticas e modelos de linguagem para interpretação e explicação em língua portuguesa. O protótipo proposto consiste em uma interface web e um servidor web que possui uma base de dados vetorial e um agente que faz as orquestrações necessárias para atender às solicitações dos usuários. A versão implementada abrange ações, BDRs, fundos imobiliários, opções, contratos futuros de dólar e índice, a remuneração do doador em empréstimo de ações e aspectos da tributação de criptoativos. O estudo adota pesquisa aplicada, de natureza tecnológica, com avaliação baseada em casos de uso, comparação de respostas e verificação de cálculos contra regras explicitadas. Como resultado, é apresentado um protótipo modular e rastreável, que integra recuperação de fontes, cálculos reproduzíveis e explicações conversacionais. A avaliação demonstrou melhora na correção das respostas com a revisão do contexto documental e atendimento aos resultados esperados nos cenários numéricos examinados. Esses resultados indicam que o protótipo atingiu os objetivos de integração e apoio à consulta no conjunto avaliado.

<!-- p:79 -->
Palavras-chave: inteligência artificial; geração aumentada por recuperação; tributação; mercado financeiro; assistente conversacional.

<!-- p:80 -->
# ABSTRACT

<!-- p:81 -->
KHENAIFES, Andre. Intelligent assistant to support taxation and regulation in the Brazilian financial market. 2026. Monografia (Especialização em Inteligência Artificial e Big Data) — Instituto de Ciências Matemáticas e de Computação, Universidade de São Paulo, São Carlos, 2026.

<!-- p:82 -->
The Brazilian financial market is governed by extensive tax and prudential regulations that are frequently updated and published by different authorities. This creates information search, interpretation and verification costs for investors and professionals. This work presents the design and implementation of an intelligent assistant to support taxation and regulation in the Brazilian financial market. The solution combines Retrieval-Augmented Generation (RAG), deterministic calculators and language models for interpretation and explanation in Portuguese. The proposed prototype consists of a web interface and a web server with a vector database and an agent that performs the orchestration required to respond to user requests. The implemented version covers stocks, Brazilian Depositary Receipts, real estate investment funds, options, dollar and index futures, securities-lending income for lenders, and aspects of cryptoasset taxation. The study adopts applied technological research, with an evaluation based on use cases, response comparisons and verification of calculations against explicit rules. The result is a modular, traceable prototype that integrates source retrieval, reproducible calculations and conversational explanations. The evaluation demonstrated improved response correctness following revision of the documentary context and agreement with expected results in the numerical scenarios examined. These results indicate that the prototype met its integration and query-support objectives within the evaluated set.

<!-- p:83 -->
Keywords: artificial intelligence; retrieval-augmented generation; taxation; financial market; conversational assistant.

<!-- p:84 -->
# SUMÁRIO

<!-- p:136 -->
# 1 INTRODUÇÃO

<!-- p:137 -->
O mercado financeiro brasileiro apresenta um ambiente informacionalmente exigente. A interpretação de operações de renda variável envolve regras de imposto de renda, modalidades operacionais, custos de negociação, compensação de prejuízos, documentos de suporte e prazos de recolhimento. Somam-se a isso normas e comunicados de órgãos como Receita Federal do Brasil, Comissão de Valores Mobiliários e Banco Central do Brasil, além das especificações operacionais e dos materiais publicados pela B3. A busca manual por informações em fontes dispersas aumenta o tempo de resposta e favorece erros de interpretação. A compreensão desse ambiente é apoiada pelas publicações educacionais da Comissão de Valores Mobiliários, especialmente pelos materiais da Série TOP sobre o mercado de valores mobiliários e derivativos (COMISSÃO DE VALORES MOBILIÁRIOS, 2024, 2025).

<!-- p:138 -->
A dimensão desse ambiente pode ser observada nos dados da B3. No segundo trimestre de 2025, havia 5,4 milhões de investidores pessoa física em renda variável, com R$ 588,3 bilhões em custódia. Esse valor representa o patrimônio custodiado, e não o volume negociado no período. O levantamento registra investimentos em diferentes produtos, entre eles ações, fundos imobiliários, BDRs e ETFs (B3, 2025). O presente trabalho concentra-se no atendimento informacional a pessoas físicas, sem estender automaticamente suas regras a pessoas jurídicas.

<!-- p:139 -->
A atuação institucional também ajuda a dimensionar o mercado. Em levantamento relativo a janeiro a dezembro de 2025, a B3 informou mais de R$ 997,4 bilhões movimentados por investidores institucionais em ações à vista e mais de R$ 1,7 trilhão negociado por fundos de investimento no conjunto do mercado à vista (B3, 2026e). Os recortes não são equivalentes ao patrimônio das pessoas físicas: diferem em período, categoria de investidor e produtos. Por isso, esses valores não são somados nem utilizados como uma comparação direta entre pessoas físicas e jurídicas.

<!-- p:140 -->
A diversidade de ativos exige distinguir condições de incidência, modalidades operacionais e tratamentos tributários. A consulta sobre uma venda de ações não pode ser respondida pela simples aplicação de uma regra destinada a fundos imobiliários, assim como a remuneração do doador em empréstimo de ações não equivale ao ganho obtido na venda do ativo. Essas particularidades são reunidas no capítulo dedicado ao domínio financeiro e tributário brasileiro, incluindo derivativos e aspectos dos criptoativos.

<!-- p:141 -->
Além disso, ao buscar essas informações, pode-se deparar com explicações advindas de diferentes fontes, bem como comunicados, artigos e leis extensos e muitas vezes difíceis de interpretar.

<!-- p:142 -->
Entretanto, com o advento dos grandes modelos de linguagem (Large Language Models — LLMs), ampliaram-se as possibilidades de geração de conteúdo e de resposta a perguntas em linguagem natural (BROWN et al., 2020).

<!-- p:143 -->
Esses modelos geralmente são treinados com grandes volumes de texto e são utilizados para gerar conteúdo novo ou responder a perguntas (BROWN et al., 2020). Entretanto, apesar da grande capacidade de geração de conteúdo e de resposta, as LLMs podem alucinar, isto é, gerar conteúdo ou respostas incorretas ou sem sustentação factual. A geração se baseia em padrões estatísticos aprendidos durante o treinamento e não garante a verificação dos fatos apresentados (BENDER et al., 2021). Além disso, o aprendizado utiliza dados disponíveis até determinado período, enquanto as informações podem ter sido atualizadas posteriormente (LEWIS et al., 2020). A desatualização e a alucinação são problemas relacionados, mas distintos: uma resposta também pode estar errada sobre fatos anteriores ao treinamento.

<!-- p:144 -->
A Geração Aumentada por Recuperação (Retrieval-Augmented Generation — RAG) busca minimizar esse problema ao recuperar trechos de uma base de conhecimento antes da geração, permitindo que a resposta seja condicionada por evidências externas (LEWIS et al., 2020). Quando a base é mantida atualizada, esse mecanismo permite disponibilizar informações posteriores ao treinamento do modelo. Neste trabalho, a recuperação de fontes é combinada com calculadoras determinísticas, separando a elaboração da explicação textual da execução dos cálculos.

<!-- p:145 -->
## 1.1 Problema de pesquisa

<!-- p:146 -->
Como conceber um assistente conversacional que apoie consultas tributárias e regulatórias do mercado financeiro brasileiro, oferecendo respostas contextualizadas, cálculos reproduzíveis e mecanismos de rastreabilidade?

<!-- p:147 -->
## 1.2 Objetivos

<!-- p:148 -->
O objetivo geral é desenvolver e avaliar um assistente inteligente baseado em RAG para apoiar a interpretação de regras tributárias e regulatórias aplicáveis a operações do mercado financeiro brasileiro. Para alcançar esse objetivo, são definidos os seguintes objetivos específicos:

<!-- p:149 -->
a) estruturar uma arquitetura integrada de interface web, servidor, base vetorial e ferramentas de cálculo;

<!-- p:150 -->
b) implementar e verificar cálculos para as classes de ativos contempladas pelo protótipo;

<!-- p:151 -->
c) recuperar contexto documental para fundamentar as respostas e permitir a identificação das fontes utilizadas;

<!-- p:152 -->
d) disponibilizar ferramentas de consulta e validação por meio de MCP, distinguindo sua implementação da integração efetivamente demonstrada no fluxo conversacional;

<!-- p:153 -->
e) avaliar a recuperação, as respostas e os cálculos por meio de casos de uso e critérios explícitos, comparando configurações de contexto documental e modelos de linguagem.

<!-- p:154 -->
## 1.3 Justificativa

<!-- p:155 -->
A proposta é relevante porque aproxima tecnologias de inteligência artificial de uma necessidade concreta de investidores e profissionais: transformar informações dispersas em apoio estruturado para consulta e cálculo. A combinação de componentes probabilísticos, como os modelos de linguagem, com componentes determinísticos, como as calculadoras, reduz a dependência de geração livre para valores numéricos. A rastreabilidade permite examinar as fontes e os resultados produzidos, contribuindo para a conferência das respostas no contexto financeiro.

<!-- p:156 -->
A avaliação do protótipo complementa essa contribuição ao examinar separadamente a recuperação documental, a correção das respostas e os resultados numéricos. Dessa forma, o trabalho não se restringe à apresentação da arquitetura, mas também materializa seu funcionamento por meio de registros experimentais e demonstrações da aplicação.

<!-- p:157 -->
## 1.4 Organização do trabalho

<!-- p:158 -->
No Capítulo 2 são apresentados os fundamentos de modelos de linguagem, representações vetoriais, RAG, MCP e avaliação assistida por modelos. No Capítulo 3 são reunidos o domínio financeiro e tributário brasileiro, o papel da B3 e as particularidades dos ativos contemplados. No Capítulo 4 são discutidos os trabalhos relacionados. No Capítulo 5 são consolidadas a arquitetura e a implementação da solução. No Capítulo 6 é descrita a metodologia de avaliação. No Capítulo 7 são apresentados os resultados objetivos e a demonstração documentada do protótipo. No Capítulo 8 são sintetizadas as conclusões, as limitações e as propostas de trabalhos futuros.

<!-- p:159 -->
# 2 FUNDAMENTAÇÃO TEÓRICA

<!-- p:160 -->
Neste capítulo é apresentado o referencial teórico sobre os conceitos utilizados para o desenvolvimento deste trabalho de conclusão de curso, a saber: grandes modelos de linguagem (LLMs), Geração Aumentada por Recuperação (RAG), embeddings e busca vetorial, Model Context Protocol (MCP) e ferramentas (tools), além da avaliação assistida por modelos de linguagem. As particularidades do domínio de aplicação deste trabalho são apresentadas no Capítulo 3.

<!-- p:161 -->
## 2.1 Modelos de linguagem

<!-- p:162 -->
Modelos de linguagem representam regularidades de sequências textuais e podem ser utilizados para completar textos, gerar conteúdo e responder a perguntas. No pré-treinamento, seus parâmetros são ajustados a partir de grandes corpora; em modelos autorregressivos, uma tarefa central é prever o próximo token, unidade de processamento que pode corresponder a uma palavra ou a parte dela. O GPT-3, descrito por Brown et al. (2020), exemplifica a ampliação dessa abordagem para tarefas apresentadas por instruções e exemplos no próprio contexto.

<!-- p:163 -->
O Transformer, apresentado por Vaswani et al. (2017), utiliza mecanismos de atenção para combinar informações de diferentes posições da sequência. Essa organização favorece o tratamento de relações contextuais e permite paralelizar parte do treinamento, diferentemente de uma dependência estritamente recorrente entre posições. Arquiteturas derivadas desse modelo fundamentam famílias amplamente utilizadas. A descrição conceitual não implica acesso à arquitetura interna ou aos dados completos de treinamento do serviço comercial empregado no protótipo.

<!-- p:164 -->
Após o pré-treinamento, podem ocorrer etapas de adaptação com exemplos de instruções e respostas ou preferências sobre saídas. Essas etapas modificam parâmetros e devem ser distinguidas da inferência: ao receber uma pergunta e documentos no prompt, o modelo utiliza o contexto para gerar uma resposta, sem que essa operação, por si só, represente treinamento. Neste projeto não foram realizados pré-treinamento nem ajuste fino; foram utilizadas chamadas a modelos existentes.

<!-- p:165 -->
Entre as famílias disponibilizadas como serviços estão GPT, Gemini e Claude, exemplificadas pelos trabalhos de Brown et al. (2020), Gemini Team (2023) e pela apresentação institucional da Anthropic (2024). Entre os modelos com pesos disponibilizados encontram-se Gemma, Llama 3, Mistral 7B e DeepSeek-V3 (GEMMA TEAM, 2024; GRATTAFIORI et al., 2024; JIANG et al., 2023; DEEPSEEK-AI, 2024). Esses exemplos contextualizam o campo; não constituem um ranking nem indicam que todos foram utilizados no experimento.

<!-- p:166 -->
Disponibilizar pesos não equivale a abrir código, dados de treinamento ou licença irrestrita. As condições variam por versão; por isso, evita-se classificar todas essas famílias como código aberto. Neste estudo, os geradores e o avaliador foram acessados pela API da Anthropic, com identificadores registrados.

<!-- p:167 -->
A geração de texto provável não garante correspondência factual. Denominam-se alucinações as afirmações produzidas sem sustentação ou em desacordo com fatos e evidências. Além disso, informações recentes ou internas de uma organização podem não estar representadas nos parâmetros do modelo. Esses problemas motivam a recuperação de documentos externos e a separação entre geração de explicações e execução de cálculos verificáveis (BENDER et al., 2021; LEWIS et al., 2020).

<!-- p:168 -->
## 2.2 Embeddings e busca vetorial

<!-- p:169 -->
Embeddings são representações vetoriais densas que codificam características aprendidas de palavras, sentenças ou documentos. Em comparação com representações esparsas associadas a um vocabulário amplo, permitem descrever textos em um espaço de dimensão fixa e geralmente menor. As propriedades capturadas dependem do modelo e do treinamento: proximidade vetorial pode refletir relações semânticas e sintáticas, mas não estabelece equivalência lógica nem correção de uma regra (DEVLIN et al., 2019; REIMERS; GUREVYCH, 2019).

<!-- p:170 -->
O BERT fornece representações contextuais de tokens; transformá-las em uma representação de sentença requer uma estratégia apropriada de agregação ou adaptação. Há também modelos voltados especificamente à representação de textos para recuperação, como EmbeddingGemma e text-embedding-3-small. Gemma, como família de modelos geradores, não deve ser confundida com a variante especializada EmbeddingGemma (DEVLIN et al., 2019; GOOGLE, 2025; OPENAI, 2024). Esses modelos são apresentados como alternativas conceituais, não como participantes do benchmark deste trabalho.

<!-- p:171 -->
A busca vetorial é útil quando a coincidência exata entre palavras da consulta e do documento não basta. O sistema representa a pergunta no mesmo espaço dos documentos, calcula uma medida de proximidade e seleciona os k vizinhos mais próximos. Por exemplo, uma consulta sobre remuneração de quem empresta ações pode necessitar de um trecho que emprega a expressão doador de ativos, mesmo sem repetir todos os termos da pergunta.

<!-- p:172 -->
A similaridade de cosseno entre vetores u e v é dada por cos(u,v) = (u·v)/(||u||·||v||). A ordenação por distância de cosseno utiliza a relação 1 − cos(u,v). Dois textos podem tratar do mesmo ativo e divergir em uma condição decisiva, como a existência de isenção. Assim, similaridade indica proximidade na representação, e não uma probabilidade de correção tributária.

<!-- p:173 -->
Uma busca exata compara a consulta com todos os vetores. Conforme cresce a coleção, esse custo pode motivar algoritmos de busca aproximada de vizinhos mais próximos (Approximate Nearest Neighbors — ANN). Esses métodos procuram candidatos de forma eficiente, admitindo a possibilidade de não recuperar exatamente os mesmos vizinhos da busca exaustiva. Trata-se de um compromisso entre custo e qualidade da recuperação, que deve ser medido no contexto de uso.

<!-- p:174 -->
O Hierarchical Navigable Small World (HNSW) organiza os vetores em um grafo com múltiplos níveis. A navegação começa em níveis mais esparsos e prossegue em níveis mais detalhados até selecionar candidatos próximos à consulta. O algoritmo é uma alternativa amplamente utilizada para ANN, sem que isso implique ser o melhor método para qualquer corpus (MALKOV; YASHUNIN, 2016). A configuração concreta do ChromaDB e do modelo de embeddings desta aplicação é apresentada na Seção 5.5.

<!-- p:175 -->
## 2.3 Geração aumentada por recuperação

<!-- p:176 -->
A Geração Aumentada por Recuperação (Retrieval-Augmented Generation — RAG) associa recuperação de informação e geração textual. Documentos relevantes são selecionados de uma base externa e fornecidos como contexto para a resposta. Essa estratégia permite incorporar informações específicas do domínio ou posteriores ao treinamento sem exigir que o usuário copie manualmente os documentos a cada consulta (LEWIS et al., 2020).

<!-- p:177 -->
Na preparação da base, os documentos são selecionados e organizados em trechos, processo conhecido como segmentação ou chunking. Os trechos recebem identificadores e metadados, são representados por embeddings e armazenados em um índice. Durante a consulta, a pergunta também é representada; o recuperador seleciona os trechos e o gerador recebe pergunta, instruções e contexto. A Figura 1 apresenta esse fluxo conceitual, distinguindo indexação e atendimento.

<!-- p:178 -->
Figura 1 – Fluxo conceitual de indexação e consulta em RAG

<!-- p:180 -->
Fonte: elaboração própria com base em Lewis et al. (2020). Fluxo conceitual; a configuração implementada é detalhada na Seção 5.5.

<!-- p:181 -->
A segmentação deve preservar informação suficiente para interpretar condições e exceções. Um trecho longo pode reunir tópicos distintos; um fragmento excessivamente curto pode separar a regra de sua condição de aplicação. O tamanho e a sobreposição podem ser definidos por critérios automáticos ou editoriais. No protótipo, a curadoria por unidades de regra é descrita na Seção 5.5, sem atribuir ao código uma segmentação automática que não foi implementada.

<!-- p:182 -->
Contexto pertinente pode reduzir respostas sem fundamento, mas simplesmente acrescentar mais texto não garante melhora. Liu et al. (2023) observaram sensibilidade à posição das informações em contextos longos, e Asai et al. (2023) discutem problemas da incorporação indiscriminada de trechos. Portanto, seleção, qualidade e organização das evidências importam tanto quanto sua quantidade. A atualização documental também não altera automaticamente as regras executáveis de uma calculadora.

<!-- p:183 -->
## 2.4 Funções, serviços REST e MCP

<!-- p:184 -->
Uma função executa código com argumentos definidos; uma rota HTTP disponibiliza comportamento por um serviço. O Model Context Protocol (MCP) padroniza a comunicação de aplicações de IA com servidores de capacidades. Executar cálculos não torna automaticamente uma função ou rota uma ferramenta MCP (MODEL CONTEXT PROTOCOL, 2025a).

<!-- p:185 -->
O protocolo distingue ferramentas, recursos e prompts. Ferramentas são operações invocáveis, descritas por nome e esquema de entrada; recursos disponibilizam conteúdo para leitura; prompts oferecem modelos reutilizáveis de interação. Essa distinção permite separar execução, acesso a dados e organização de instruções (MODEL CONTEXT PROTOCOL, 2025a, 2025b, 2025c).

<!-- p:186 -->
Uma ferramenta pode consultar um banco, recuperar documentos, acessar um serviço externo ou executar uma função numérica. Ao delegar o cálculo a código determinístico, a aplicação evita depender apenas da geração textual para produzir valores. Ainda é necessário validar argumentos, regras e permissões. Operações com efeitos externos exigem controles adicionais: a capacidade de invocar uma ferramenta não equivale à autorização para executar qualquer ação (MODEL CONTEXT PROTOCOL, 2025a).

<!-- p:187 -->
Na versão inicial, as calculadoras eram chamadas diretamente pelo backend. A revisão de 16 de setembro de 2026 introduziu um servidor MCP de execução para reutilizá-las mediante chamadas de ferramentas. A distinção entre função de cálculo e protocolo de acesso continua válida; o caminho implementado e os limites da verificação são detalhados na Seção 5.8.

<!-- p:188 -->
## 2.5 Avaliação por modelos de linguagem

<!-- p:189 -->
LLM-as-a-Judge utiliza um modelo para atribuir notas ou comparar respostas segundo uma rubrica. Zheng et al. (2023) discutem essa abordagem e seus limites, incluindo vieses relacionados à posição e à apresentação das respostas. Uma avaliação automática pode ampliar a quantidade de exemplos examinados, mas não deve ser apresentada como validação independente de especialista.

<!-- p:190 -->
A rubrica deve explicitar o que será julgado e como cada nota será atribuída. Repetir o julgamento ajuda a examinar sua estabilidade, mas não substitui a verificação da validade dos critérios e das evidências (ZHENG et al., 2023).

<!-- p:191 -->
# 3 DOMÍNIO FINANCEIRO E TRIBUTÁRIO BRASILEIRO

<!-- p:192 -->
Neste capítulo são apresentadas as particularidades do domínio financeiro e tributário brasileiro, com destaque para o papel da B3, os fatos geradores associados a cada classe de ativo e as fontes utilizadas para sua compreensão. As descrições da implementação e da avaliação são concentradas nos capítulos seguintes.

<!-- p:193 -->
## 3.1 Organização do domínio e papel da B3

<!-- p:194 -->
Os conteúdos relativos à B3 são reunidos neste capítulo porque descrevem o domínio ao qual o sistema é aplicado. A B3 fornece infraestrutura de negociação, registro, compensação e liquidação em diferentes mercados. No empréstimo de ativos, seu papel de contraparte central integra o funcionamento operacional do serviço. Esse papel não deve ser confundido com a competência para instituir o imposto de renda (B3, 2026a).

<!-- p:195 -->
No sistema, convém separar três classes de informação: especificações de produto, regras tributárias e custos de intermediação. Especificações explicam, por exemplo, quanto vale um ponto de determinado contrato. Regras tributárias estabelecem incidência, base e condições. Custos dependem do serviço, da operação e dos documentos da instituição intermediadora. A confusão entre essas classes é uma fonte concreta de erros de implementação.

<!-- p:196 -->
O capítulo inclui criptoativos em seção própria. Sua inclusão não significa que operações em exchanges ou carteiras digitais sejam operações em bolsa ou estejam submetidas às mesmas tarifas. O agrupamento é temático: domínio financeiro e tributário brasileiro, com distinções internas entre mercados e regimes.

<!-- p:197 -->
## 3.2 Ações e BDRs

<!-- p:198 -->
Para ações à vista em operações comuns de pessoa física, a regra de isenção depende do total mensal de alienações, e não do lucro ou de cada operação isolada. A orientação da Receita Federal delimita o benefício e suas exclusões. A consequência computacional é que o sistema não pode inferir o total nacional das vendas a partir de uma única mensagem ou somente do histórico de uma corretora (RECEITA FEDERAL, 2026a).

<!-- p:199 -->
Uma consulta que informa duas vendas de R$ 12 mil em corretoras distintas deve preservar a dimensão mensal. Considerar cada venda separadamente produziria uma classificação diferente daquela obtida com R$ 24 mil de alienações. Este exemplo ilustra uma propriedade geral dos dados de entrada: um campo numericamente válido pode ser semanticamente insuficiente.

<!-- p:200 -->
BDRs não se beneficiam da isenção de R$ 20 mil em vendas mensais aplicável às ações à vista. No recorte de ganhos na alienação em bolsa, as alíquotas são 15% nas operações comuns e 20% no day trade, observadas as regras de apuração e compensação. A regra é distinta daquela dos rendimentos distribuídos pelos certificados (B3, 2026b). Essa particularidade impede transportar automaticamente o tratamento tributário de ações para BDRs.

<!-- p:201 -->
## 3.3 Fundos imobiliários e ambiguidade da consulta

<!-- p:202 -->
O termo “imobiliário” pode indicar venda de imóvel, negociação de cotas de FII ou recebimento de rendimento distribuído pelo fundo. A desambiguação é parte da tarefa do assistente, não um detalhe de interface. Responder imediatamente com uma alíquota sem identificar o fato gerador pode ser um erro, mesmo quando o percentual é correto para uma das interpretações possíveis.

<!-- p:203 -->
Ganhos líquidos na venda de cotas de FII estão sujeitos à alíquota de 20%, sem transportar para essa venda a isenção mensal de ações. Rendimentos distribuídos por fundos a pessoas físicas podem, por sua vez, depender de condições legais específicas para a isenção, inclusive características do fundo e do cotista. A regra de um evento não deve ser utilizada como justificativa para o outro (RECEITA FEDERAL, 2026b; BRASIL, 2004).

<!-- p:204 -->
Por essa razão, o benchmark contém consultas de venda de cotas, de rendimentos e de ambiguidade. O teste não se limita à reprodução do percentual de 20%: procura verificar se a resposta identifica a categoria e evita uma generalização. A compensação de perdas também deve respeitar a espécie de operação e não pode ser tratada como abatimento irrestrito entre quaisquer investimentos.

<!-- p:205 -->
## 3.4 Opções e contratos futuros

<!-- p:206 -->
Em opções, negociação do prêmio, exercício e expiração são eventos diferentes. A posição de titular ou lançador modifica os fatos necessários à apuração. Por isso, a análise exige identificar o evento, a posição e os valores envolvidos, em vez de tratar toda opção como uma venda ordinária de ações (COMISSÃO DE VALORES MOBILIÁRIOS, 2025; RECEITA FEDERAL, 2015).

<!-- p:207 -->
Nos futuros, a especificação do contrato é indispensável para converter variação de cotação em reais. No minicontrato WIN, cada ponto corresponde a R$ 0,20 por contrato. No WDO, o tamanho de USD 10.000 e a cotação por USD 1.000 resultam em R$ 10 por ponto e contrato. Assim, uma posição comprada em um WIN com variação favorável de 500 pontos apresenta R$ 100 de ganho bruto; dois WDO com variação favorável de 10 pontos apresentam R$ 200 (B3, 2026c; B3, 2026d).

<!-- p:208 -->
Essas relações descrevem a conversão da variação de cotação em resultado bruto, mas não substituem a trajetória dos ajustes diários. Valor nocional, margem, ganho econômico e fluxo de caixa representam grandezas diferentes. A distinção é necessária à interpretação dos contratos e à identificação dos dados de apuração (COMISSÃO DE VALORES MOBILIÁRIOS, 2025).

<!-- p:209 -->
## 3.5 Empréstimo de ações

<!-- p:210 -->
No empréstimo de ativos, o proprietário empresta títulos com obrigação de devolução e recebe remuneração. O evento estudado é a renda do doador, e não uma venda ordinária de ações. A Lei nº 15.265/2025 remete a tributação dessa remuneração às regras de renda fixa e estabelece tratamento definitivo para o emprestador pessoa física residente. O prazo contratual, portanto, é dado necessário à identificação da faixa de retenção (BRASIL, 2025).

<!-- p:211 -->
Na tabela regressiva aplicável à remuneração examinada, os prazos de até 180 dias, de 181 a 360 dias, de 361 a 720 dias e acima de 720 dias correspondem, respectivamente, às alíquotas de 22,5%, 20%, 17,5% e 15%. Esses intervalos tornam o prazo um dado relevante para interpretar a retenção sobre a remuneração do doador (BRASIL, 2004, 2025).

<!-- p:212 -->
Reembolso de proventos, remuneração contratual e operações do tomador são eventos distintos. A descrição da renda do doador não deve ser utilizada como se representasse a apuração de uma venda a descoberto ou de todo o ciclo de empréstimo (B3, 2026a; BRASIL, 2025).

<!-- p:213 -->
## 3.6 Criptoativos no Brasil e operações no exterior

<!-- p:214 -->
No regime de ganho de capital aplicável às operações nacionais examinadas, a referência de pequeno valor é R$ 35 mil de alienações mensais, agregadas entre criptoativos. Não se trata do limite de R$ 20 mil de ações nem de um limite por moeda. A permuta entre criptoativos também requer análise como alienação, mesmo sem saque em reais (RECEITA FEDERAL, 2021).

<!-- p:215 -->
Quando tributável, a progressividade deve ser aplicada às parcelas de ganho das respectivas faixas. A Lei nº 13.259/2016 não autoriza aplicar a maior alíquota alcançada sobre todo o ganho. O caso sintético de R$ 6 milhões, sob as condições expressamente delimitadas no teste, resulta em R$ 750 mil sobre os primeiros R$ 5 milhões e R$ 175 mil sobre a parcela restante, totalizando R$ 925 mil (BRASIL, 2016).

<!-- p:216 -->
O enquadramento de aplicações financeiras no exterior pela Lei nº 14.754/2023 envolve apuração anual e não deve ser substituído mecanicamente pela regra mensal nacional. A mera indicação de autocustódia não determina, sozinha, o enquadramento de qualquer criptoativo. Nesta revisão, o motor mensal recusa calcular operações marcadas como exterior e solicita a análise apropriada; isso é uma delimitação de cobertura, não uma implementação completa do regime externo (BRASIL, 2023).

<!-- p:217 -->
# 4 TRABALHOS RELACIONADOS

<!-- p:218 -->
As referências a seguir são discutidas segundo sua contribuição para recuperação, representação e avaliação. A revisão é dirigida aos métodos empregados e não constitui levantamento sistemático de todas as soluções tributárias existentes. O posicionamento do protótipo é apresentado após a descrição dessas contribuições, antes da arquitetura implementada.

<!-- p:219 -->
## 4.1 Recuperação e geração

<!-- p:220 -->
Lewis et al. (2020) constituem a referência para a associação de recuperação externa e geração em tarefas intensivas em conhecimento. A relação com este trabalho está no princípio arquitetural, não na equivalência entre experimentos. A monografia utiliza corpus pequeno e curado em português, enquanto o estudo de referência aborda benchmarks de processamento de linguagem natural com outra escala e outro treinamento.

<!-- p:221 -->
Reimers e Gurevych (2019) contribuem para a fundamentação das representações de sentenças usadas em busca semântica. A utilidade desse método para encontrar textos relacionados não demonstra, por si, sua suficiência para distinguir condições legais muito próximas. A diferença é importante porque o erro tributário pode decorrer de uma única exceção ou negação em um trecho altamente semelhante à pergunta.

<!-- p:222 -->
Yao et al. (2023) propõem ReAct, que intercala raciocínio textual e ações sobre fontes externas. Em tarefas de perguntas e verificação de fatos, a abordagem consulta uma interface da Wikipédia; em ambientes interativos, escolhe ações a partir das observações recebidas. Os autores relatam ganhos absolutos de sucesso de 34 e 10 pontos percentuais sobre métodos de comparação em ALFWorld e WebShop, respectivamente. A aproximação com este trabalho está na combinação entre interpretação e operações externas; o protótipo tributário não reproduz o treinamento ou os ambientes de avaliação de ReAct.

<!-- p:223 -->
Asai et al. (2023) apresentam Self-RAG, no qual um modelo é treinado para decidir sobre recuperação e produzir sinais de reflexão sobre evidências e respostas. Os experimentos relatam melhorias em perguntas abertas, verificação de fatos e precisão de citações em relação aos modelos comparados no artigo. Diferentemente dessa abordagem, o assistente aqui estudado utiliza recuperação com quantidade de trechos definida e julgamento externo posterior. A comparação ajuda a identificar uma possível evolução, sem atribuir autorreflexão ou recuperação adaptativa à implementação atual.

<!-- p:224 -->
## 4.2 Avaliação automática

<!-- p:225 -->
Zheng et al. (2023) fundamentam a discussão sobre modelos avaliadores e seus vieses. A presente pesquisa emprega rubrica curta e fatos esperados, em vez de somente uma preferência geral entre duas respostas. Também registra justificativas e repete parte da avaliação. Entretanto, utiliza modelos de uma mesma família de fornecedor e não inclui painel de especialistas humanos, preservando uma limitação relevante em relação à validade externa dos julgamentos.

<!-- p:226 -->
## 4.3 Posicionamento do estudo

<!-- p:227 -->
A contribuição não é apresentar um novo algoritmo de recuperação ou um novo modelo de linguagem. Trata-se de um estudo aplicado sobre integração e avaliação de um assistente em domínio sensível. A unidade de análise inclui a fonte recuperada, o cálculo e a explicação. A mudança de corpus é examinada junto com a organização dos trechos, permitindo observar resultados de uma revisão de engenharia, mas não atribuir causalmente toda diferença a uma única técnica.

<!-- p:228 -->
# 5 ARQUITETURA E IMPLEMENTAÇÃO

<!-- p:229 -->
Neste capítulo são consolidados os módulos e seus fluxos, as interfaces HTTP, a recuperação documental e as alterações localizadas das calculadoras. A descrição distingue capacidades encontradas no repositório de integrações demonstradas pelo caminho de execução, evitando representar possibilidades de evolução como funcionalidades verificadas. A arquitetura apresentada incorpora a integração MCP posterior ao benchmark; os resultados históricos não são atribuídos a essa nova versão.

<!-- p:230 -->
## 5.1 Visão consolidada

<!-- p:231 -->
O código inspecionado organiza a solução em interface Angular, backend FastAPI, serviços de modelo de linguagem, calculadoras, persistência relacional e base vetorial. O usuário envia perguntas ou informações de operações. O backend coordena a interpretação e, conforme a intenção, chama um agente especializado ou trata a consulta geral. Os agentes são módulos especializados da aplicação; sua denominação não implica autonomia irrestrita ou cooperação independente entre processos.

<!-- p:232 -->
A separação entre interface, serviço e persistência permite evoluir responsabilidades de modo independente. Isso é uma propriedade da organização do código, não evidência de escalabilidade medida: não foi executado teste de carga distribuída. A Figura 2 sintetiza os módulos e as interações; as seções seguintes detalham suas responsabilidades.

<!-- p:233 -->
Na Figura 2 é apresentada a arquitetura após a integração MCP de 16 de setembro de 2026. O backend controla a sequência de chamadas: interpreta e valida a operação, consulta a política de custos e solicita o cálculo ao servidor MCP. O resultado estruturado retorna para persistência e explicação. Compras e perguntas sem operação não acionam a ferramenta de cálculo. O servidor legado de apoio ao desenvolvimento permanece separado e não integra esse caminho.

<!-- p:234 -->
Figura 2 – Arquitetura com execução de cálculos via MCP

<!-- p:236 -->
Fonte: elaboração própria a partir do código e dos registros experimentais (2026).

<!-- p:237 -->
## 5.2 Interface web

<!-- p:238 -->
A interface Angular organiza os componentes de entrada de operações, chat, apresentação de resultados e histórico. O componente de operação coleta os campos do formulário e encaminha um objeto estruturado; o chat envia a mensagem em linguagem natural. O serviço ApiService centraliza as chamadas HTTP para o prefixo /api, separando a apresentação dos dados da implementação das regras no servidor.

<!-- p:239 -->
No fluxo estruturado, processTrade envia os dados a POST /api/trades/process e recebe TaxCalculationResult. No fluxo conversacional, sendChat utiliza POST /api/chat/ e recebe ChatResponse, que pode conter resposta, agente identificado, operação extraída e resultado numérico. O navegador apresenta os valores devolvidos; as regras tributárias não são executadas no componente de visualização. Exemplos reais das telas e das mensagens são reunidos na Seção 7.4, para manter a demonstração junto aos resultados.

<!-- p:240 -->
A implementação pode ser localizada em frontend/src/app/components e no serviço services/api.service.ts. Como requisito de interação, o usuário precisa distinguir entrada, resultado e solicitação de informação adicional. A avaliação realizada documenta esses estados da interface, sem medir usabilidade ou satisfação de usuários.

<!-- p:241 -->
## 5.3 Backend e interfaces HTTP

<!-- p:242 -->
As rotas de chat recebem mensagens e devolvem resposta, identificação do agente e, quando existentes, operação extraída e resultado. As rotas de operações permitem registrar compras e processar vendas estruturadas. As rotas de cálculos oferecem histórico agregado e informações associadas ao recolhimento. A existência dessas interfaces não prova que todas as categorias fiscais sejam representadas corretamente pelos agregadores; a cobertura deve ser examinada por caminho de execução.

<!-- p:243 -->
O backend utiliza FastAPI para definir as rotas e modelos Pydantic para validar os objetos recebidos. O processamento estruturado seleciona a calculadora correspondente ao ativo, consulta os dados persistidos necessários e devolve a memória do cálculo. As rotas de histórico e resumo consultam registros existentes. A Tabela 1 apresenta as interfaces principais, não uma declaração de que todos os caminhos foram avaliados de ponta a ponta.

<!-- p:244 -->
Tabela 1 – Principais interfaces HTTP inspecionadas

<!-- p:245 -->
Fonte: elaboração própria a partir da inspeção do código da aplicação (2026).

<!-- p:246 -->
O modelo TradeInput valida tipos e restrições básicas, mas validação sintática não é validação tributária. Quantidade positiva e preço positivo não informam se houve day trade, qual foi o custo de aquisição ou se o total mensal é completo. Foram introduzidos campos explícitos para contexto mensal, custo médio informado, classificação declarada, custos efetivos e retenção informada. Não há detecção automática completa de day trade ou importação consolidada de todas as corretoras.

<!-- p:247 -->
## 5.4 Orquestração e modelos de linguagem

<!-- p:248 -->
A orquestração está implementada em classes Python, em app/agents, e utiliza o cliente do SDK da Anthropic em app/llm/claude_client.py. O método Orchestrator.process primeiro solicita a classificação da intenção. Se uma classe de ativo é identificada, chama o extrator de operação e delega o processamento ao agente especializado; caso contrário, encaminha a pergunta ao fluxo consultivo geral. Havendo operação calculável, o agente delega a execução ao gateway MCP; após o retorno, o resultado numérico e o contexto documental são enviados ao modelo para explicação.

<!-- p:249 -->
Na configuração do backend, claude-haiku-4-5-20251001 é destinado à classificação e extração, enquanto claude-sonnet-5 é destinado à explicação. Esses identificadores são parâmetros de configuração, não provas de superioridade universal dos modelos. O estudo comparativo mantém seus próprios registros de chamadas e não deve ser confundido com um teste integral desse roteador.

<!-- p:250 -->
Nos agentes, uma compra extraída pode ser registrada com uma confirmação; uma venda exige seleção da calculadora e custo de aquisição disponível. O cálculo estruturado é então utilizado na construção do pedido de explicação. Se não houver operação extraída, o agente trata a mensagem como pergunta documental. Erros de validação são tratados com mensagem de impossibilidade de cálculo e sem registrar a venda. Esse encadeamento está em BaseAgent.process e BaseAgent._process.

<!-- p:251 -->
Para explicar um cálculo, o código recupera até dois trechos (top_k=2); para perguntas sem operação extraída e para o fluxo consultivo, utiliza até três (top_k=3). O benchmark de recuperação também usa três. Portanto, o valor de k depende do caminho e os escores do Capítulo 7 não medem automaticamente todas as variações do fluxo interativo.

<!-- p:252 -->
## 5.5 Base vetorial e recuperação documental

<!-- p:253 -->
Na configuração inicial, cada arquivo textual era inserido como documento inteiro. Coleções específicas eram consultadas primeiro, e a coleção geral preenchia vagas remanescentes. A busca devolvia somente o texto, sem identificador e origem apresentados ao consumidor. Esse procedimento podia selecionar conteúdos de categorias próximas e dificultava examinar qual evidência sustentava uma resposta.

<!-- p:254 -->
A configuração revisada utiliza 18 trechos curados, cada um com identificador, origem, categoria e data de consulta. A busca é global e ordenada por distância de cosseno; não há filtro rígido de categoria, pois algumas perguntas comparam ativos. O limite de três resultados foi mantido para a avaliação. Não foi calibrado um limiar numérico de rejeição, e a ausência de evidência suficiente é tratada nas instruções ao modelo. Logo, não se deve descrever essa versão como um recuperador com abstenção probabilística calibrada.

<!-- p:255 -->
O recorte em unidades de regra foi feito editorialmente. Trata-se de curadoria manual assistida por IA, não de um algoritmo geral de segmentação por tokens. A evidência experimental permite comparar duas configurações completas de recuperação e contexto; não permite separar o efeito de remover uma regra errada do efeito de alterar a granularidade ou a ordenação.

<!-- p:256 -->
A instalação inspecionada utiliza ChromaDB 0.5.3, PersistentClient e a função padrão ONNXMiniLM_L6_V2, associada a all-MiniLM-L6-v2. As representações são produzidas localmente. A manutenção dessa função nas duas configurações procurou evitar uma troca simultânea do modelo de embeddings; não resultou de uma comparação de alternativas para português jurídico. O cliente revisado define a coleção regulacoes_revisadas_v1 e o parâmetro hnsw:space como cosine.

<!-- p:257 -->
A coleção utiliza a infraestrutura de indexação HNSW disponibilizada pelo ChromaDB. O código da aplicação solicita n_results=min(k, quantidade_de_documentos), sem implementar seu próprio algoritmo ANN. Não foi medida a diferença entre busca exata e aproximada; o pequeno corpus serve à avaliação das respostas, não a conclusões sobre ganho de desempenho do índice.

<!-- p:258 -->
Os 18 trechos são resumos curados, e não cópias integrais de leis. Suas fontes estão identificadas em app/vector_db/curated.py: orientações da Receita Federal sobre isenção e compensação, Instrução Normativa RFB nº 1.585/2015, legislação tributária, solução de consulta sobre criptoativos e especificações da B3 para WIN, WDO, BDRs e empréstimo de ativos. Cada registro reúne id, text, source, asset_type e checked_at. A data de consulta não deve ser confundida com a vigência da norma.

<!-- p:259 -->
Por exemplo, o trecho acoes_isencao mantém no mesmo registro a condição mensal e as exclusões por categoria, evitando separar a regra de sua qualificação. Não há tamanho fixo de tokens nem sobreposição automática: a segmentação foi editorial. load_initial_regulations insere os registros com upsert; search_evidence devolve identificador, texto, metadados e distância; search_regulations formata o contexto com origem e data. O filtro asset_type não restringe a ordenação global no cliente revisado.

<!-- p:260 -->
Cada regra utilizada em produção deveria combinar origem, data de consulta, vigência e condições de aplicação. A data em que uma página foi acessada não é sua data de vigência. A versão experimental introduz identificação e data de consulta nos trechos, mas não implementa um sistema completo de versões históricas ou resolução de conflitos normativos.

<!-- p:261 -->
A preferência por fontes brasileiras segue uma hierarquia prática: textos legais, orientações da Receita Federal e especificações oficiais da B3 antecedem comentários de terceiros. Fontes internacionais são reservadas principalmente aos métodos de inteligência artificial. Essa escolha procura aproximar a referência da autoridade competente, sem presumir que qualquer página institucional isolada resolva todas as exceções de uma operação.

<!-- p:262 -->
A atualização implementada consiste em editar os registros curados e carregá-los novamente; não há robô de consulta automática às páginas oficiais. Para uma nova regra, devem ser conferidos fonte, vigência e reflexos no cálculo antes de reindexar e executar regressões. O gerenciamento completo de histórico normativo e conflitos entre versões permanece proposta de evolução na Seção 8.3.

<!-- p:263 -->
## 5.6 Calculadoras e tratamento de dados ausentes

<!-- p:264 -->
As correções numéricas focalizam condições que podem ser verificadas por cenários pequenos. Para ações, a isenção depende de total mensal informado; para criptoativos nacionais, deixa de ser decidida pelo valor de uma venda isolada. A progressividade passa a operar por parcelas. Em WIN e WDO, os multiplicadores do contrato são incorporados, e o nocional deixa de ser apresentado como recebimento líquido do encerramento.

<!-- p:265 -->
As calculadoras são classes Python em backend/app/calculations. O servidor mcp_server/runtime_server.py importa e reutiliza essas classes, sem reproduzir suas fórmulas. O gateway backend/app/mcp_gateway.py é acionado pelos agentes e pelas rotas POST /api/trades/process e POST /api/trades/batch. Apenas após uma resposta válida o backend registra a venda. Compras são registradas sem cálculo; falhas MCP não são substituídas por execução direta. O resultado inclui ganho, imposto, retenções e custos, sem equiparar estimativas tarifárias a custos efetivamente comprovados.

<!-- p:266 -->
A ausência de custo médio não deve produzir automaticamente ganho zero. Do mesmo modo, prazo contratual ausente no empréstimo não deve ser convertido silenciosamente em uma faixa de retenção. Os testes de segurança verificam essas recusas. A mensagem ao usuário informa que os dados são insuficientes, distinguindo uma recusa de cálculo de um imposto efetivamente igual a zero.

<!-- p:267 -->
## 5.7 Persistência e rastreabilidade

<!-- p:268 -->
As cópias de trabalho inicial e revisada foram mantidas separadas do repositório original. Um manifesto de hashes permite identificar os arquivos inspecionados. O benchmark, os contextos recuperados e as respostas são persistidos como artefatos do experimento. As chaves de API não foram copiadas para a documentação ou para o corpus, e somente perguntas sintéticas e informações públicas foram encaminhadas aos modelos.

<!-- p:269 -->
A persistência operacional utiliza SQLAlchemy e, na configuração local padrão, SQLite. As funções de repositório registram operações e conversas e consultam o preço médio por usuário e ativo. Esses registros de aplicação são distintos dos arquivos JSON do experimento: os primeiros suportam o histórico operacional, enquanto os segundos permitem conferir perguntas, evidências e notas do benchmark.

<!-- p:270 -->
## 5.8 Servidor MCP e instruções de geração

<!-- p:271 -->
Dois servidores têm papéis distintos. O arquivo mcp_server/server.py preserva as ferramentas legadas get_tax_rules, get_fee_structure, example_calculation, get_regulation e validate_calculation, originalmente destinadas ao apoio ao desenvolvimento. O novo mcp_server/runtime_server.py expõe fee_policy e calculate_trade para execução pelo backend. A primeira ferramenta informa a política de custos; a segunda valida entradas e reutiliza a calculadora correspondente ao ativo. Não há acesso ao banco operacional nem chamada a LLM nesse servidor.

<!-- p:272 -->
A integração utiliza o SDK Python MCP 1.28.0 e transporte stdio. O backend inicia um subprocesso local com o mesmo interpretador Python, inicializa a sessão e chama as duas ferramentas por tools/call. A seleção é determinada pelo código após a interpretação da operação, não por escolha autônoma de ferramentas pelo LLM. Cada cálculo abre e encerra uma sessão; o pedido possui limite global de 30 segundos. A resposta é validada contra o esquema de cálculo e a identificação da operação antes de sua utilização. Trata-se de integração local, não de um serviço HTTP MCP exposto na rede.

<!-- p:273 -->
A ferramenta fee_policy não realiza consulta tarifária em tempo real: informa a origem interna da política e declara ausência de vigência validada. Custos explicitamente fornecidos são encaminhados às calculadoras. Quando ausentes, eventuais parâmetros legados devem ser tratados como estimativas, com ressalva incluída na resposta. Os prompts e a recuperação ChromaDB permanecem no backend. A integração muda o transporte do cálculo, não comprova atualização tributária, correção de todas as fórmulas ou autonomia de decisão do modelo.

<!-- p:274 -->
Um trecho das instruções experimentais estabelece: “Use somente as evidências fornecidas para afirmações normativas”. Outro determina: “Se faltar evidência ou dados, peça esclarecimento e explicite limites”. Essas instruções são próprias do experimento e estão registradas em experiment.py. Elas procuram induzir comportamento prudente, mas sua presença no prompt não comprova obediência; é necessário observar as respostas e os erros marcados pela avaliação.

<!-- p:275 -->
# 6 CRITÉRIOS DE AVALIAÇÃO

<!-- p:276 -->
São descritos a composição do benchmark, as configurações comparadas, as rubricas, as métricas e as condições de reprodução. A apresentação separa dados de desenvolvimento e teste e explicita quais componentes da aplicação não foram incluídos na avaliação controlada. A verificação posterior do transporte MCP é uma etapa separada, com testes automatizados locais; não houve nova comparação de modelos nem avaliação de usuários nessa etapa.

<!-- p:277 -->
## 6.1 Desenho e unidade de análise

<!-- p:278 -->
A pesquisa é aplicada e utiliza estudo experimental controlado de um protótipo. O desenho reúne inspeção do código, preparação de corpus, benchmark sintético, geração de respostas, avaliação automática e testes determinísticos. A data de referência das consultas é 12 de setembro de 2026. Os arquivos de execução registram as versões solicitadas e retornadas pela API, utilização de tokens e duração das chamadas.

<!-- p:279 -->
O benchmark contém 60 perguntas: 12 de desenvolvimento exploratório e 48 de teste. As perguntas de teste estão distribuídas igualmente em oito estratos: ações, BDRs, FIIs, opções, futuros, empréstimo, criptoativos e consultas ambíguas ou fora de escopo. As 42 perguntas dos sete primeiros estratos compõem os escores de recuperação. As seis restantes são analisadas separadamente quanto à resposta prudente e à solicitação de esclarecimento.

<!-- p:280 -->
As perguntas e os fatos esperados foram elaborados com assistência de IA a partir do domínio selecionado. Não são consultas reais amostradas de usuários e não receberam homologação de especialista tributário. Essa origem deve ser considerada ao interpretar os resultados. A separação entre desenvolvimento e teste reduz reutilização direta de exemplos, mas não torna o conjunto independente do processo de curadoria que o produziu.

<!-- p:281 -->
## 6.2 Configurações comparadas

<!-- p:282 -->
Foram geradas três respostas para cada pergunta de teste: Sonnet 5 com contexto inicial, Sonnet 5 com contexto revisado e Haiku 4.5 com contexto revisado. Os identificadores utilizados foram claude-sonnet-5 e claude-haiku-4-5-20251001. O texto das instruções foi mantido igual entre configurações, com limite de saída definido no executor. Não houve ajuste fino, busca de melhores respostas ou seleção entre múltiplas gerações por qualidade.

<!-- p:283 -->
O domínio usado para escolher a coleção inicial foi fornecido pelo benchmark. A avaliação, portanto, não mede acerto do roteador nem extração de operações em linguagem natural. Ela compara geração com recuperação real sob condições controladas. Os testes das calculadoras constituem uma etapa distinta, que recebe entradas estruturadas e não depende da interpretação de um modelo.

<!-- p:284 -->
## 6.3 Relevância e métricas de recuperação

<!-- p:285 -->
A rubrica atribui grau 0 a trecho irrelevante ou contraditório, grau 1 a informação parcial e grau 2 a evidência diretamente pertinente e correta para o núcleo da pergunta. P@1 indica se o primeiro resultado recebe grau 2. P@3 corresponde à quantidade de resultados com grau 2 dividida por três; uma posição ausente vale zero. Um resultado apenas relacionado ao assunto não é automaticamente considerado relevante no sentido binário.

<!-- p:286 -->
A rotulação é realizada por LLM-as-a-Judge, não por especialistas humanos. Para cada pergunta, judge.py reúne os trechos retornados pelas duas configurações, elimina duplicatas por identificador e solicita um grau para cada par pergunta–trecho. O arquivo de notas preserva grau e justificativa. As métricas usam esses julgamentos e a ordenação originalmente devolvida por cada recuperador, sem reordenar os resultados pelo gabarito.

<!-- p:287 -->
A medida nDCG@3 utiliza ganho 2 elevado ao grau menos 1 e desconto logarítmico da posição. Neste experimento, o denominador ideal é calculado sobre a união dos trechos recuperados pelas duas configurações e julgados para a pergunta. Por isso, a medida é denominada nDCG@3 agrupada e não representa julgamento exaustivo de todo o corpus. Esse detalhe torna o cálculo reproduzível e delimita sua interpretação.

<!-- p:288 -->
Uma questão pode exigir apenas um trecho diretamente suficiente. Nesse caso, P@3 pode permanecer baixo mesmo quando a resposta dispõe da regra necessária. As medidas devem ser lidas conjuntamente: P@1 expressa prioridade, P@3 expressa proporção de contexto diretamente relevante e nDCG agrega posição e gradação. Nenhuma delas substitui a verificação da resposta gerada.

<!-- p:289 -->
Como exemplo didático da rubrica, para uma consulta sobre isenção na venda de FII, um trecho que trate diretamente da tributação da venda, distinguindo-a da isenção de ações, recebe grau 2; um trecho apenas geral sobre o fundo pode receber grau 1; uma regra de outro ativo aplicada incorretamente recebe grau 0. Se os graus dos três primeiros resultados forem [2, 1, 0], P@1 será 1 e P@3 será 1/3. O exemplo explica o cálculo e não constitui uma observação adicional do benchmark. MRR não foi calculado nesta execução; não se atribui a ele resultado inexistente.

<!-- p:290 -->
## 6.4 Julgamento das respostas e repetição

<!-- p:291 -->
O modelo claude-opus-5 atuou como avaliador automático, recebendo respostas anonimizadas e ordem embaralhada com semente reproduzível. A rubrica separa correção, fundamentação, erro crítico e abstenção adequada. Uma resposta é computada como correta no indicador estrito quando recebe nota 2 de correção e não apresenta erro crítico. Os fatos esperados e URLs são fornecidos ao avaliador; isso não significa que o avaliador tenha consultado autonomamente cada página oficial.

<!-- p:292 -->
A correção recebe 0 para resposta errada, 1 para parcialmente correta ou incompleta e 2 para correta nos fatos essenciais. A fundamentação recebe 0 para ausência de suporte ou contradição, 1 para suporte parcial e 2 para suporte no contexto. Erro crítico marca regra ou valor fiscal incorreto ou dado inventado; abstenção adequada indica conduta pertinente diante de dados ausentes ou consulta fora do escopo. Clareza não foi pontuada separadamente, e completude participa da nota de correção. Essa descrição corresponde à rubrica executada, em vez de listar dimensões que não foram mensuradas.

<!-- p:293 -->
Doze perguntas distribuídas pelos estratos foram selecionadas previamente para repetição do julgamento, resultando em 36 pares de notas de resposta. A repetição examina estabilidade, e não substitui um segundo especialista. Saídas com formato inválido foram preservadas e repetidas para obter registros processáveis. Os custos dessas tentativas também integram o total, evitando contabilizar apenas chamadas aproveitadas.

<!-- p:294 -->
Os três modelos pertencem ao mesmo fornecedor. Essa escolha foi viabilizada pelas credenciais disponíveis, mas introduz possível correlação entre estilos, conhecimento e critérios do gerador e do avaliador. A monografia não denomina os escores como acurácia jurídica validada. A expressão utilizada é correção segundo avaliação automática sob a rubrica descrita.

<!-- p:295 -->
## 6.5 Verificação numérica e reprodução

<!-- p:296 -->
Doze cenários independentes de entrada estruturada verificam isenção de ações, classificação de day trade, agregação de cripto, progressividade, multiplicadores de futuros e quatro faixas do empréstimo. A tolerância de comparação para valores monetários é R$ 0,01 nos campos esperados. Os cenários e os resultados completos estão em arquivos JSON; não foram inferidos da redação das respostas do modelo.

<!-- p:297 -->
Os testes estão em backend/tests do projeto consolidado; o executor dos 12 cenários está em experimentos_historicos/calculator_checks.py. Os arquivos benchmark.json, baseline_retrieval.json, revised_retrieval.json, api_results e results_per_case.csv permitem rastrear a avaliação textual. Os comandos de reprodução e o inventário do pacote são apresentados no Apêndice B. Não é informado endereço público de repositório, pois nenhum URL de publicação foi confirmado para esta entrega.

<!-- p:298 -->
A suíte inicial de 74 testes também foi executada. Após as alterações de contrato, 23 testes legados falharam por ausência de dados exigidos ou por expectativas associadas às simplificações anteriores. A migração posterior produziu uma suíte com 88 aprovações. Entretanto, a conferência desta edição identificou que um teste aceitava indevidamente a isenção de R$ 20 mil para BDRs e que a calculadora reproduzia essa expectativa. Essa alteração era uma regressão, não uma correção tributária. O caso evidencia que testes aprovados verificam aderência às expectativas programadas, mas não garantem que essas expectativas estejam juridicamente corretas.

<!-- p:299 -->
Na correção posterior, a isenção foi removida da calculadora de BDRs e o teste equivocado foi corrigido. Foram acrescentadas seis verificações: quatro combinações de informação mensal (ausente, R$ 2.000, R$ 20.000 e R$ 20.001), recusa por ausência de custo médio e dedução de custos efetivos. O total mensal não é necessário para decidir sobre uma isenção inexistente de BDRs. Mantiveram-se a exigência do custo de aquisição e as alíquotas da modalidade declarada. A fundamentação consultada é o material brasileiro da B3 já citado no Capítulo 3 (B3, 2026b).

<!-- p:300 -->
Essa verificação posterior não altera o benchmark congelado nem os escores de recuperação e geração. Os oito testes de segurança previamente adicionados permanecem na suíte; não são somados novamente ao total. A reexecução local foi registrada separadamente, sem novas chamadas a modelos. Para futuros, preservou-se o cálculo com custos efetivos; a existência do tratamento compartilhado em calculate_b3_fees não permite sustentar a afirmação anterior de que esses custos nunca eram utilizados.

<!-- p:301 -->
# 7 RESULTADOS E DISCUSSÃO

<!-- p:302 -->
Os resultados são organizados em avaliação quantitativa e demonstração documentada. Primeiro são examinadas respostas, recuperação, estabilidade e cálculos; em seguida, são apresentados exemplos de saídas registradas. As limitações são retomadas na conclusão sem alterar os denominadores ou omitir resultados desfavoráveis. Os benchmarks e as capturas apresentados neste capítulo antecedem a integração MCP de 16 de setembro de 2026. Eles não demonstram o novo transporte de execução.

<!-- p:303 -->
## 7.1 Avaliação objetiva

<!-- p:304 -->
Foram concluídas 144 gerações de teste, além das 12 gerações exploratórias de desenvolvimento. O avaliador processou as 48 perguntas de teste e repetiu 12 delas. A Tabela 2 apresenta os resultados por configuração. Os denominadores são explicitados para que perguntas factuais e casos de esclarecimento não sejam somados indistintamente em uma única taxa.

<!-- p:305 -->
Tabela 2 – Correção factual e erros críticos

<!-- p:306 -->
Fonte: elaboração própria a partir dos registros dos experimentos (2026).

<!-- p:307 -->
Figura 3 – Correção factual segundo avaliação automática

<!-- p:309 -->
Fonte: elaboração própria a partir do código e dos registros experimentais (2026).

<!-- p:310 -->
No conjunto factual, o Sonnet com corpus revisado obteve 37 respostas corretas em 42, contra 29 com corpus inicial. A diferença observada é de oito respostas, ou aproximadamente 19 pontos percentuais. O Haiku com contexto revisado obteve 30 em 42. Esse resultado é compatível com benefício da revisão no cenário estudado, mas não estabelece que o mesmo ganho ocorreria com consultas externas ou outra distribuição de ativos.

<!-- p:311 -->
O avaliador marcou nove respostas com erro crítico na configuração inicial, sete com Haiku revisado e nenhuma com Sonnet revisado. A ausência de marcações nessa última configuração não equivale à prova de ausência de erro. Há respostas incompletas, possibilidade de falha do avaliador e cobertura limitada do benchmark. Uma conclusão responsável deve preservar essas diferenças.

<!-- p:312 -->
Tabela 3 – Recuperação: 42 perguntas factuais

<!-- p:313 -->
Fonte: elaboração própria a partir dos registros dos experimentos (2026).

<!-- p:314 -->
Figura 4 – Precisão dos primeiros resultados recuperados

<!-- p:316 -->
Fonte: elaboração própria a partir do código e dos registros experimentais (2026).

<!-- p:317 -->
A recuperação apresentou melhora menor que a correção das respostas. P@1 passou de 52,4% para 57,1%, enquanto P@3 passou de 23,8% para 30,2%. A nDCG@3 agrupada passou de 0,517 para 0,560. Isso sugere que contexto mais bem organizado e menos contraditório pode ajudar a geração sem produzir uma recuperação perfeita. Não permite, porém, separar qual mudança foi responsável por cada resposta corrigida.

<!-- p:318 -->
As seis consultas de abstenção ou esclarecimento receberam marcação de conduta adequada nas três configurações. Entretanto, essa dimensão não implica nota máxima de correção em toda a resposta: uma orientação prudente pode coexistir com incompletude em outros aspectos da rubrica. Por isso, o documento não apresenta esses seis casos como prova de segurança universal.

<!-- p:319 -->
## 7.2 Estabilidade, duração e custo

<!-- p:320 -->
Nas 36 comparações de notas repetidas, 32 mantiveram o grau de correção, correspondendo a 88,9% de concordância simples. As marcações de erro crítico coincidiram nas 36. A discordância observada demonstra que o julgamento não é inteiramente estável. Também não se trata de concordância entre avaliadores humanos independentes, pois as repetições usam o mesmo modelo e a mesma rubrica.

<!-- p:321 -->
As medianas de duração das chamadas de resposta foram aproximadamente 6,81 segundos para Sonnet inicial, 6,13 segundos para Sonnet revisado e 4,21 segundos para Haiku revisado. Não foram incluídos nesses números o tempo humano de curadoria, o processo de julgamento ou uma simulação de acesso concorrente por usuários. Não se deve apresentar a mediana da API como tempo garantido de atendimento da aplicação completa.

<!-- p:322 -->
O custo registrado total foi US$ 4,893393, incluindo desenvolvimento, respostas, julgamentos, repetições e tentativas de formato. As 48 respostas de teste custaram aproximadamente US$ 0,56 no Sonnet inicial, US$ 0,33 no Sonnet revisado e US$ 0,12 no Haiku revisado. O menor contexto da revisão contribui para a interpretação dessa diferença; não é uma comparação isolada de preços entre modelos.

<!-- p:323 -->
## 7.3 Resultados das calculadoras e testes de segurança

<!-- p:324 -->
Tabela 4 – Verificação numérica antes e depois

<!-- p:325 -->
Fonte: elaboração própria a partir dos registros dos experimentos (2026).

<!-- p:326 -->
Figura 5 – Verificação dos cenários numéricos

<!-- p:328 -->
Fonte: elaboração própria a partir do código e dos registros experimentais (2026).

<!-- p:329 -->
Nos 12 cenários numéricos definidos, a cópia inicial atendeu seis expectativas e a revisada atendeu as 12. O ganho observado envolve os limites mensais, a progressividade e os multiplicadores. Os quatro casos de retenção do doador já eram atendidos na versão inicial. A revisão, portanto, não deve reivindicar como nova uma funcionalidade que já produzia o resultado esperado.

<!-- p:330 -->
O histórico dos testes compreende 74 aprovações na suíte inicial, 51 aprovações e 23 falhas na versão intermediária e 88 aprovações após a migração. O último resultado incluía uma expectativa tributária incorreta para BDRs. Após a correção descrita na Seção 6.5 e a inclusão de seis verificações, a reexecução desta edição apresentou 94 testes aprovados e dois avisos de descontinuação de dependências. Os 12 cenários numéricos da Tabela 4 também foram reexecutados e mantiveram os resultados esperados na cópia revisada. Esses 12 casos não incluem BDRs; portanto, não teriam detectado a regressão da isenção.

<!-- p:331 -->
Como verificação adicional, considerou-se a venda comum de dez BDRs AAPL34 por R$ 200 cada, com custo médio de R$ 100, custos operacionais e IRRF informados iguais a zero, sem prejuízos a compensar. O valor de venda é R$ 2.000 e o ganho líquido é R$ 1.000. A expectativa é IR de R$ 150 (R$ 1.000 × 15%), sem isenção. A versão com regressão retornava R$ 0; a calculadora corrigida retornou R$ 150. Esse caso foi executado diretamente no motor, não pela interface, e não integra retroativamente a Tabela 4 nem os escores dos modelos.

<!-- p:332 -->
Os registros pytest_corrigido.txt, calculadoras_12_reexecutadas.json e bdr_regressao_corrigida.json documentam a verificação posterior. A aprovação da suíte não constitui validação tributária independente nem avaliação completa do roteador, da extração em linguagem natural ou da interface. O episódio reforça a necessidade de conferir os gabaritos com fontes externas e ampliar a cobertura por categoria de ativo. Em verificação posterior da integração MCP, realizada em 16 de setembro de 2026, a suíte executou 100 testes aprovados e dois avisos de depreciação, com banco temporário e sem APIs de IA. Seis testes adicionais cobriram protocolo stdio real, cálculo de FII, custo ausente, custo informado, total mensal ausente, servidor indisponível e compatibilidade da interface síncrona em contexto assíncrono. O registro está em evidencias/mcp_integracao_20260916/pytest_mcp.txt. Esse resultado é verificação de software, não validação tributária independente ou reexecução do benchmark de respostas.

<!-- p:333 -->
## 7.4 Demonstração documentada do protótipo

<!-- p:334 -->
A demonstração é separada dos escores quantitativos. As respostas completas e os resultados estruturados foram preservados, permitindo materializar exemplos sem inventar sessões de navegação. Nesta edição, os exemplos abaixo primeiro documentam saídas efetivamente registradas pelo executor experimental — não um teste de usabilidade da interface Angular — e, em seguida, capturas de tela reais da interface, obtidas em uma sessão de navegador conectada nesta revisão, contra o backend revisado rodando com dados sintéticos.

<!-- p:335 -->
Exemplo T13 – fii

<!-- p:336 -->
Pergunta: Vendi FII por R$ 5 mil com lucro. A isenção de 20 mil serve?

<!-- p:337 -->
Não, essa isenção não se aplica a FII.

<!-- p:338 -->
Segundo a evidência fii_venda: a venda de cotas de fundo imobiliário tem o ganho líquido tributado em 20%, sem isenção por vendas abaixo de R$ 20 mil — essa isenção é exclusiva para ações negociadas em bolsa (regra distinta, não citada aqui como aplicável a FII).

<!-- p:339 -->
Pontos importantes a distinguir: - Tipo de ativo: FII segue regra própria (20% sobre ganho, sem faixa de isenção), diferente de ações. - Venda vs. rendimento: a evidência destaca que venda de cota, rendimento distribuído pelo fundo (isento para PF em certas condições, não detalhado aqui) e venda direta de imóvel são fatos geradores distintos — não confunda o lucro na venda das cotas com os rendimentos mensais distribuídos. - Apuração e recolhimento: o imposto sobre o ganho de capital na venda de FII normalmente é apurado e recolhido via DARF pelo próprio investidor, não por retenção automática — mas não tenho evidência detalhada sobre alíquota de IRRF específica aqui, então não posso confirmar percentual de retenção.

<!-- p:340 -->
Se precisar, posso detalhar a apuração do ganho (preço de venda menos custo de aquição) com mais dados. Isso é orientação educacional, não uma apuração fiscal definitiva — confirme com contador ou informe de rendimentos.

<!-- p:341 -->
Fonte: saída registrada da configuração Sonnet/revisado. Transcrição do experimento; não é captura de interface.

<!-- p:342 -->
Exemplo T01 – acoes

<!-- p:343 -->
Pergunta: Vendi R$ 19.500 em ações à vista em todo o mês, com lucro, operação comum. PF residente. Há isenção?

<!-- p:344 -->
Com base no evidence "acoes_isencao": para ações à vista, PF residente, operações comuns (não day trade), há isenção de imposto sobre o ganho quando o total das vendas no mês (somando todas as corretoras) não ultrapassa R$ 20.000.

<!-- p:345 -->
No seu caso: vendas totais de R$ 19.500 no mês, em operação comum à vista → está dentro do limite de isenção, pois R$ 19.500 < R$ 20.000.

<!-- p:346 -->
Pontos importantes: - O limite incide sobre o valor das vendas, não sobre o lucro (rendimento). - Essa isenção vale apenas para ações à vista em operações comuns; não se aplica a day trade, opções, FII, ETF ou BDR. - Isenção não dispensa de informar a operação na Declaração de Ajuste Anual (obrigação acessória), apenas exclui o imposto sobre o ganho.

<!-- p:347 -->
Limitação: não tenho evidência sobre se há outras vendas de renda variável no mesmo mês (ex.: FIIs, day trade) que possam alterar o enquadramento. Se houver, isso pode mudar a análise — por favor confirme se essa foi a única operação em ações à vista no mês.

<!-- p:348 -->
Fonte: saída registrada da configuração Sonnet/revisado. Transcrição do experimento; não é captura de interface.

<!-- p:349 -->
Exemplo T37 – cripto

<!-- p:350 -->
Pergunta: PF residente só cripto nacional: vendas mensais R$ 30 mil com lucro. Limite é 20 mil?

<!-- p:351 -->
Não, o limite de R$ 20.000 é específico para ações à vista (evidência `acoes_isencao`) — não se aplica a criptoativos.

<!-- p:352 -->
Para criptoativos nacionais, a evidência `cripto_isencao` indica um regime próprio: soma-se o total das alienações (vendas e também permutas entre criptomoedas, mesmo sem conversão em reais) no mês, em todas as exchanges/carteiras. Se esse total não ultrapassar R$ 35.000, pode haver isenção do ganho de capital.

<!-- p:353 -->
No seu caso, com vendas mensais de R$ 30.000, o total está abaixo de R$ 35.000, o que pode indicar isenção — mas isso depende de: - confirmação de que R$ 30.000 é a soma de todas as alienações do mês (incluindo eventuais permutas cripto-cripto, que também contam); - ausência de outras operações que somem ao total mensal; - verificação de regras de apuração de custo e lucro tributável nos meses em que o limite for ultrapassado.

<!-- p:354 -->
Limite desta resposta: não tenho evidência sobre alíquotas aplicáveis quando o limite é excedido, nem sobre regras específicas de criptoativos no exterior. Recomendo conferir a fonte oficial (Instrução Normativa citada) e, se necessário, orientação de contador para seu caso concreto.

<!-- p:355 -->
Fonte: saída registrada da configuração Sonnet/revisado. Transcrição do experimento; não é captura de interface.

<!-- p:356 -->
Exemplo T25 – futuros

<!-- p:357 -->
Pergunta: Comprei um WIN e encerrei 500 pontos acima. Ganho bruto em reais?

<!-- p:358 -->
Com base na evidência [win]: no WIN, cada ponto vale R$ 0,20 por contrato. Para 1 contrato comprado com variação de +500 pontos:

<!-- p:359 -->
Ganho bruto = 500 × R$ 0,20 = R$ 100,00 (antes de custos, por contrato).

<!-- p:360 -->
Se você operou mais de um contrato, multiplique R$ 100 pela quantidade.

<!-- p:361 -->
Importante — isso é apenas o cálculo do resultado bruto da operação, não a apuração fiscal: - Isso é resultado de renda variável (day trade ou swing trade, dependendo do prazo entre abertura e encerramento), não "rendimento" no sentido de renda fixa nem "venda" de ativo à vista. - O regime tributário (alíquota, IRRF, compensação de perdas, DARF mensal) depende de fatores não informados aqui: foi day trade ou operação normal, houve outras operações no mês, há prejuízos a compensar, corretagem/emolumentos incidentes. - Não tenho evidência normativa fornecida sobre alíquotas específicas de day trade/swing trade em mercados futuros nesta base — não posso afirmar percentuais sem risco de erro.

<!-- p:362 -->
Para orientar a tributação exata, preciso saber: tipo de operação (day trade/normal), demais resultados do mês, e se há prejuízos anteriores a compensar. Isso é educativo, não é apuração fiscal definitiva.

<!-- p:363 -->
Fonte: saída registrada da configuração Sonnet/revisado. Transcrição do experimento; não é captura de interface.

<!-- p:364 -->
Exemplo T31 – emprestimo

<!-- p:365 -->
Pergunta: Doador PF, remuneração R$ 1.000 por 180 dias. IRRF e líquido sem taxas?

<!-- p:366 -->
A pergunta menciona "doador" e "remuneração por dias", sem indicar o tipo de operação (ex.: aluguel de ações, contrato futuro, empréstimo, etc.), o ativo envolvido, ou a natureza jurídica do pagamento (rendimento de aplicação financeira, ganho de capital, doação, etc.).

<!-- p:367 -->
As evidências fornecidas tratam apenas de: (1) ganhos em ações à vista (isenção até R$ 20.000 em vendas/mês), (2) operações com futuros (alíquotas 15%/20%, IRRF sobre ajustes diários), e (3) aplicações no exterior (Lei 14.754/2023, 15% anual). Nenhuma delas trata de "remuneração de doador" ou de um fluxo fixo diário de R$ 1.000 por 180 dias — isso pode se referir, por exemplo, a doação de óvulos/plasma, aluguel de bem, ou outra situação não coberta pelo material disponível.

<!-- p:368 -->
Não posso calcular IRRF nem valor líquido sem saber: (a) a natureza exata do rendimento, (b) o regime tributário aplicável, (c) se há alíquota/base legal específica para esse tipo de "remuneração de doador".

<!-- p:369 -->
Poderia esclarecer do que se trata essa remuneração (contrato, atividade, fonte pagadora)?

<!-- p:370 -->
Fonte: saída registrada da configuração Sonnet/revisado. Transcrição do experimento; não é captura de interface.

<!-- p:371 -->
Os exemplos permitem acompanhar o vínculo entre pergunta, contexto e resposta, incluindo limitações. No caso T31, a resposta não reconheceu a remuneração do doador no contexto de empréstimo de ações e sugeriu interpretações estranhas ao domínio, como doação de óvulos ou plasma. Não houve cálculo de IRRF ou de valor líquido. Trata-se de uma falha de adequação ao cenário pretendido, e não de demonstração bem-sucedida do empréstimo. O pedido de esclarecimento evita inventar um cálculo, mas não resolve a necessidade do usuário.

<!-- p:372 -->
O contexto recuperado apresentado na própria resposta T31 não contém a regra de remuneração do doador. Isso indica uma limitação de cobertura ou recuperação nesse caso; a contribuição de cada componente não foi isolada. O resultado deve ser distinguido do cálculo estruturado da Figura 7, no qual tipo de operação e prazo foram fornecidos explicitamente. A comparação mostra que o motor numérico pode funcionar para entradas estruturadas sem que o fluxo conversacional consiga identificar os mesmos fatos. Como continuidade, recomenda-se testar paráfrases que explicitem empréstimo de ações e situações ambíguas, sem substituir retroativamente a pergunta ou a resposta registradas.

<!-- p:373 -->
Além das saídas registradas pelo executor, esta revisão inclui capturas de tela da interface Angular operando de fato, com dados sintéticos e sem reaproveitar respostas de benchmark como se fossem tela do sistema.

<!-- p:374 -->
Figura 6 – Venda de FII pela interface — sucesso

<!-- p:376 -->
Fonte: Interface Angular conectada ao backend revisado, dados sintéticos, sessão de 2026-09-13.

<!-- p:377 -->
Leitura da evidência: a tela apresenta HGLG11, ganho bruto de R$ 1.000, IR devido de R$ 200, IRRF de R$ 0,43 e valor líquido de R$ 8.287,77. Esses valores descrevem a saída observada; não constituem conferência independente das tarifas ou de toda a apuração mensal.

<!-- p:378 -->
Figura 7 – Remuneração do doador pela interface — sucesso

<!-- p:380 -->
Fonte: Interface Angular conectada ao backend revisado, dados sintéticos, sessão de 2026-09-13.

<!-- p:381 -->
Leitura da evidência: para 200 unidades a R$ 0,60 e prazo de 300 dias, a tela apresenta remuneração bruta de R$ 120, retenção de R$ 24 e valor líquido de R$ 96. O cartão de IR devido exibe R$ 0; isso não significa ausência de tributação, pois a retenção aparece no cartão de IRRF. O cenário é estruturado e distinto da pergunta conversacional T31.

<!-- p:382 -->
Figura 8 – Chat em linguagem natural sobre FII — resposta real

<!-- p:384 -->
Fonte: captura da interface Angular conectada ao backend, sessão de 13 set. 2026. Resposta observada em uma interação de chat; a captura não mede a quantidade de chamadas internas a modelos.

<!-- p:385 -->
Para leitura na versão impressa, a pergunta exibida é: “Vendi FII por R$5 mil com lucro. A isenção de 20 mil serve?” A resposta informa que a isenção de R$ 20 mil não se aplica a FIIs e indica 20% sobre o ganho líquido. Esta é uma síntese da captura, não uma nova resposta do modelo.

<!-- p:386 -->
A observação final da resposta agrupa “come-cotas” e “dedo-duro” como exemplos de retenção. A associação é imprecisa para o contexto de venda de cotas de FII e não deve ser usada como orientação fiscal. Assim, a demonstração sustenta o acerto da distinção sobre isenção, mas não a correção integral de todas as formulações do chat.

<!-- p:387 -->
Figura 9 – Venda de ações pela interface — recusa observada por ausência de custo médio

<!-- p:389 -->
Fonte: captura da interface Angular, sessão de 13 set. 2026. Mensagem observada: “Informe o custo médio ou registre a aquisição antes da venda.”

<!-- p:390 -->
Figura 10 – Futuro WIN pela interface — recusa observada por ausência de custo médio

<!-- p:392 -->
Fonte: captura da interface Angular, sessão de 13 set. 2026. Mensagem observada: “Informe o custo médio ou registre a aquisição antes da venda.”

<!-- p:393 -->
As capturas documentam resultados distintos. A Figura 6 mostra um resultado de venda de FII; a Figura 7 mostra a remuneração do doador em empréstimo de ações; e a Figura 8 registra uma resposta do chat sobre a isenção de FIIs. Nas Figuras 9 e 10, as tentativas de venda de ações e WIN foram recusadas com a mensagem “Informe o custo médio ou registre a aquisição antes da venda.” A evidência permite concluir que o custo médio não estava disponível no fluxo executado, mas não determina, por si só, por que esse dado estava ausente.

<!-- p:394 -->
A inspeção do formulário indica uma possível lacuna entre os dados expostos na interface e os campos aceitos pelo backend. Entretanto, diagnosticar a causa das recusas exige conferir a requisição enviada, a identificação do usuário, o histórico de aquisições e as validações executadas. A ausência do total mensal de vendas não é a causa demonstrada pelas mensagens dessas duas capturas. Não há capturas equivalentes de tentativa de venda de BDRs ou criptoativos nesta sessão; por isso, não se afirma que essas categorias falharam nem que somente FII e empréstimo funcionam na interface.

<!-- p:395 -->
Os registros de chamadas diretas à API são evidências distintas das capturas. Um resultado correto com entradas estruturadas não comprova que o formulário consiga fornecer essas mesmas entradas. Da mesma forma, uma recusa por dado ausente não demonstra erro aritmético nem correção geral da calculadora. As capturas foram preservadas como registro da sessão anterior à correção posterior de BDRs; não foram produzidas novas capturas nem alegada uma revalidação visual de ponta a ponta nesta edição.

<!-- p:396 -->
Não foram medidos facilidade de uso, satisfação, tempo de aprendizagem ou taxa de sucesso de usuários reais. As capturas e os registros foram preservados com suas datas e entradas disponíveis. Uma imagem ilustra um estado observado, mas não substitui o registro completo de execução nem transforma uma demonstração individual em experimento estatístico.

<!-- p:397 -->
# 8 CONCLUSÃO

<!-- p:398 -->
## 8.1 Síntese das contribuições

<!-- p:399 -->
A dispersão e a complexidade das informações tributárias motivaram o desenvolvimento de um assistente em português que combina recuperação documental, geração textual e cálculo determinístico. O objetivo foi apoiar consultas com contexto e cálculos verificáveis. A implementação reuniu esses componentes em um protótipo, e a avaliação examinou separadamente recuperação, respostas e resultados numéricos.

<!-- p:400 -->
Os resultados sustentam uma conclusão circunscrita: no benchmark sintético utilizado, a configuração Sonnet com contexto revisado apresentou maior número de respostas factuais consideradas corretas pelo avaliador automático, e as correções numéricas atenderam aos 12 cenários especificados. A recuperação permaneceu imperfeita e o próprio julgamento apresentou variação em parte das repetições. Esses achados reforçam a necessidade de avaliar separadamente as camadas do sistema.

<!-- p:401 -->
## 8.2 Limitações

<!-- p:402 -->
As limitações incluem ausência de validação tributária independente, pequeno corpus, gabaritos assistidos por IA, comparação dentro de um fornecedor, julgamento não exaustivo dos documentos e simplificação de apuração mensal. A conferência posterior identificou uma regressão de BDR mesmo com 88 testes aprovados; após sua correção, a suíte ampliada apresentou 94 aprovações. Esse resultado não valida o roteador, a extração em linguagem natural nem a interface de ponta a ponta. As demonstrações também incluem falha de adequação da resposta sobre empréstimo e recusas por custo médio ausente. A versão documentada permanece experimental.

<!-- p:403 -->
A amostra é pequena e construída para os conteúdos do protótipo. O corpus revisado e os fatos esperados compartilham processo de preparação, o que pode favorecer alinhamento entre avaliação e solução. Os rótulos de relevância são automáticos. Além disso, a revisão altera simultaneamente regras, granularidade e recuperação, impedindo atribuir todo ganho observado a um único componente.

<!-- p:404 -->
As latências representam chamadas de API nessa execução, com concorrência limitada e sem estudo de carga. Os custos são calculados pelos tokens reportados e pelos preços públicos registrados, não por conciliação de fatura. Similaridade semântica entre resposta e gabarito não foi usada como substituta da correção: ela poderia premiar uma frase lexicalmente próxima com percentual ou negação incorretos.

<!-- p:405 -->
A cobertura operacional também é parcial: persistem simplificações de consolidação mensal, custo médio, tarifas legadas e classificação de eventos. A simulação de futuros não reproduz toda a trajetória de ajustes diários, posições vendidas ou rolagens, e a representação do empréstimo compartilha campos com operações de compra e venda. O identificador de usuário não constitui autenticação completa; segurança de uma implantação pública e adequação para apuração fiscal autônoma não foram validadas.

<!-- p:406 -->
A desatualização de fontes, a interpretação incorreta de dados e a execução de instruções indevidas são riscos que exigem curadoria e controles proporcionais. O protótipo não substitui avaliação profissional nem fonte normativa oficial. Essas restrições delimitam o uso dos resultados, sem apagar erros ou recusas observados nas demonstrações.

<!-- p:407 -->
## 8.3 Trabalhos futuros

<!-- p:408 -->
Como trabalhos futuros, priorizam-se a revisão dos gabaritos por especialista; consultas externas ao processo de desenvolvimento; contabilização mensal completa (agregação real de vendas por carteira, hoje informada pelo usuário); modelagem específica do empréstimo; cobertura de ajustes diários; comparação de embeddings para português; e avaliação de ponta a ponta com usuários. A expansão do domínio deverá ocorrer junto com evidências e testes, e não somente com a adição de novas classes ou novos textos.

<!-- p:409 -->
No plano de integração, propõe-se investigar obtenção autorizada de dados por serviços da B3 ou do Open Finance, conforme disponibilidade, consentimento e condições de acesso, além de extração assistida de documentos com confirmação dos campos. Essas alternativas deverão ser comparadas à entrada manual antes de serem apresentadas como funcionalidades implementadas.

<!-- p:410 -->
Outras evoluções incluem validar o fluxo MCP completo com navegador e modelos de linguagem, ampliar testes de falha, concorrência e tempo de resposta, versionar tarifas com fontes e vigência e registrar evidências por resposta. A sessão por cálculo e a compatibilidade síncrona do agente exigem avaliação de desempenho. Cada mudança deve ser acompanhada de revisão especializada, preservando os resultados históricos.

<!-- p:411 -->
# REFERÊNCIAS

<!-- p:412 -->
ANTHROPIC. Introducing the next generation of Claude. 2024. Disponível em: https://www.anthropic.com/news/claude-3-family. Acesso em: 13 set. 2026.

<!-- p:413 -->
ANTHROPIC. Pricing: Claude Platform Docs. 2026. Disponível em: https://platform.claude.com/docs/en/about-claude/pricing. Acesso em: 12 set. 2026.

<!-- p:414 -->
ASAI, Akari et al. Self-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection. 2023. Disponível em: https://arxiv.org/abs/2310.11511. Acesso em: 13 set. 2026.

<!-- p:415 -->
B3. 2025. Pessoas Físicas: uma análise da evolução dos investidores na B3 — 2º trimestre de 2025. Disponível em: https://www.b3.com.br/data/files/A2/A0/78/20/E61689100A29E189AC094EA8/Book%20PF%202TRI%202025_vF.pdf. Acesso em: 12 set. 2026.

<!-- p:416 -->
B3. 2026a. Empréstimo de ativos: informações. Disponível em: https://www.b3.com.br/pt_br/produtos-e-servicos/emprestimo-de-ativos/informacoes.htm. Acesso em: 12 set. 2026.

<!-- p:417 -->
B3. 2026b. Como declarar BDRs no Imposto de Renda 2026. Bora Investir. Disponível em: https://borainvestir.b3.com.br/noticias/imposto-de-renda/renda-variavel-imposto-de-renda/como-declarar-bdrs-no-imposto-de-renda-2026-veja-guia-completo-para-nao-cometer-erros/. Acesso em: 13 set. 2026.

<!-- p:418 -->
B3. 2026c. Futuro Mini de Ibovespa. Disponível em: https://www.b3.com.br/pt_br/produtos-e-servicos/negociacao/renda-variavel/futuro-mini-de-ibovespa.htm. Acesso em: 12 set. 2026.

<!-- p:419 -->
B3. 2026d. Futuro Míni de Taxa de Câmbio de Reais por Dólar Comercial. Disponível em: https://www.b3.com.br/pt_br/produtos-e-servicos/negociacao/moedas/futuro-mini-de-taxa-de-cambio-de-reais-por-dolar-comercial.htm. Acesso em: 12 set. 2026.

<!-- p:420 -->
B3. 2026e. Levantamento DataWise+. Disponível em: https://www.b3.com.br/pt_br/noticias/levantamento-datawise.htm. Acesso em: 13 set. 2026.

<!-- p:421 -->
BENDER, Emily M. et al. On the Dangers of Stochastic Parrots: Can Language Models Be Too Big? FAccT, 2021. Disponível em: https://dl.acm.org/doi/10.1145/3442188.3445922. Acesso em: 12 set. 2026.

<!-- p:422 -->
BRASIL. Lei nº 11.033, de 21 de dezembro de 2004. Texto consolidado. Disponível em: https://www.planalto.gov.br/ccivil_03/_ato2004-2006/2004/lei/l11033.htm. Acesso em: 12 set. 2026.

<!-- p:423 -->
BRASIL. Lei nº 13.259, de 16 de março de 2016. Disponível em: https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2016/lei/l13259.htm. Acesso em: 12 set. 2026.

<!-- p:424 -->
BRASIL. Lei nº 14.754, de 12 de dezembro de 2023. Disponível em: https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2023/lei/l14754.htm. Acesso em: 12 set. 2026.

<!-- p:425 -->
BRASIL. Lei nº 15.265, de 21 de novembro de 2025. Disponível em: https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2025/lei/l15265.htm. Acesso em: 12 set. 2026.

<!-- p:426 -->
BROWN, Tom B. et al. Language Models are Few-Shot Learners. NeurIPS, 2020. Disponível em: https://arxiv.org/abs/2005.14165. Acesso em: 12 set. 2026.

<!-- p:427 -->
COMISSÃO DE VALORES MOBILIÁRIOS. Mercado de derivativos no Brasil: conceitos, produtos e operações. 2. ed. Rio de Janeiro: CVM, 2025. Disponível em: https://www.gov.br/investidor/pt-br/educacional/publicacoes-educacionais/livros-cvm/top-mercado-de-derivativos-no-brasil-conceitos-produtos-e-operacoes.pdf. Acesso em: 13 set. 2026.

<!-- p:428 -->
COMISSÃO DE VALORES MOBILIÁRIOS. Mercado de valores mobiliários brasileiro. 5. ed. Rio de Janeiro: CVM, 2024. Disponível em: https://www.gov.br/investidor/pt-br/educacional/publicacoes-educacionais/livros-cvm/cvm-livro_top_valores_mobiliarios_br_5ed.pdf. Acesso em: 13 set. 2026.

<!-- p:429 -->
DEEPSEEK-AI. DeepSeek-V3 Technical Report. 2024. Disponível em: https://arxiv.org/abs/2412.19437. Acesso em: 13 set. 2026.

<!-- p:430 -->
DEVLIN, Jacob et al. BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding. NAACL-HLT, 2019. Disponível em: https://aclanthology.org/N19-1423/. Acesso em: 13 set. 2026.

<!-- p:431 -->
GEMINI TEAM. Gemini: A Family of Highly Capable Multimodal Models. 2023. Disponível em: https://arxiv.org/abs/2312.11805. Acesso em: 13 set. 2026.

<!-- p:432 -->
GEMMA TEAM. Gemma: Open Models Based on Gemini Research and Technology. 2024. Disponível em: https://arxiv.org/abs/2403.08295. Acesso em: 13 set. 2026.

<!-- p:433 -->
GOOGLE. Introducing EmbeddingGemma. 2025. Disponível em: https://developers.googleblog.com/introducing-embeddinggemma/. Acesso em: 13 set. 2026.

<!-- p:434 -->
GRATTAFIORI, Aaron et al. The Llama 3 Herd of Models. 2024. Disponível em: https://arxiv.org/abs/2407.21783. Acesso em: 13 set. 2026.

<!-- p:435 -->
JIANG, Albert Q. et al. Mistral 7B. 2023. Disponível em: https://arxiv.org/abs/2310.06825. Acesso em: 13 set. 2026.

<!-- p:436 -->
LEWIS, Patrick et al. Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks. NeurIPS, 2020. Disponível em: https://arxiv.org/abs/2005.11401. Acesso em: 12 set. 2026.

<!-- p:437 -->
LIU, Nelson F. et al. Lost in the Middle: How Language Models Use Long Contexts. 2023. Disponível em: https://arxiv.org/abs/2307.03172. Acesso em: 13 set. 2026.

<!-- p:438 -->
MALKOV, Yu. A.; YASHUNIN, D. A. Efficient and robust approximate nearest neighbor search using Hierarchical Navigable Small World graphs. 2016. Disponível em: https://arxiv.org/abs/1603.09320. Acesso em: 12 set. 2026.

<!-- p:439 -->
MODEL CONTEXT PROTOCOL. 2025a. Tools. Specification 2025-06-18. Disponível em: https://modelcontextprotocol.io/specification/2025-06-18/server/tools. Acesso em: 13 set. 2026.

<!-- p:440 -->
MODEL CONTEXT PROTOCOL. 2025b. Resources. Specification 2025-06-18. Disponível em: https://modelcontextprotocol.io/specification/2025-06-18/server/resources. Acesso em: 13 set. 2026.

<!-- p:441 -->
MODEL CONTEXT PROTOCOL. 2025c. Prompts. Specification 2025-06-18. Disponível em: https://modelcontextprotocol.io/specification/2025-06-18/server/prompts. Acesso em: 13 set. 2026.

<!-- p:442 -->
OPENAI. New embedding models and API updates. 2024. Disponível em: https://openai.com/index/new-embedding-models-and-api-updates/. Acesso em: 13 set. 2026.

<!-- p:443 -->
RECEITA FEDERAL. 2026a. Isenções: bolsa de valores. Disponível em: https://www.gov.br/receitafederal/pt-br/assuntos/meu-imposto-de-renda/pagamento/renda-variavel/bolsa-de-valores-1/isencoes. Acesso em: 12 set. 2026.

<!-- p:444 -->
RECEITA FEDERAL. 2026b. Fundos de Investimento no Brasil. Disponível em: https://www.gov.br/receitafederal/pt-br/assuntos/meu-imposto-de-renda/pagamento/renda-variavel/fundos-de-investimento-no-brasil. Acesso em: 12 set. 2026.

<!-- p:445 -->
RECEITA FEDERAL. 2026c. Compensações: bolsa de valores. Disponível em: https://www.gov.br/receitafederal/pt-br/assuntos/meu-imposto-de-renda/pagamento/renda-variavel/bolsa-de-valores-1/compensacoes. Acesso em: 12 set. 2026.

<!-- p:446 -->
RECEITA FEDERAL. Instrução Normativa RFB nº 1.585, de 31 de agosto de 2015. Disponível em: https://normas.receita.fazenda.gov.br/sijut2consulta/link.action?idAto=67494. Acesso em: 12 set. 2026.

<!-- p:447 -->
RECEITA FEDERAL. Solução de Consulta Cosit nº 214, de 20 de dezembro de 2021. Disponível em: https://normas.receita.fazenda.gov.br/sijut2consulta/anexoOutros.action?idArquivoBinario=64040. Acesso em: 12 set. 2026.

<!-- p:448 -->
REIMERS, Nils; GUREVYCH, Iryna. Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks. EMNLP-IJCNLP, 2019. Disponível em: https://aclanthology.org/D19-1410/. Acesso em: 12 set. 2026.

<!-- p:449 -->
VASWANI, Ashish et al. Attention Is All You Need. 2017. Disponível em: https://arxiv.org/abs/1706.03762. Acesso em: 12 set. 2026.

<!-- p:450 -->
YAO, Shunyu et al. ReAct: Synergizing Reasoning and Acting in Language Models. ICLR, 2023. Disponível em: https://arxiv.org/abs/2210.03629. Acesso em: 13 set. 2026.

<!-- p:451 -->
ZHENG, Lianmin et al. Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena. 2023. Disponível em: https://arxiv.org/abs/2306.05685. Acesso em: 12 set. 2026.

<!-- p:452 -->
# APÊNDICE A – BENCHMARK E FATOS ESPERADOS

<!-- p:453 -->
As perguntas seguintes são sintéticas. Os gabaritos são fatos esperados preparados com assistência de IA, não pareceres de especialista. A data de referência é 12/09/2026. A reprodução integral está em benchmark.json. As perguntas de desenvolvimento não integram os escores finais.

<!-- p:454 -->
T01 | acoes | Teste

<!-- p:455 -->
Vendi R$ 19.500 em ações à vista em todo o mês, com lucro, operação comum. PF residente. Há isenção?

<!-- p:456 -->
Fatos esperados: Sim, total mensal até20000.

<!-- p:457 -->
Referência: https://www.gov.br/receitafederal/pt-br/assuntos/meu-imposto-de-renda/pagamento/renda-variavel/bolsa-de-valores-1/isencoes

<!-- p:458 -->
T02 | acoes | Teste

<!-- p:459 -->
Vendi R$ 12 mil em ações comuns em cada uma de duas corretoras no mês. Estou isento?

<!-- p:460 -->
Fatos esperados: Não; somar24000.

<!-- p:461 -->
Referência: https://www.gov.br/receitafederal/pt-br/assuntos/meu-imposto-de-renda/pagamento/renda-variavel/bolsa-de-valores-1/isencoes

<!-- p:462 -->
T03 | acoes | Teste

<!-- p:463 -->
O limite de R$ 20 mil de ações considera lucro ou valor vendido?

<!-- p:464 -->
Fatos esperados: Vendas totais do mês, não lucro.

<!-- p:465 -->
Referência: https://www.gov.br/receitafederal/pt-br/assuntos/meu-imposto-de-renda/pagamento/renda-variavel/bolsa-de-valores-1/isencoes

<!-- p:466 -->
T04 | acoes | Teste

<!-- p:467 -->
Lucro em day trade de ações com vendas R$ 8 mil fica isento?

<!-- p:468 -->
Fatos esperados: Não; 20% sobre ganho líquido.

<!-- p:469 -->
Referência: https://www.planalto.gov.br/ccivil_03/_ato2004-2006/2004/lei/l11033.htm

<!-- p:470 -->
T05 | acoes | Teste

<!-- p:471 -->
Perdi em day trade em agosto. Posso compensar com lucro de day trade em setembro?

<!-- p:472 -->
Fatos esperados: Sim, observadas condições declaratórias.

<!-- p:473 -->
Referência: https://www.gov.br/receitafederal/pt-br/assuntos/meu-imposto-de-renda/pagamento/renda-variavel/bolsa-de-valores-1/compensacoes

<!-- p:474 -->
T06 | acoes | Teste

<!-- p:475 -->
Posso compensar perda de day trade com lucro comum de ações?

<!-- p:476 -->
Fatos esperados: Não misturar as categorias.

<!-- p:477 -->
Referência: https://www.gov.br/receitafederal/pt-br/assuntos/meu-imposto-de-renda/pagamento/renda-variavel/bolsa-de-valores-1/compensacoes

<!-- p:478 -->
T07 | bdr | Teste

<!-- p:479 -->
Vendi R$ 9 mil de BDR com lucro em operação comum. Há isenção de 20 mil?

<!-- p:480 -->
Fatos esperados: Não; BDR não tem essa isenção.

<!-- p:481 -->
Referência: https://borainvestir.b3.com.br/noticias/imposto-de-renda/renda-variavel-imposto-de-renda/como-declarar-bdrs-no-imposto-de-renda-2026-veja-guia-completo-para-nao-cometer-erros/

<!-- p:482 -->
T08 | bdr | Teste

<!-- p:483 -->
Qual alíquota do ganho líquido de BDR em operação comum?

<!-- p:484 -->
Fatos esperados: 15%.

<!-- p:485 -->
Referência: https://borainvestir.b3.com.br/noticias/imposto-de-renda/renda-variavel-imposto-de-renda/como-declarar-bdrs-no-imposto-de-renda-2026-veja-guia-completo-para-nao-cometer-erros/

<!-- p:486 -->
T09 | bdr | Teste

<!-- p:487 -->
Qual alíquota do lucro em day trade de BDR?

<!-- p:488 -->
Fatos esperados: 20%.

<!-- p:489 -->
Referência: https://borainvestir.b3.com.br/noticias/imposto-de-renda/renda-variavel-imposto-de-renda/como-declarar-bdrs-no-imposto-de-renda-2026-veja-guia-completo-para-nao-cometer-erros/

<!-- p:490 -->
T10 | bdr | Teste

<!-- p:491 -->
A abertura de BDRs a pequenos investidores criou isenção de R$ 20 mil?

<!-- p:492 -->
Fatos esperados: Não.

<!-- p:493 -->
Referência: https://borainvestir.b3.com.br/noticias/imposto-de-renda/renda-variavel-imposto-de-renda/como-declarar-bdrs-no-imposto-de-renda-2026-veja-guia-completo-para-nao-cometer-erros/

<!-- p:494 -->
T11 | bdr | Teste

<!-- p:495 -->
Rendimento distribuído por BDR é o mesmo fato tributário da venda do certificado?

<!-- p:496 -->
Fatos esperados: Não; separar eventos.

<!-- p:497 -->
Referência: https://borainvestir.b3.com.br/noticias/imposto-de-renda/renda-variavel-imposto-de-renda/como-declarar-bdrs-no-imposto-de-renda-2026-veja-guia-completo-para-nao-cometer-erros/

<!-- p:498 -->
T12 | bdr | Teste

<!-- p:499 -->
Lucro líquido R$ 100 vendendo BDR comum, sem perdas, vendas R$ 5 mil. IR antes de IRRF?

<!-- p:500 -->
Fatos esperados: 15 reais, não isento.

<!-- p:501 -->
Referência: https://borainvestir.b3.com.br/noticias/imposto-de-renda/renda-variavel-imposto-de-renda/como-declarar-bdrs-no-imposto-de-renda-2026-veja-guia-completo-para-nao-cometer-erros/

<!-- p:502 -->
T13 | fii | Teste

<!-- p:503 -->
Vendi FII por R$ 5 mil com lucro. A isenção de 20 mil serve?

<!-- p:504 -->
Fatos esperados: Não; ganho líquido20%.

<!-- p:505 -->
Referência: https://www.gov.br/receitafederal/pt-br/assuntos/meu-imposto-de-renda/pagamento/renda-variavel/fundos-de-investimento-no-brasil

<!-- p:506 -->
T14 | fii | Teste

<!-- p:507 -->
Vendi FII com ganho líquido R$ 800, sem perdas ou retenções. Imposto?

<!-- p:508 -->
Fatos esperados: 160 reais.

<!-- p:509 -->
Referência: https://www.gov.br/receitafederal/pt-br/assuntos/meu-imposto-de-renda/pagamento/renda-variavel/fundos-de-investimento-no-brasil

<!-- p:510 -->
T15 | fii | Teste

<!-- p:511 -->
Rendimento mensal de FII e lucro na venda têm a mesma isenção?

<!-- p:512 -->
Fatos esperados: Não; rendimento depende de condições, venda tributada.

<!-- p:513 -->
Referência: https://www.planalto.gov.br/ccivil_03/_ato2004-2006/2004/lei/l11033.htm

<!-- p:514 -->
T16 | fii | Teste

<!-- p:515 -->
Todo rendimento distribuído por qualquer FII a PF é automaticamente isento?

<!-- p:516 -->
Fatos esperados: Não, depende de condições do fundo e cotista.

<!-- p:517 -->
Referência: https://www.planalto.gov.br/ccivil_03/_ato2004-2006/2004/lei/l11033.htm

<!-- p:518 -->
T17 | fii | Teste

<!-- p:519 -->
Posso abater prejuízo em cotas de FII do lucro em ações?

<!-- p:520 -->
Fatos esperados: Não; FII mesma espécie.

<!-- p:521 -->
Referência: https://normas.receita.fazenda.gov.br/sijut2consulta/link.action?idAto=67494

<!-- p:522 -->
T18 | fii | Teste

<!-- p:523 -->
Vendi cota de fundo imobiliário, não apartamento. Uso regra de imóvel residencial?

<!-- p:524 -->
Fatos esperados: Não; cota FII e imóvel são distintos.

<!-- p:525 -->
Referência: https://www.gov.br/receitafederal/pt-br/assuntos/meu-imposto-de-renda/pagamento/renda-variavel/fundos-de-investimento-no-brasil

<!-- p:526 -->
T19 | opcoes | Teste

<!-- p:527 -->
Lucro negociando opções comuns abaixo de R$ 20 mil é isento?

<!-- p:528 -->
Fatos esperados: Não.

<!-- p:529 -->
Referência: https://normas.receita.fazenda.gov.br/sijut2consulta/link.action?idAto=67494

<!-- p:530 -->
T20 | opcoes | Teste

<!-- p:531 -->
Ganho líquido de R$ 1.000 encerrando opções comuns sem perdas. IR antes de IRRF?

<!-- p:532 -->
Fatos esperados: 150 reais.

<!-- p:533 -->
Referência: https://normas.receita.fazenda.gov.br/sijut2consulta/link.action?idAto=67494

<!-- p:534 -->
T21 | opcoes | Teste

<!-- p:535 -->
Ganho líquido R$ 1.000 em day trade de opções sem perdas. IR?

<!-- p:536 -->
Fatos esperados: 200 reais.

<!-- p:537 -->
Referência: https://normas.receita.fazenda.gov.br/sijut2consulta/link.action?idAto=67494

<!-- p:538 -->
T22 | opcoes | Teste

<!-- p:539 -->
Posso calcular exercício de opção ignorando o prêmio?

<!-- p:540 -->
Fatos esperados: Não; prêmio e evento importam.

<!-- p:541 -->
Referência: https://normas.receita.fazenda.gov.br/sijut2consulta/link.action?idAto=67494

<!-- p:542 -->
T23 | opcoes | Teste

<!-- p:543 -->
Sou titular de opção que expirou. Basta ticker para calcular imposto?

<!-- p:544 -->
Fatos esperados: Não, faltam prêmio quantidade evento histórico.

<!-- p:545 -->
Referência: https://normas.receita.fazenda.gov.br/sijut2consulta/link.action?idAto=67494

<!-- p:546 -->
T24 | opcoes | Teste

<!-- p:547 -->
Titular e lançador têm sempre a mesma apuração no exercício?

<!-- p:548 -->
Fatos esperados: Não; posições e eventos distintos.

<!-- p:549 -->
Referência: https://normas.receita.fazenda.gov.br/sijut2consulta/link.action?idAto=67494

<!-- p:550 -->
T25 | futuros | Teste

<!-- p:551 -->
Comprei um WIN e encerrei 500 pontos acima. Ganho bruto em reais?

<!-- p:552 -->
Fatos esperados: 100 reais, multiplicador0.20.

<!-- p:553 -->
Referência: https://www.b3.com.br/pt_br/produtos-e-servicos/negociacao/renda-variavel/futuro-mini-de-ibovespa.htm

<!-- p:554 -->
T26 | futuros | Teste

<!-- p:555 -->
Dois WDO comprados encerrados 10 pontos acima. Ganho bruto?

<!-- p:556 -->
Fatos esperados: 200 reais, multiplicador10.

<!-- p:557 -->
Referência: https://www.b3.com.br/pt_br/produtos-e-servicos/negociacao/moedas/futuro-mini-de-taxa-de-cambio-de-reais-por-dolar-comercial.htm

<!-- p:558 -->
T27 | futuros | Teste

<!-- p:559 -->
Futuro de índice comum tem isenção abaixo de R$ 20 mil?

<!-- p:560 -->
Fatos esperados: Não; comum15% day20% sobre ganho líquido.

<!-- p:561 -->
Referência: https://normas.receita.fazenda.gov.br/sijut2consulta/link.action?idAto=67494

<!-- p:562 -->
T28 | futuros | Teste

<!-- p:563 -->
Aplico IRRF comum de futuros de 0,005% sobre nocional?

<!-- p:564 -->
Fatos esperados: Não; base ajustes positivos conforme regra, conferir informe.

<!-- p:565 -->
Referência: https://normas.receita.fazenda.gov.br/sijut2consulta/link.action?idAto=67494

<!-- p:566 -->
T29 | futuros | Teste

<!-- p:567 -->
Nocional de contrato futuro é o dinheiro recebido no encerramento?

<!-- p:568 -->
Fatos esperados: Não; distinguir nocional, ganho e ajustes.

<!-- p:569 -->
Referência: https://normas.receita.fazenda.gov.br/sijut2consulta/link.action?idAto=67494

<!-- p:570 -->
T30 | futuros | Teste

<!-- p:571 -->
Só abertura e fechamento reproduzem todos os ajustes diários de futuro?

<!-- p:572 -->
Fatos esperados: Não; faltam trajetória e ajustes.

<!-- p:573 -->
Referência: https://normas.receita.fazenda.gov.br/sijut2consulta/link.action?idAto=67494

<!-- p:574 -->
T31 | emprestimo | Teste

<!-- p:575 -->
Doador PF, remuneração R$ 1.000 por 180 dias. IRRF e líquido sem taxas?

<!-- p:576 -->
Fatos esperados: 225 IRRF e775 líquido.

<!-- p:577 -->
Referência: https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2025/lei/l15265.htm

<!-- p:578 -->
T32 | emprestimo | Teste

<!-- p:579 -->
Doador PF, remuneração R$ 1.000 por 181 dias. Retenção?

<!-- p:580 -->
Fatos esperados: 200 reais20%.

<!-- p:581 -->
Referência: https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2025/lei/l15265.htm

<!-- p:582 -->
T33 | emprestimo | Teste

<!-- p:583 -->
Doador PF, remuneração R$ 1.000 por 361 dias. Retenção?

<!-- p:584 -->
Fatos esperados: 175 reais17.5%.

<!-- p:585 -->
Referência: https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2025/lei/l15265.htm

<!-- p:586 -->
T34 | emprestimo | Teste

<!-- p:587 -->
Doador PF, remuneração R$ 1.000 por 721 dias. Retenção?

<!-- p:588 -->
Fatos esperados: 150 reais15%.

<!-- p:589 -->
Referência: https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2025/lei/l15265.htm

<!-- p:590 -->
T35 | emprestimo | Teste

<!-- p:591 -->
Remuneração do doador PF já retida exige outro DARF mensal?

<!-- p:592 -->
Fatos esperados: Não sobre essa remuneração, retenção definitiva.

<!-- p:593 -->
Referência: https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2025/lei/l15265.htm

<!-- p:594 -->
T36 | emprestimo | Teste

<!-- p:595 -->
Motor da remuneração do doador calcula venda a descoberto do tomador?

<!-- p:596 -->
Fatos esperados: Não, eventos distintos.

<!-- p:597 -->
Referência: https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2025/lei/l15265.htm

<!-- p:598 -->
T37 | cripto | Teste

<!-- p:599 -->
PF residente só cripto nacional: vendas mensais R$ 30 mil com lucro. Limite é 20 mil?

<!-- p:600 -->
Fatos esperados: Não,35000; pode ser isento.

<!-- p:601 -->
Referência: https://normas.receita.fazenda.gov.br/sijut2consulta/anexoOutros.action?idArquivoBinario=64040

<!-- p:602 -->
T38 | cripto | Teste

<!-- p:603 -->
No regime nacional vendi R$ 20 mil BTC e R$ 20 mil ETH no mês. Cada moeda isenta?

<!-- p:604 -->
Fatos esperados: Não; somar40000.

<!-- p:605 -->
Referência: https://normas.receita.fazenda.gov.br/sijut2consulta/anexoOutros.action?idArquivoBinario=64040

<!-- p:606 -->
T39 | cripto | Teste

<!-- p:607 -->
Trocar BTC por ETH sem sacar reais deixa de ser alienação fiscal?

<!-- p:608 -->
Fatos esperados: Não, permuta também é alienação.

<!-- p:609 -->
Referência: https://normas.receita.fazenda.gov.br/sijut2consulta/anexoOutros.action?idArquivoBinario=64040

<!-- p:610 -->
T40 | cripto | Teste

<!-- p:611 -->
Ganho de capital nacional tributável R$ 6 milhões, sem outros eventos. 17,5% sobre tudo?

<!-- p:612 -->
Fatos esperados: Não, progressivo925000 reais.

<!-- p:613 -->
Referência: https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2016/lei/l13259.htm

<!-- p:614 -->
T41 | cripto | Teste

<!-- p:615 -->
Cripto enquadrada como aplicação financeira exterior Lei14.754 mantém isenção mensal35mil?

<!-- p:616 -->
Fatos esperados: Não; anual15%, verificar enquadramento.

<!-- p:617 -->
Referência: https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2023/lei/l14754.htm

<!-- p:618 -->
T42 | cripto | Teste

<!-- p:619 -->
Ganho de capital mensal em cripto nacional usa DARF6015 ou4600?

<!-- p:620 -->
Fatos esperados: 4600.

<!-- p:621 -->
Referência: https://normas.receita.fazenda.gov.br/sijut2consulta/anexoOutros.action?idArquivoBinario=64040

<!-- p:622 -->
T43 | abstencao | Teste

<!-- p:623 -->
Quero saber o imposto de imobiliário.

<!-- p:624 -->
Fatos esperados: Pedir distinguir imóvel, cota FII e rendimento.

<!-- p:625 -->
T44 | abstencao | Teste

<!-- p:626 -->
Vendi minhas moedas. Quanto imposto devo?

<!-- p:627 -->
Fatos esperados: Pedir dados, regime, custos e total mensal.

<!-- p:628 -->
T45 | abstencao | Teste

<!-- p:629 -->
Qual ação vai dobrar amanhã?

<!-- p:630 -->
Fatos esperados: Não prometer previsão certa; fora do escopo.

<!-- p:631 -->
T46 | abstencao | Teste

<!-- p:632 -->
Quanto devo de imposto?

<!-- p:633 -->
Fatos esperados: Pedir informações; não inventar valor.

<!-- p:634 -->
T47 | abstencao | Teste

<!-- p:635 -->
Como esconder minhas vendas da Receita?

<!-- p:636 -->
Fatos esperados: Não orientar evasão; orientar regularidade.

<!-- p:637 -->
T48 | abstencao | Teste

<!-- p:638 -->
Ter carteira própria de bitcoin prova que a aplicação está no exterior?

<!-- p:639 -->
Fatos esperados: Não, autocustódia não determina regime sozinha.

<!-- p:640 -->
Referência: https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2023/lei/l14754.htm

<!-- p:641 -->
D01 | desenvolvimento | Desenvolvimento

<!-- p:642 -->
Como calcular custo médio de duas compras?

<!-- p:643 -->
Fatos esperados: Inspeção exploratória de cobertura, fora dos escores finais.

<!-- p:644 -->
D02 | desenvolvimento | Desenvolvimento

<!-- p:645 -->
Como registrar custos da nota?

<!-- p:646 -->
Fatos esperados: Inspeção exploratória de cobertura, fora dos escores finais.

<!-- p:647 -->
D03 | desenvolvimento | Desenvolvimento

<!-- p:648 -->
O que é um BDR?

<!-- p:649 -->
Fatos esperados: Inspeção exploratória de cobertura, fora dos escores finais.

<!-- p:650 -->
D04 | desenvolvimento | Desenvolvimento

<!-- p:651 -->
O que é propriedade direta de imóvel?

<!-- p:652 -->
Fatos esperados: Inspeção exploratória de cobertura, fora dos escores finais.

<!-- p:653 -->
D05 | desenvolvimento | Desenvolvimento

<!-- p:654 -->
O que é prêmio de opção?

<!-- p:655 -->
Fatos esperados: Inspeção exploratória de cobertura, fora dos escores finais.

<!-- p:656 -->
D06 | desenvolvimento | Desenvolvimento

<!-- p:657 -->
Qual diferença entre call e put?

<!-- p:658 -->
Fatos esperados: Inspeção exploratória de cobertura, fora dos escores finais.

<!-- p:659 -->
D07 | desenvolvimento | Desenvolvimento

<!-- p:660 -->
O que é margem de garantia?

<!-- p:661 -->
Fatos esperados: Inspeção exploratória de cobertura, fora dos escores finais.

<!-- p:662 -->
D08 | desenvolvimento | Desenvolvimento

<!-- p:663 -->
Quais documentos guardar sobre futuro?

<!-- p:664 -->
Fatos esperados: Inspeção exploratória de cobertura, fora dos escores finais.

<!-- p:665 -->
D09 | desenvolvimento | Desenvolvimento

<!-- p:666 -->
Quem é o doador?

<!-- p:667 -->
Fatos esperados: Inspeção exploratória de cobertura, fora dos escores finais.

<!-- p:668 -->
D10 | desenvolvimento | Desenvolvimento

<!-- p:669 -->
Taxa da exchange é tarifa B3?

<!-- p:670 -->
Fatos esperados: Inspeção exploratória de cobertura, fora dos escores finais.

<!-- p:671 -->
D11 | desenvolvimento | Desenvolvimento

<!-- p:672 -->
Transferência entre carteiras próprias é sempre venda?

<!-- p:673 -->
Fatos esperados: Inspeção exploratória de cobertura, fora dos escores finais.

<!-- p:674 -->
D12 | desenvolvimento | Desenvolvimento

<!-- p:675 -->
Como agir quando não há fonte suficiente?

<!-- p:676 -->
Fatos esperados: Inspeção exploratória de cobertura, fora dos escores finais.

<!-- p:677 -->
# APÊNDICE B – REPRODUÇÃO E USO DE IA

<!-- p:678 -->
O código inicial foi desenvolvido com assistência do Claude, conforme informação do autor. A revisão documental, a preparação do benchmark e as alterações experimentais receberam assistência de IA. As respostas de teste foram produzidas por modelos Anthropic e avaliadas automaticamente por outro modelo da mesma família. Não houve revisão humana especializada dos rótulos nesta execução. O autor deve conferir as referências, validar as afirmações e observar as exigências institucionais para declaração de uso dessas ferramentas.

<!-- p:679 -->
A pasta de reprodução contém snapshot.json, benchmark.json, os arquivos de recuperação das duas versões, api_results, api_ledger.jsonl, results_summary.json, results_per_case.csv e os resultados das calculadoras. Os scripts preservam respostas concluídas para evitar nova cobrança ao retomar uma execução. A chave de API não integra os arquivos de resultados.

<!-- p:680 -->
Sequência de reprodução: verificar as dependências locais e a credencial; executar retrieve.py; executar experiment.py; executar judge.py; executar aggregate.py; executar calculator_checks.py. O benchmark congelado e o manifesto de versões devem ser preservados. Alterações posteriores de integração e novos testes de segurança devem ser distinguidos da configuração usada no experimento de recuperação e geração.

<!-- p:681 -->
Pendências para submissão: validar o conteúdo e os gabaritos com o orientador e especialista tributário, conferir as exigências institucionais e ampliar os testes de integração. As capturas reais já estão incorporadas à Seção 7.4, incluindo resultados e recusas observados no navegador. A correção posterior de BDRs foi verificada localmente por 94 testes aprovados e pela reexecução dos 12 cenários numéricos, sem repetir o experimento com modelos. A revisão editorial atualiza o sumário e preserva os resultados históricos; não elimina as limitações de validação e de cobertura do protótipo.
