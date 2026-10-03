# Perguntas e respostas para a defesa do TCC

Assistente inteligente para apoio em tributação e regulação no mercado financeiro brasileiro

Revisão de 22 de setembro de 2026. Este roteiro reúne 120 perguntas com respostas sugeridas para apresentação oral. Foi conferido contra o código disponível e o manuscrito da monografia. Não é um novo benchmark nem um registro de respostas produzidas pela aplicação. Os números experimentais citados pertencem às avaliações documentadas; não houve nova execução dessas avaliações para preparar este roteiro.

Use as respostas como apoio, não como texto para decorar. Nas perguntas de justificativa, adote a formulação apenas se ela representar sua decisão e sua compreensão do trabalho. As descrições de regras e produtos delimitam a implementação estudada, não constituem orientação tributária atualizada para operações reais.

## 1. Apresentação do trabalho

### 1. Como você explica seu TCC em um minuto?

Desenvolvi e avaliei um protótipo que combina consulta a uma base documental, interpretação de linguagem natural e cálculos programados para apoiar dúvidas sobre o mercado financeiro brasileiro. O usuário pode fazer perguntas e informar operações. O trabalho avalia separadamente a recuperação de informações, as respostas geradas e os cálculos, mostrando tanto os resultados favoráveis quanto as limitações encontradas.

### 2. Qual problema o projeto procura resolver?

As informações necessárias para compreender uma operação estão distribuídas entre documentos, orientações e regras de diferentes produtos. O protótipo procura facilitar o acesso a essas informações e conectar explicações a cálculos verificáveis. Ele não pretende realizar sozinho toda a apuração fiscal do investidor.

### 3. Qual é a pergunta de pesquisa?

Em que medida a combinação de recuperação de evidências e cálculo determinístico pode apoiar respostas tributárias verificáveis, e quais erros permanecem observáveis em um conjunto controlado de consultas? A pergunta exige avaliar os resultados, e não apenas demonstrar uma interface funcionando.

### 4. Qual é a principal contribuição?

A contribuição é a integração e a avaliação aplicada em um domínio sensível. O trabalho não propõe um novo modelo de linguagem nem um novo algoritmo de busca. Ele mostra como combinar componentes existentes, verificar suas saídas e identificar falhas que não seriam percebidas olhando apenas para a fluência da resposta.

### 5. Para quem o protótipo foi pensado?

Para apoiar pessoas físicas em dúvidas e exemplos de operações dentro do escopo estudado. A interface procura reduzir a dificuldade de fornecer dados e interpretar resultados. Não é uma plataforma validada para contadores, instituições financeiras ou uso fiscal autônomo.

### 6. O projeto atingiu o objetivo?

Demonstrou a viabilidade da abordagem no conjunto avaliado: reuniu recuperação documental, cálculos e explicações, e apresentou melhoria após a revisão do corpus. Isso não significa que toda pergunta seja atendida corretamente. As limitações de memória, carteira, atualização normativa e validação independente delimitam o resultado.

### 7. Por que escolher o mercado financeiro brasileiro?

É um domínio em que produtos semelhantes podem ter tratamentos distintos, e uma explicação imprecisa pode produzir uma conclusão inadequada. Também permite trabalhar com fontes institucionais brasileiras. O recorte torna possível avaliar erros concretos de enquadramento e cálculo, em vez de apenas a qualidade aparente do texto.

### 8. Qual é o escopo de produtos?

O protótipo possui tratamento para ações, BDRs, FIIs, opções, futuros de índice e dólar, empréstimo de ações e criptoativos. Essa lista não significa cobertura integral de cada mercado. Os futuros estão restritos a WIN e WDO, opções têm tratamento simplificado e o motor de cripto não cobre todos os enquadramentos possíveis.

## 2. Arquitetura e fluxo

### 9. Quais são os principais componentes?

A interface usa Angular e se comunica com uma API FastAPI. O backend contém o orquestrador e os agentes especialistas, integra modelos de linguagem e acessa as ferramentas de cálculo por MCP. SQLite guarda operações e mensagens; ChromaDB guarda os trechos usados na recuperação documental.

### 10. O que acontece quando o usuário envia uma mensagem?

O orquestrador solicita a classificação da intenção. Quando reconhece uma categoria de ativo, encaminha a mensagem ao especialista e tenta extrair uma operação. Uma compra extraída é registrada; uma venda suficientemente estruturada pode entrar no ciclo de ferramentas. Sem operação extraída, o sistema pode responder à pergunta com apoio documental.

### 11. Toda pergunta usa o MCP?

Não. Perguntas conceituais podem ser respondidas pelo fluxo de recuperação e geração, sem cálculo. O MCP participa do caminho de cálculo; registrar uma compra também não exige calcular imposto de venda. É importante demonstrar essas diferenças, em vez de apresentar o MCP como uma etapa obrigatória de todas as mensagens.

### 12. O que faz o orquestrador?

Ele coordena o encaminhamento da solicitação. Usa a classificação produzida pelo modelo para escolher um especialista ou o caminho consultivo geral. Não é o componente que implementa as fórmulas financeiras e não deve ser confundido com o servidor MCP.

### 13. Os especialistas são modelos de IA diferentes?

Não necessariamente. São componentes de software com escopos e instruções específicos, que podem utilizar os mesmos modelos configurados. A especialização está no encaminhamento e nas instruções; não significa que cada classe tenha sido treinada como um modelo independente.

### 14. Os agentes debatem entre si para produzir a resposta?

Não no fluxo implementado. Há um orquestrador que encaminha a solicitação a um especialista. Não há uma discussão entre vários agentes seguida de votação ou consenso. Portanto, não apresento a arquitetura como uma sociedade de agentes autônomos.

