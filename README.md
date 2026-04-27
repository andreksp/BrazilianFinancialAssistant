# BrazilianFinancialAssistant
MBA Artificial Inteligence - Brazilian Financial Assisant using RAG


# Claude Commands
/init - Init Claude.md
/plan - Plan mode before working on it
/memory 
/model  - Choose mode
/clear - Clear context
/compact - Shrink Context
/rewind - Rollback based on checkpoints

  ┌──────────────────┬───────────────────────────────────────┐
  │      Skill       │                  Uso                  │
  ├──────────────────┼───────────────────────────────────────┤
  │ /review          │ Review de pull requests               │
  ├──────────────────┼───────────────────────────────────────┤
  │ /security-review │ Revisão de segurança do código        │
  ├──────────────────┼───────────────────────────────────────┤
  │ /plan            │ Modo de planejamento (atual)          │
  ├──────────────────┼───────────────────────────────────────┤
  │ /init            │ Gera/atualiza CLAUDE.md               │
  ├──────────────────┼───────────────────────────────────────┤
  │ /claude-api      │ Ajuda com integração da API do Claude │
  ├──────────────────┼───────────────────────────────────────┤
  │ /schedule        │ Agenda agentes recorrentes            │
  ├──────────────────┼───────────────────────────────────────┤
  │ /loop            │ Repete um prompt em intervalo         │
  ├──────────────────┼───────────────────────────────────────┤
  │ /ultrareview     │ Review multi-agente profundo          │
  └──────────────────┴───────────────────────────────────────┘
@src/components/file.txt - Add file to the context


# Prompts

A ideia do trabalho de conclusao de curso seria criar um chat bot ou assistente para o mercado financeiro Brasileiro
Podermos calculor impostos, taxas, valor liquido e coisas relacionadas quando o usuario inserir os trades que foi feito no brazil.


Primeira Fase
Seria incluir as regras de acoes do mercado brasileiro. 
Incluiria,
	Acoes
	BDRs
	Fundos Imobiliarios
	Opcoes de Acoes

Segunda Fase
	Derivativos 
		Futuro e Dolar, 
		Futuro De Indice, 
		Futuro de criptomoedas 
		etc. 
	
Terceira Fase 
	Emprestimos de acoes. 
	
adiciona isso no Claude.md?
	
	
Tambem  adcionar deve planejamos usar o ChromaDB

Uma UI feita em angular para podeermos interagir com o chat e um backend em python?
tudo no mesmo projeto pra simplificar o deployment. 

Acho que podemos usar docker tb. 

Tambem adicionar que planejo subir isso no Claude(Azure ou AWS) temporariamente para apresentacao do TCC
Tambem planejo criar algum MCP proprio que ajude nesse trabalho.