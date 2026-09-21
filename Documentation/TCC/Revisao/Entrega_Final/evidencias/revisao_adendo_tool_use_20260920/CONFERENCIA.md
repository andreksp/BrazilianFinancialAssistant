# Conferência do adendo de Claude e correção complementar

Data: 20/09/2026. Projeto: D:/Projects/BrazilianFinancialAssistant.

## Evidências conferidas

Foram lidos `../tool_use_validacao_claude/RELATORIO_TOOL_USE.md`, o JSON da segunda rodada com modelo real, o registro de concorrência, o log de instalação e o encerramento do log da suíte limpa.

- O adendo confirma as quatro correções anteriores. O JSON real registra uma compra e duas vendas; os impostos das vendas são R$ 99,63 (HGLG11) e R$ 19,93 (KNRI11).
- O modelo solicitou consulta de preço médio no caso com compra anterior, mas não no caso com custo informado. Os sete cenários não constituem reexecução do benchmark histórico.
- A instalação limpa está documentada com saída sem dependências quebradas. O arquivo `pytest_suite_limpa.txt` registra **120**, não 142 testes. O adendo declara 142, mas esse log específico pertence à rodada anterior. A execução de 142 também tem evidência própria em `../correcoes_tool_use_20260920/pytest.txt`; não se deve atribuir a ela a instalação limpa daquele log.
- O JSON de concorrência registra máximo intervalo de 0,077 s entre batimentos durante um e três chats; as respostas de modelo eram simuladas. Isso não certifica desempenho com carga elevada ou latência real de provedor.
- O custo de US$ 0,1349 é um **custo estimado** no JSON, não uma cobrança conferida em fatura. Não foram feitas novas chamadas pagas nesta conferência.
- O cenário de ações sem total mensal terminou após consulta de custo médio vazia. Não comprova, nessa rodada, que a ferramenta de cálculo tenha rejeitado especificamente a falta do total mensal. A possível falha de extração de custo permanece uma observação sem frequência medida.
- Navegador e benchmark completo não foram executados nesta rodada.

## Correção complementar

O achado remanescente foi reproduzido pelo caminho `consultar_preco_medio -> end_turn`, sem `calculate_trade`. A consulta retornava custo nulo como sucesso, e o encerramento sem resultado gerava mensagem genérica.

Agora a consulta com custo indisponível, para ativos que exigem esse dado, retorna erro de validação específico ao modelo. O host preserva a mensagem ao encerrar, informa o ativo e solicita o custo médio e o reenvio dos dados completos da venda. A ressalva de reenvio corresponde à ausência de memória entre requisições. Empréstimo continua dispensado dessa exigência.

Não se repassa automaticamente qualquer texto final do modelo como resultado: isso poderia apresentar imposto inventado ou alegação de gravação sem cálculo validado. A solução entrega esclarecimento baseado no estado conhecido pelo backend. Não altera o contrato de persistência nem implementa memória conversacional.

O comentário do adendo sobre erros retornados via `tool_result/is_error` como novidade da correção anterior não corresponde ao histórico do código: esse mecanismo já existia; a correção anterior passou a preservar sua mensagem ao encerrar e a desembrulhar exceções agrupadas.

## Verificação local posterior

**146 passed, 2 warnings in 15.78s**, conforme `pytest.txt`. Quatro casos novos: custo ausente sem tentativa de cálculo em FII e ações; texto inventado não convertido em sucesso; agente com sessão MCP real, resposta específica e nenhuma chamada de gravação de venda. Respostas de LLM programadas, banco temporário e chave de API vazia. Ambiente já instalado, não instalação limpa nova. Avisos de depreciação Starlette/httpx e Pydantic.

Não foram alterados os artefatos históricos de Claude. A alteração complementar ainda não foi exercitada com modelo pago nem navegador.

## Sincronização da monografia — pendente

O Word canônico estava bloqueado por outro processo. Não foram alterados Word, PDF, modelo ou manuscrito, evitando sobrescrever trabalho aberto ou criar divergência entre as fontes.

Ao liberar o documento, a Seção 7.5 deve distinguir: validação original de 120 testes em instalação limpa; correções e rodada real posterior; verificação local de 146 testes após o ajuste complementar. Atualizar também as afirmações de trabalhos futuros sobre instalação e concorrência para refletir os ensaios já realizados, preservando suas limitações. Não modificar resumo aprovado nem métricas históricas; não apresentar o benchmark antigo como avaliação da arquitetura atual.