### 15. Por que separar classificação, cálculo e explicação?

São tarefas diferentes. Classificar identifica o caminho, extrair transforma a mensagem em dados, calcular executa regras e explicar apresenta o resultado. Essa separação ajuda a investigar um erro: um cálculo pode estar correto para dados que foram extraídos incorretamente.

### 16. Quais modelos são utilizados?

O código configura modelos para classificação e extração, e outro para explicações e respostas. Os valores padrão estão em `backend/app/core/config.py` e podem ser substituídos pela configuração do ambiente. Para descrever um experimento, uso os identificadores registrados na evidência daquela execução, não presumo que a configuração atual seja a histórica.

### 17. O formulário e o chat executam exatamente o mesmo fluxo?

Não. O formulário já recebe campos estruturados e o backend determina as chamadas MCP. No chat, há interpretação da linguagem natural e, para uma venda extraída, o modelo seleciona ferramentas dentro de um ciclo controlado. Ambos reutilizam o servidor e as calculadoras, mas os riscos de extração e explicação são diferentes.

### 18. Uma explicação convincente prova que o fluxo funcionou?

Não. É necessário conferir os campos extraídos, as chamadas de ferramentas, o resultado estruturado e a persistência. O modelo pode explicar bem uma operação diferente da solicitada ou descrever incorretamente o que foi gravado. Por isso, a demonstração deve incluir evidências além da mensagem final.

## 3. MCP e ferramentas

### 19. O que é MCP neste projeto?

É o protocolo utilizado para expor e chamar ferramentas de cálculo com um contrato estruturado. O backend atua como cliente e inicia um servidor local por subprocesso. MCP não é o modelo de linguagem, não é o banco de dados e não contém, por si só, as regras financeiras.

### 20. Qual servidor MCP está em uso?

O ponto de entrada utilizado é `mcp_server/server.py`, referenciado pelo gateway. Ele expõe `fee_policy` e `calculate_trade`. O roteiro anterior descrevia uma organização antiga com outro arquivo de execução; essa descrição não corresponde ao caminho atual.

### 21. A IA escolhe as ferramentas hoje?

Sim, no ciclo de ferramentas do chat para uma operação já extraída. O modelo solicita chamadas e recebe os resultados antes de elaborar a explicação. No formulário estruturado, a sequência é determinada pelo backend. Portanto, a resposta depende de qual entrada da aplicação estamos descrevendo.

### 22. Essa escolha é totalmente autônoma?

Não. O backend fixa a operação e o usuário, valida argumentos e impõe pré-condições e limites. O modelo não pode substituir livremente os dados financeiros por novos argumentos. A autonomia consiste em selecionar ferramentas permitidas dentro de uma tarefa delimitada.

### 23. Quais ferramentas o modelo pode selecionar no chat?

Ele recebe `fee_policy`, `calculate_trade` e `consultar_preco_medio`. As duas primeiras são encaminhadas ao servidor MCP. A terceira é executada localmente pelo backend, com acesso somente de leitura ao custo do ativo para o usuário da requisição. Nem toda ferramenta oferecida ao modelo é uma ferramenta remota MCP.

### 24. Como o modelo pede uma ferramenta sem escolher os argumentos financeiros?

As ferramentas apresentadas ao modelo usam um esquema de entrada vazio nesse fluxo. Ao receber a solicitação, o backend acrescenta os dados da operação previamente extraída. Essa escolha reduz a possibilidade de o modelo alterar quantidade, ativo ou identidade durante o cálculo, mas também restringe a flexibilidade da conversa.

### 25. Para que serve `fee_policy`?

Ela informa a política de custos e suas ressalvas. Não consulta uma tabela de tarifas atualizada da B3. O retorno informa que custos fornecidos pelo usuário são preferidos e que eventuais tarifas parametrizadas são estimativas legadas, sem vigência validada.

### 26. O MCP calcula ou apenas repassa uma pergunta para outra IA?

Neste projeto, o servidor valida a entrada e executa classes Python de cálculo. Ele não precisa consultar outro modelo para fazer a aritmética. O modelo de linguagem participa da escolha de ferramentas e da explicação, enquanto o cálculo é executado por código.

### 27. Por que não chamar diretamente a função Python?

Uma chamada direta seria mais simples e teria menos custo de comunicação. MCP foi usado para separar a interface de ferramentas do cliente e permitir reutilização por clientes compatíveis. O benefício é arquitetural; o protocolo não torna uma fórmula mais correta nem demonstra sozinho uma vantagem de desempenho.

### 28. Qual transporte é utilizado?

O servidor é local e usa entrada e saída padrão, ou `stdio`, em um subprocesso Python. Não é um serviço HTTP público. Isso explica por que a instalação precisa disponibilizar o arquivo do servidor e suas dependências ao processo que atende a aplicação.

### 29. Como evitar que o modelo entre em um ciclo infinito de chamadas?

O ciclo do chat possui limites explícitos: seis rodadas e oito chamadas de ferramenta. Também verifica identificadores de chamadas, argumentos e estados de término. Ao atingir um limite ou encontrar uma resposta inválida, o fluxo deve recusar a conclusão do cálculo.

### 30. O que acontece se o MCP falhar?

O sistema não deve apresentar um cálculo alternativo silencioso como se a ferramenta tivesse funcionado. O gateway converte falhas em erro e não possui fallback para chamar diretamente a calculadora. No chat, erros de validação são recuperados também de exceções agrupadas, para preservar uma explicação útil sobre dados faltantes.

