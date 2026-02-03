# Gerador de Posts LinkedIn com Loop Agent

Este exemplo demonstra o uso de um padrão de Agente Sequencial e Loop Agent no Agent Development Kit (ADK) para gerar e refinar um post do LinkedIn.

## Visão Geral

O Gerador de Posts LinkedIn usa um pipeline sequencial com um componente de loop para:
1. Gerar um post inicial do LinkedIn
2. Refinar iterativamente o post até que os requisitos de qualidade sejam atendidos

Isso demonstra vários padrões importantes:
1. **Pipeline Sequencial**: Um fluxo de trabalho multi-etapas com estágios distintos
2. **Refinamento Iterativo**: Usando um loop para refinar conteúdo repetidamente
3. **Verificação Automática de Qualidade**: Validando conteúdo contra critérios específicos
4. **Refinamento Orientado por Feedback**: Melhorando conteúdo baseado em feedback específico
5. **Ferramenta de Saída do Loop**: Usando uma ferramenta para encerrar o loop quando os requisitos de qualidade são atendidos

## Arquitetura

O sistema é composto pelos seguintes componentes:

### Agente Sequencial Raiz

`LinkedInPostGenerationPipeline` - Um SequentialAgent que orquestra o processo geral:
1. Primeiro executa o gerador de post inicial
2. Depois executa o loop de refinamento

### Gerador de Post Inicial

`InitialPostGenerator` - Um LlmAgent que cria o primeiro rascunho do post do LinkedIn sem contexto prévio.

### Loop de Refinamento

`PostRefinementLoop` - Um LoopAgent que executa um processo de refinamento em duas etapas:
1. Primeiro executa o revisor para avaliar o post e possivelmente sair do loop
2. Depois executa o refinador para melhorar o post se o loop continuar

### Sub-Agentes Dentro do Loop de Refinamento

1. **Revisor de Post** (`PostReviewer`) - Revisa posts quanto à qualidade e fornece feedback ou sai do loop se os requisitos forem atendidos
2. **Refinador de Post** (`PostRefiner`) - Refina o post baseado no feedback para melhorar a qualidade

### Ferramentas

1. **Contador de Caracteres** - Valida o tamanho do post contra os requisitos (usado pelo Revisor)
2. **Saída do Loop** - Encerra o loop quando todos os critérios de qualidade são satisfeitos (usado pelo Revisor)

## Controle do Loop com Ferramenta de Saída

Um padrão de design importante neste exemplo é o uso de uma ferramenta `exit_loop` para controlar quando o loop termina. O Revisor de Post tem duas responsabilidades:

1. **Avaliação de Qualidade**: Verifica se o post atende todos os requisitos
2. **Controle do Loop**: Chama a ferramenta exit_loop quando o post passa em todas as verificações de qualidade

Quando a ferramenta exit_loop é chamada:
1. Ela define `tool_context.actions.escalate = True`
2. Isso sinaliza ao LoopAgent que ele deve parar de iterar

Esta abordagem segue as melhores práticas do ADK ao:
1. Separar a geração inicial do refinamento
2. Dar ao revisor de qualidade controle direto sobre o encerramento do loop
3. Usar um agente dedicado para refinamento de posts
4. Usar uma ferramenta para gerenciar o fluxo de controle do loop

## Uso

Para executar este exemplo:

```bash
cd 12-loop-agent
adk web
```

Depois na interface web, insira um prompt como:
"Gere um post do LinkedIn sobre o que aprendi do tutorial do Agent Development Kit do @aiwithbrandon."

O sistema irá:
1. Gerar um post inicial do LinkedIn
2. Revisar o post quanto à qualidade e conformidade com os requisitos
3. Se o post atender todos os requisitos, sair do loop
4. Caso contrário, fornecer feedback e refinar o post
5. Continuar este processo até que um post satisfatório seja criado ou o máximo de iterações seja atingido
6. Retornar o post final

## Exemplo de Entrada

```
Gere um post do LinkedIn sobre o que aprendi do tutorial do Agent Development Kit do @aiwithbrandon.
```

## Encerramento do Loop

O loop termina de uma das duas formas:
1. Quando o post atende todos os requisitos de qualidade (revisor chama a ferramenta exit_loop)
2. Após atingir o número máximo de iterações (10)