### 31. O servidor MCP grava a venda?

Não. O servidor calcula e devolve dados. No fluxo do chat, o agente do backend grava a venda após receber um cálculo concluído. Essa distinção é essencial: dizer que a ferramenta não grava não significa que a solicitação inteira seja somente de leitura.

### 32. O problema antigo de bloqueio do chat continua igual?

O código atual declara a rota do chat como função síncrona, diferente da rota assíncrona que chamava processamento síncrono no achado histórico. Assim, não é correto repetir o diagnóstico antigo como descrição literal da implementação atual. Os ensaios posteriores e suas condições devem ser consultados; isso não substitui um estudo de carga com modelos reais.

## 4. RAG e base documental

### 33. O que é RAG, de forma simples?

É recuperar conteúdo relevante de uma base e fornecer esse conteúdo ao modelo para apoiar a resposta. No projeto, isso permite associar a geração a trechos identificados por origem. Não significa que o modelo esteja pesquisando toda a internet a cada pergunta.

### 34. Por que usar RAG em vez de confiar apenas no conhecimento do modelo?

Porque o conhecimento interno do modelo não oferece, sozinho, uma evidência verificável para cada afirmação. A recuperação permite examinar quais trechos foram disponibilizados. Mesmo assim, o modelo pode interpretar mal o contexto ou responder além dele; RAG reduz alguns riscos, mas não garante correção.

### 35. Qual é a diferença entre RAG e treinamento do modelo?

No RAG, fornecemos documentos no contexto da solicitação sem alterar os parâmetros do modelo. Treinar ou ajustar um modelo envolve modificar esses parâmetros. O projeto não realizou um novo treinamento do modelo de linguagem para memorizar a legislação brasileira.

### 36. Como está organizada a base revisada?

Ela contém 18 trechos curados, definidos em `backend/app/vector_db/curated.py`, com identificador, texto, origem, categoria e data de consulta. São resumos selecionados para o experimento, não a íntegra de toda a legislação aplicável.

### 37. O que são embeddings?

São representações numéricas de textos usadas para comparar proximidade semântica. A pergunta e os trechos podem ser comparados nesse espaço vetorial. Proximidade não equivale a validade: duas frases sobre a mesma isenção podem ser próximas mesmo quando uma a afirma e a outra a nega.

### 38. Como os trechos são encontrados?

A implementação revisada utiliza ChromaDB, uma função de embedding padrão e uma coleção configurada para distância de cosseno. A consulta recupera os resultados mais próximos. Isso não é uma prova de que o primeiro trecho contém a regra correta para o caso do usuário.

### 39. Existe um filtro rígido por categoria de ativo?

Não na busca revisada. A função recebe `asset_type` por compatibilidade, mas o ranqueamento é global na coleção. Isso pode ajudar perguntas que comparam produtos, mas também pode trazer trechos de outro produto; é um compromisso que exige avaliação.

### 40. Quantos trechos vão para o modelo?

No caminho de venda extraída, o especialista solicita até dois trechos. Nos caminhos de pergunta sem operação extraída e consulta geral, solicita até três. O benchmark de recuperação considera os três primeiros resultados. Não há um único valor de `k` para todos os caminhos.

### 41. Por que apenas 18 trechos?

O conjunto pequeno permitiu revisar o conteúdo e analisar resultados de forma controlada. Em contrapartida, limita a diversidade de situações atendidas. Não é suficiente para afirmar que o sistema representa toda a regulação financeira ou que a busca funcionará da mesma forma em um corpus grande.

### 42. As informações são atualizadas automaticamente?

Não. A revisão depende de conferir as fontes, editar o corpus e carregá-lo novamente. A data de consulta de um trecho não é garantia de vigência normativa. Também não há resolução completa de conflitos entre versões históricas das regras.

### 43. Por que priorizar fontes brasileiras?

Porque a aplicação trata de um domínio brasileiro, no qual fontes institucionais locais são diretamente relevantes para regras e especificações. Isso não impede usar literatura internacional para RAG, modelos e avaliação. A origem deve ser adequada à afirmação, não escolhida apenas pelo idioma.

### 44. A B3 é a fonte de todas as regras tributárias?

Não. A B3 é relevante para produtos, contratos e funcionamento do mercado, enquanto regras tributárias exigem legislação e orientações das autoridades competentes. A base e a bibliografia devem preservar essa diferença de papel entre as fontes.

### 45. Mostrar um link prova que a resposta está fundamentada?

Não. É preciso verificar se a fonte sustenta aquela afirmação e se o trecho se aplica ao caso. Um link verdadeiro pode acompanhar uma conclusão que não está no documento. Por isso, fundamentação e correção são avaliadas, não presumidas pela presença de uma URL.

### 46. Existe um corte automático que rejeita trechos pouco semelhantes?

Não foi calibrado um limiar numérico de rejeição. O sistema possui instruções para lidar com falta de evidência, mas isso não equivale a um mecanismo de abstenção com desempenho conhecido. É uma limitação importante quando a base não cobre a pergunta.

## 5. Banco de dados e memória

### 47. Para que serve o SQLite?

Ele guarda compras, vendas, resultados associados e mensagens do chat. Os registros permitem exibir o histórico, consultar custo médio e alimentar a apuração mensal implementada. Guardar os dados não significa que a IA tenha acesso livre ou automático a todos eles.

### 48. Por que também existe o ChromaDB?

Porque os dois bancos resolvem problemas diferentes. SQLite organiza registros estruturados de operações; ChromaDB suporta a busca semântica dos trechos documentais. O texto de uma norma não é tratado da mesma forma que quantidade, preço e data de uma compra.

### 49. Como funciona o custo médio?

O repositório percorre as operações registradas em ordem de data e atualiza a média ponderada nas compras. Por exemplo, 100 unidades a R$ 20 e mais 100 a R$ 30 resultam em média de R$ 25 por unidade nesse algoritmo. Essa descrição não implica cobertura de todos os eventos corporativos ou ajustes fiscais de custo.

### 50. Registrar uma compra já gera imposto no protótipo?

A compra é persistida sem cálculo de imposto de venda. Ela deve aparecer no histórico e pode contribuir para o custo médio de uma venda posterior. Ausência de imposto calculado para a compra não significa ausência de registro.

### 51. Por que uma compra não aparece como venda no resumo mensal?

Porque o resumo tributário consulta vendas, enquanto o histórico agora lista compras e vendas. Em um mês só com compras, a interface informa que não existem vendas para apurar. Não é correto transformar a compra em uma linha de imposto apenas para preencher o resumo.

### 52. O que foi corrigido na identificação do usuário?

O frontend passou a centralizar `user123` no serviço de API e enviá-lo no chat, no formulário e nas consultas de histórico, resumo e DARF. Antes, alguns caminhos consultavam `default`. Essa correção de consistência não implementa login nem migra automaticamente registros antigos de outra identidade.

### 53. O sistema tem memória conversacional?

Não entre mensagens do usuário. O histórico é armazenado, mas não é recuperado nem sumarizado para construir a próxima solicitação ao modelo. Portanto, uma pergunta como “e se eu vender metade disso?” não pode contar com a compreensão da mensagem anterior.

### 54. Então o ciclo de ferramentas também não tem memória?

Dentro de uma única solicitação, o ciclo mantém as chamadas e os resultados de ferramentas em uma lista de mensagens. Isso permite ao modelo usar o resultado de uma ferramenta na próxima rodada daquela solicitação. É diferente de manter a conversa entre duas mensagens enviadas pelo usuário.

### 55. O histórico é apagado ao recarregar a tela?

A lista exibida pelo componente de chat é reiniciada, mas isso não significa que os registros tenham sido excluídos do SQLite. Existe uma rota de histórico de chat; a interface não a utiliza para reconstruir a conversa automaticamente. Memória visual, armazenamento e contexto enviado ao modelo são coisas distintas.

### 56. Por que “se eu vender meu saldo de PETR4” não consulta a carteira?

A ferramenta disponível consulta custo médio, não uma posição completa, e só é oferecida depois da extração de uma operação com dados suficientes. Uma pergunta incompleta pode seguir para resposta geral. O sistema ainda não possui o fluxo de buscar saldo, perguntar preço e data e continuar a simulação.

### 57. Como demonstrar a consulta de custo médio sem confundi-la com memória?

Em um ambiente de testes, registre uma compra e depois forneça uma venda completa do mesmo ativo e usuário, omitindo apenas o custo médio. Confira nos logs a seleção de `consultar_preco_medio` e o cálculo retornado. Recarregar a tela entre as etapas ajuda a mostrar que o dado vem do banco, não de uma conversa lembrada.

### 58. O sistema já distingue simular de registrar?

Não há separação explícita e segura entre esses propósitos no fluxo atual. Se a mensagem for extraída como venda e o cálculo terminar, o agente persiste a operação. Por isso, não apresento perguntas hipotéticas como uma funcionalidade de simulação sem efeitos sobre a carteira.

## 6. Cálculos e escopo financeiro

### 59. O que significa cálculo determinístico?

Para as mesmas entradas, parâmetros e versão do código, a calculadora deve produzir os mesmos resultados. O modelo não precisa improvisar a aritmética. Porém, uma fórmula incorreta também pode produzir o mesmo resultado errado em todas as execuções; determinismo não é certificação tributária.

### 60. A calculadora valida se a venda realmente ocorreu?

Não. Ela trabalha com os dados recebidos e as validações implementadas. Não consulta notas de corretagem ou uma confirmação da bolsa para provar a ocorrência da operação. Um cálculo correto sobre uma entrada fictícia continua sendo apenas o resultado daquela entrada.

### 61. Por que não assumir custo médio igual ao preço de venda quando falta informação?

Porque isso faria o ganho parecer zero sem fundamento nos registros. O protótipo passou a recusar a ausência de custo necessário, em vez de produzir um valor aparentemente válido. A recusa é um comportamento útil quando impede que falta de informação seja confundida com ausência de imposto.

### 62. FII e opções ainda têm a antiga falha de custo médio ausente?

A descrição do roteiro anterior ficou desatualizada. As correções posteriores adicionaram validação de custo médio e tratamento de custos nas calculadoras dessas categorias. Ao defender isso, devo apontar o código e os testes da revisão correspondente, sem apresentar um achado antigo como defeito necessariamente ainda ativo.

### 63. Por que não aplicar a mesma regra a todos os produtos?

Porque cada categoria exige verificar enquadramento, dados necessários e forma de cálculo. Um limite ou tratamento usado em ações não pode ser transferido automaticamente para outro produto. O benchmark inclui perguntas desenhadas para detectar justamente essas generalizações indevidas.

### 64. O sistema consolida toda a movimentação mensal automaticamente?

Não de forma completa. Existe um resumo das vendas registradas, mas campos como `total_vendas_mes` ainda dependem da informação fornecida pelo usuário no cálculo. Somar resultados persistidos não equivale a reconstruir toda a apuração fiscal entre corretoras, meses e categorias.

### 65. A classificação de day trade é inferida automaticamente?

Não há um mecanismo geral de conciliação de compras e vendas que determine corretamente todos esses casos. O modelo de entrada possui classificação informada, e o tratamento efetivo depende da calculadora. Não devo afirmar que o protótipo identifica day trade apenas porque existem datas no banco.

### 66. O que significa o campo `ganho_prejuizo_liquido`?

No fluxo documentado, representa o ganho após custos antes de IR, não necessariamente o ganho final após imposto. A palavra “líquido” pode induzir outra interpretação. As instruções do chat procuram explicitar essa diferença e evitar descontar imposto duas vezes na explicação.

### 67. O protótipo cobre todos os derivativos?

Não. Em futuros, cobre WIN e WDO com simplificações; também tem tratamento limitado de opções. Outros contratos, posições e eventos exigem regras e testes próprios. Essa restrição está registrada na seção de limitações, e a expansão aparece como trabalho futuro.

### 68. O cálculo de futuros reproduz todos os ajustes diários?

Não. O modelo simplificado não reconstrói toda a trajetória operacional de ajustes, posições vendidas e rolagens. Assim, a demonstração de uma diferença de preços de contrato não deve ser apresentada como escrituração completa de uma posição real.

### 69. O empréstimo de ações é tratado como uma venda comum?

O projeto inclui um cálculo específico para a remuneração do doador, mas a representação ainda compartilha campos com operações de compra e venda. Isso é uma limitação de modelagem. Não devo extrapolar esse cálculo para todas as situações do tomador, garantias e eventos do contrato.

### 70. Qual é o limite da cobertura de criptoativos?

O motor possui um recorte de cálculo nacional e recusa o enquadramento sinalizado como exterior. Essa recusa evita aplicar uma regra do recorte a um caso não coberto. Ela não demonstra que um simples campo booleano seja suficiente para classificar juridicamente qualquer criptoativo.

## 7. Avaliação e resultados

### 71. O que foi avaliado separadamente?

A recuperação de trechos, a qualidade das respostas, os cenários numéricos e o funcionamento técnico da integração. Cada avaliação responde a uma pergunta diferente. Um teste de transporte MCP aprovado não prova que o trecho recuperado é pertinente nem que a resposta está juridicamente correta.

### 72. Quantas perguntas compõem o benchmark?

São 60: 12 de desenvolvimento e 48 de teste. Das 48, 42 pertencem aos sete grupos factuais e seis tratam de ambiguidades ou situações fora de escopo. Os denominadores precisam acompanhar cada resultado; não é correto dizer apenas “acurácia em 60 perguntas”.

### 73. Por que separar desenvolvimento de teste?

Para não apresentar como avaliação final as mesmas perguntas usadas no ajuste exploratório. Essa separação reduz uma forma de favorecimento do resultado, mas não elimina todos os vieses. Como o conjunto é pequeno e produzido no contexto do desenvolvimento, a avaliação externa continua necessária.

### 74. O que significa Precision at 1?

Nesta avaliação, verifica se o primeiro trecho recuperado recebeu grau máximo de relevância, conforme a rubrica. A média indica em quantas consultas isso ocorreu. Mede a recuperação, não o percentual de respostas finais corretas.

### 75. Como explicar Precision at 3 com um exemplo?

Se dois dos três primeiros trechos têm grau máximo de relevância, P@3 daquela consulta é 2/3. Um terceiro trecho apenas parcialmente útil não entra como relevante pleno nessa definição. Um único trecho pode ser suficiente para responder, por isso essa métrica deve ser lida junto com as demais.

### 76. Para que serve nDCG@3?

Ela considera graus de relevância e a posição dos resultados, valorizando conteúdo mais relevante nas primeiras posições. No trabalho, a referência ideal foi construída com os trechos julgados em conjunto nas configurações comparadas. É uma nDCG agrupada, não uma avaliação exaustiva de todos os documentos possíveis.

### 77. Quem define se um trecho é relevante?

A definição vem da rubrica e dos julgamentos aplicados às perguntas. O trabalho usa graus de irrelevante, parcial e diretamente pertinente. A existência de uma rubrica torna o critério explícito, mas os julgamentos continuam sujeitos a erro e precisam de revisão especializada.

### 78. O que é LLM-as-a-Judge?

É usar um modelo para avaliar respostas segundo critérios explícitos, como correção e fundamentação. Ele ajuda a organizar uma avaliação repetível, mas não substitui um especialista tributário. Um modelo avaliador mais capaz também pode errar ou compartilhar vieses com o gerador.

### 79. Por que similaridade semântica não basta para avaliar uma resposta?

Uma resposta que afirma uma isenção e outra que a nega podem ser muito próximas semanticamente. Também é possível escrever uma resposta correta com palavras diferentes do gabarito. Por isso, proximidade textual não substitui verificar os fatos necessários e as condições de aplicação.

### 80. Quais foram os principais resultados das respostas?

No conjunto factual de 42 perguntas, o Sonnet com corpus inicial obteve 29 respostas consideradas corretas; com corpus revisado, 37; e o Haiku revisado, 30. A comparação sugere benefício da revisão naquele conjunto. Não prova o mesmo ganho em qualquer população de usuários ou na versão posterior do fluxo MCP.

### 81. O que aconteceu com as cinco respostas restantes do Sonnet revisado?

Elas não receberam classificação de plenamente corretas no critério utilizado. Isso não permite dizer que todas foram totalmente erradas, nem que eram apenas detalhes: os casos precisam ser examinados individualmente nos registros. Não ter marcações de erro crítico é diferente de ter todas as respostas completas e corretas.

### 82. A recuperação também melhorou?

P@1 passou de 52,4% para 57,1%, P@3 de 23,8% para 30,2% e nDCG@3 agrupada de 0,517 para 0,560. A melhora foi menor que a observada nas respostas. Não foi isolado experimentalmente o efeito de cada alteração do corpus, portanto evito atribuir toda a diferença a uma única causa.

### 83. Os resultados antigos valem automaticamente para a arquitetura atual?

Não. O benchmark e os testes posteriores representam momentos e condições diferentes. A integração MCP e o ciclo de ferramentas receberam verificações próprias, mas não equivalem à reexecução integral do benchmark de linguagem natural. Essa distinção precisa aparecer ao discutir a evolução do projeto.

### 84. Qual número de testes devo citar na defesa?

Devo citar a execução, a data e o escopo. A monografia registra 146 aprovações na rodada posterior de 20 de setembro; a correção de histórico de 21 de setembro foi verificada por 19 testes de API, testes isolados do frontend e compilação. Esses números não devem ser somados como se fossem testes distintos nem anunciados como uma suíte integral recém-executada.

## 8. Perguntas difíceis e demonstração

### 85. Se ainda existem limitações, por que o trabalho tem valor?

Porque um estudo aplicado precisa demonstrar o que funciona e delimitar o que não foi validado. O trabalho produziu uma integração executável e evidências separadas de recuperação, respostas e cálculo. Seu valor não depende de afirmar que o protótipo está pronto para uso fiscal em produção.

### 86. Se a IA ajudou no código, nos testes e no texto, qual é a responsabilidade do autor?

A assistência deve ser declarada, como no apêndice da monografia. A responsabilidade pela compreensão, seleção do método, conferência das afirmações e apresentação dos resultados permanece com o autor. Não devo alegar validação independente ou revisão manual que não tenha ocorrido, e devo conseguir explicar as decisões sem depender do texto gerado.

### 87. O identificador de usuário resolve a segurança dos dados?

Não. Ele permite separar consultas logicamente, mas é informado pela aplicação e não constitui autenticação ou autorização robusta. A identidade fixa usada no protótipo não é adequada a um serviço público multiusuário. Esse requisito precisaria ser implementado e testado antes de uma implantação real.

### 88. Como fazer uma demonstração segura da compra e venda de PETR4?

Use somente um banco de testes e confira previamente a identidade, o saldo e o mês selecionado. Registre 4.000 PETR4 a R$ 40 e forneça uma venda completa, com preço, data, classificação e demais dados exigidos, sem informar o custo médio. Mostre o histórico e os logs para verificar a consulta ao custo. Avise que a venda será registrada: a demonstração não é uma simulação sem persistência.

### 89. E se a demonstração ao vivo falhar?

Não devo inventar a saída nem substituir a evidência por uma resposta decorada. Posso explicar a falha observada, conferir os logs e apresentar uma captura de execução anterior claramente identificada como tal. Se faltar um dado, a recusa deve ser distinguida de uma indisponibilidade técnica ou erro de implementação.

### 90. Qual seria sua próxima prioridade?

Eu priorizaria revisão especializada das regras e dos gabaritos, seguida de uma separação explícita entre consulta, simulação e registro. Para o chat, isso inclui consulta de posição e coleta dos dados faltantes. Depois, ampliaria a avaliação de ponta a ponta e a cobertura de produtos, preservando testes e rastreabilidade das mudanças.

## 9. Casos práticos para explicar à banca

### 91. Comprei 4.000 PETR4 a R$ 40. Que informação já existe para uma venda futura?

O registro fornece ativo, quantidade, preço e data da compra, vinculados ao usuário. Considerando apenas essa compra, o algoritmo de custo médio encontra R$ 40 por ação. Ainda faltam os dados da venda, e o banco não fornece automaticamente uma cotação atual de mercado.

### 92. Se eu informar apenas “vendi R$ 30 mil de PETR4”, por que isso não basta?

O valor total vendido não informa, sozinho, quantidade, preço unitário, custo médio e todos os demais dados necessários. O sistema não deve inventar esses campos para produzir um número. Além disso, o total de uma operação não deve ser confundido com o total das vendas relevantes do mês.

### 93. Qual seria uma mensagem completa para testar o caso da PETR4?

Em um banco de testes: “Vendi 4.000 PETR4 por R$ 45 por ação em 22/09/2026, em operação comum, não day trade. Minhas vendas de ações no mês, incluindo esta, somam R$ 180.000. Consulte meu custo médio registrado.” Custos e retenções também devem ser informados quando necessários. Essa mensagem testa uma venda que pode ser persistida, não uma hipótese sem efeitos.

### 94. Qual parte desse exemplo pode ser conferida sem depender da IA?

A aritmética básica: 4.000 vezes R$ 45 produz R$ 180.000 de venda; 4.000 vezes R$ 40 produz R$ 160.000 de custo de aquisição no exemplo simplificado. A diferença bruta é R$ 20.000. Esse cálculo não é o imposto final: não incorpora todos os custos, retenções e condições da apuração.

### 95. Se eu vender apenas metade, o custo médio também cai pela metade?

No algoritmo implementado, uma venda reduz a quantidade mantida, mas não divide o custo médio unitário pela metade. Partindo de 4.000 unidades a R$ 40, vender 2.000 deixa 2.000 unidades com média unitária de R$ 40, na ausência de outras operações. O valor total da posição ao custo é que diminui.

### 96. E se eu comprar mais PETR4 por outro preço?

O algoritmo recalcula a média ponderada. Por exemplo, 4.000 unidades a R$ 40 mais 1.000 a R$ 50 resultam em R$ 210.000 divididos por 5.000 unidades, ou R$ 42 por unidade. É um exemplo do comportamento do algoritmo, sem incorporar eventos ou custos adicionais não representados.

### 97. O banco substitui o extrato da corretora?

Não. Ele contém o que foi registrado na aplicação, que pode estar incompleto ou errado. Não há garantia de importação e conciliação de todas as movimentações reais. O histórico do protótipo deve ser apresentado como histórico interno, não como prova independente da carteira do investidor.

### 98. O que acontece se o usuário repetir uma mensagem de venda?

O fluxo não deve ser presumido idempotente. Como uma venda calculada pode ser gravada, repetir a solicitação pode produzir registros duplicados. A prevenção de duplicidade e a confirmação explícita do registro são pontos importantes antes de tratar o chat como interface operacional confiável.

### 99. Se aparecer “não registrei a venda” na resposta, posso confiar?

Não apenas no texto gerado. O servidor MCP não grava, mas o agente do backend pode gravar depois do cálculo, e essa diferença pode não ser explicada corretamente pelo modelo. A confirmação deve ser baseada no resultado da persistência e no histórico, não em uma afirmação livre da IA.

### 100. Um resumo vazio significa que não tenho imposto a pagar?

Não. Pode significar ausência de vendas registradas para aquele usuário e período, falha de entrada de dados ou carteira incompleta. A interface deve distinguir ausência de dados de uma apuração efetivamente realizada com resultado zero. Essa diferença motivou a correção do histórico e de sua apresentação.

## 10. Aprofundamento técnico

### 101. O que um esquema de dados valida e o que ele não valida?

Ele pode exigir tipos, campos e restrições, como quantidade positiva e formato de data. Isso não comprova que os dados correspondem à realidade nem que o enquadramento tributário foi escolhido corretamente. Uma entrada pode ser estruturalmente válida e ainda representar uma operação inventada ou mal interpretada.

### 102. Qual é a diferença entre erro de extração e erro de cálculo?

Erro de extração ocorre quando a mensagem é convertida para dados incorretos, como interpretar uma quantidade errada. Erro de cálculo ocorre quando o motor produz uma saída inadequada para os dados recebidos. Separar essas classes evita culpar a fórmula por uma entrada errada ou atribuir à IA um defeito numérico do código.

### 103. O que seria necessário para atualizar uma regra com segurança?

Conferir a fonte e a vigência, identificar os produtos e situações afetados, revisar o trecho documental e modificar a calculadora quando houver efeito numérico. Depois, reexecutar os testes pertinentes. Atualizar somente o texto do RAG não altera automaticamente as fórmulas Python.

### 104. Pode haver divergência entre a regra recuperada e a calculadora?

Sim. São componentes diferentes e podem ser atualizados em momentos distintos. Uma explicação pode mencionar uma condição que não está representada no cálculo, ou o código pode estar mais atualizado que o trecho recuperado. A avaliação precisa verificar coerência entre evidência, entrada, cálculo e explicação.

### 105. O que é prompt injection nesse contexto?

É a tentativa de fazer o modelo tratar conteúdo não confiável como uma instrução para alterar seu comportamento. As instruções do ciclo dizem que documentos recuperados são evidências, não comandos, e o backend restringe ferramentas e argumentos. Essas medidas não permitem afirmar que todos os ataques foram eliminados.

### 106. Os dados financeiros permanecem todos no computador local?

Não se deve afirmar isso. SQLite, ChromaDB e o servidor MCP são locais na configuração examinada, mas o modelo é acessado por uma API externa. Mensagens, operação extraída, contexto e resultados usados no diálogo com ferramentas podem compor as solicitações ao provedor. Uma implantação real exigiria avaliação de privacidade e minimização desses dados.

### 107. O sistema funciona sem conexão com o provedor de IA?

O chat depende do acesso ao modelo para classificar, extrair e responder. O caminho estruturado de cálculo utiliza o servidor MCP local e não precisa de uma explicação gerada para executar a fórmula. Isso não significa que toda a aplicação ou qualquer instalação funcione integralmente offline.

### 108. Por que manter logs das chamadas de ferramentas?

Para distinguir uma resposta que realmente usou cálculo de outra que apenas apresentou um texto plausível. Os logs ajudam a identificar ferramenta selecionada e ocorrência de falha. Para rastreabilidade completa, também seria necessário controlar versões, entradas e resultados, com cuidado para não expor dados sensíveis.

### 109. Como testar o sistema sem pagar por chamadas de modelo a cada teste?

Podemos substituir o cliente de IA por respostas controladas nos testes de software. Isso permite exercitar sequências de ferramentas, dados faltantes e falhas de protocolo. Porém, esses testes não demonstram como um modelo real classificará uma mensagem; essa parte exige ensaios separados e claramente identificados.

### 110. MCP permite trocar de modelo sem alterar nada?

Não necessariamente. O protocolo ajuda a padronizar o acesso às ferramentas, mas o cliente de IA, os formatos de mensagens e o tratamento de respostas dependem da integração. Além disso, outro modelo pode selecionar ferramentas ou interpretar instruções de forma diferente. A substituição exigiria adaptação e novos testes.

## 11. Aprofundamento metodológico e defesa

### 111. Qual é a diferença entre teste unitário, integração e ponta a ponta?

Um teste unitário verifica um componente delimitado, como uma função de cálculo. Um teste de integração verifica a interação entre componentes, como cliente e servidor MCP. Um teste de ponta a ponta acompanha a solicitação pela interface até a resposta e a persistência. Aprovação em uma camada não garante aprovação nas outras.

### 112. Por que comparar MCP com chamada direta da calculadora?

Para verificar se transporte, serialização e reconstrução da resposta preservam os resultados nos casos examinados. Como ambos reutilizam as mesmas fórmulas, a comparação não é uma validação independente dessas fórmulas. Se os dois caminhos compartilham um erro de regra, podem concordar perfeitamente.

### 113. O que a repetição do julgamento automático demonstra?

Demonstra estabilidade do avaliador nas condições repetidas. Não demonstra, por si só, que o julgamento é correto: um avaliador pode repetir consistentemente a mesma interpretação errada. Por isso, repetibilidade e validade devem ser discutidas separadamente.

### 114. Por que usar o mesmo fornecedor para gerar e julgar é uma limitação?

Os modelos podem compartilhar tendências de estilo, conhecimento e avaliação. Isso pode favorecer certas respostas ou deixar erros semelhantes passarem. Uma ampliação do estudo deveria incluir avaliação humana especializada e, quando pertinente, avaliadores de outras famílias de modelos.

### 115. Qual é o risco de melhorar o corpus usando o próprio benchmark?

O sistema pode ficar ajustado às perguntas conhecidas sem melhorar proporcionalmente em dúvidas novas. A separação entre desenvolvimento e teste ajuda, mas a origem e o uso do conjunto também importam. Para generalizar, eu precisaria avaliar consultas externas que não orientaram as revisões.

### 116. A comparação feita prova que RAG é melhor que não usar RAG?

Não diretamente. As configurações relatadas comparam corpus inicial e revisado e modelos em condições específicas; não constituem uma comparação completa com uma condição sem RAG. Portanto, o resultado sustenta uma conclusão sobre as configurações avaliadas, não uma superioridade universal da técnica.

### 117. Como comparar modelos de maneira mais rigorosa em uma próxima avaliação?

Manter perguntas, corpus, critérios, condições de execução e orçamento claramente controlados, registrar versões e repetir execuções quando adequado. Também incluir avaliação externa e condições de referência relevantes, como resposta sem recuperação. É importante evitar que várias mudanças simultâneas sejam atribuídas apenas ao modelo.

### 118. O que seria necessário para transformar o protótipo em produto?

Além de revisão tributária especializada, seriam necessários autenticação, autorização, conciliação dos dados, prevenção de duplicidade, separação entre simular e registrar, atualização normativa e testes de carga e segurança. A interface demonstrada é uma parte desse caminho. Não é adequado apresentar esses requisitos como meros detalhes de acabamento.

### 119. Como responder a uma pergunta da banca sobre um resultado que você não lembra?

Eu diria que preciso conferir a tabela ou a evidência específica, em vez de arriscar um número. Posso explicar o método e apontar onde o resultado foi registrado. Reconhecer o limite da lembrança é preferível a produzir uma afirmação incompatível com a monografia.

### 120. Qual mensagem principal deve ficar ao final da defesa?

Combinar recuperação documental, cálculo programado e geração de linguagem tornou possível construir e avaliar um assistente aplicado ao domínio escolhido. A avaliação mostrou benefícios no conjunto estudado e revelou limites importantes da integração. O resultado é um protótipo verificável e criticamente delimitado, não uma garantia de correção tributária para qualquer operação.

## Consulta rápida antes da apresentação

Não afirmar que o LLM nunca escolhe ferramentas: ele escolhe no fluxo delimitado do chat. Não chamar a consulta local de custo médio de ferramenta remota MCP. Não confundir armazenamento de mensagens com memória conversacional. Não apresentar tarifas parametrizadas como cotações atuais da B3. Não tratar teste de software como validação tributária independente. Não apresentar uma hipótese de venda como simulação segura sem persistência.

As perguntas 1, 3, 9, 17, 21, 23, 31, 53, 56, 58, 71, 80, 81, 83 e 86 são um bom primeiro conjunto para ensaio oral. Depois, peça que alguém faça perguntas de acompanhamento: “onde isso está no código?”, “qual evidência sustenta isso?” e “qual é a limitação dessa afirmação?”.

## Onde conferir as respostas

Os caminhos abaixo são relativos à raiz do projeto.

| Tema | Código ou documento |
| --- | --- |
| Encaminhamento das mensagens | `backend/app/agents/orchestrator.py` |
| Compra, venda e persistência após cálculo | `backend/app/agents/base_agent.py` |
| Ferramentas selecionadas pelo modelo e seus limites | `backend/app/agents/tool_chat.py` |
| Caminho estruturado e transporte MCP | `backend/app/mcp_gateway.py` |
| Ferramentas do servidor | `mcp_server/server.py` |
| Operações, custo médio e chat armazenado | `backend/app/storage/repository.py` |
| Histórico de operações e resumo | `backend/app/api/trades.py` e `backend/app/api/calculations.py` |
| Identidade enviada pela interface | `frontend/src/app/services/api.service.ts` |
| Recuperação e corpus | `backend/app/vector_db/revised_client.py` e `backend/app/vector_db/curated.py` |
| Avaliação, resultados e limitações | `Documentation/TCC/Revisao/manuscrito.md`, capítulos 6, 7 e 8 |
| Suíte de 146 testes documentada | `Documentation/TCC/Revisao/Entrega_Final/evidencias/revisao_adendo_tool_use_20260920/pytest.txt` |

Este roteiro atualiza afirmações antigas sobre servidores MCP, seleção de ferramentas, concorrência e histórico. As evidências históricas da monografia não foram reescritas nem substituídas, e nenhum resultado novo de modelo foi produzido nesta revisão. Para discutir valores tributários reais ou mudanças de legislação, consulte as fontes oficiais e a vigência aplicável, além da implementação estudada.
