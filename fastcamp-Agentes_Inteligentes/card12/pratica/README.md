# Gerador de Aulas via WhatsApp (LLM + LaTeX)

Extensão do agente WhatsApp do card12: em vez de só ecoar mensagens, esse workflow recebe
um pedido de aula em linguagem natural, gera o conteúdo com o Claude (Anthropic), compila
em LaTeX/PDF localmente e responde com o PDF pronto, tudo pelo WhatsApp.


## Como funciona

```
WhatsApp ("/aula Física - Lei de Ohm - Ensino Médio")
  → WAHA Trigger
  → Filter (só segue se a mensagem começar com "/aula")
  → Ler diretrizes de formatação (pratica/templates/diretrizes-formatacao.md)
  → Claude gera o LaTeX completo da aula
  → Compilador LaTeX local (latex-compiler) gera o PDF
  → Sucesso → converte PDF em base64 → envia como arquivo pelo WhatsApp
  → Erro     → envia mensagem de texto avisando a falha
```

## Infraestrutura

```bash
cd pratica
mkdir -p n8n_data waha_data
docker compose up -d --build
```

- **n8n** — `http://localhost:5678`
- **WAHA** — `http://localhost:3000`
- **latex-compiler** — `http://localhost:8001` (uso interno do n8n; `POST /compile` recebe
  `{"tex": "<fonte>"}` e devolve o PDF gerado, ou erro 422 com o log do `pdflatex`)

Essa stack usa os **mesmos nomes de container e portas** da stack raiz do card12 — as duas
não podem rodar ao mesmo tempo (`docker compose down` na raiz antes de subir esta).

## Setup

1. Suba os containers (acima).
2. Crie a conta no n8n, instale o nó comunitário `@devlikeapro/n8n-nodes-waha` e pareie o
   WhatsApp via QR Code no dashboard da WAHA — mesmo processo do card12 original, porque
   essa é uma instância nova, sem nada configurado ainda.
3. Crie a credencial Anthropic no n8n (Settings → Credentials → Anthropic) com sua própria
   chave de API.
4. O workflow **"Gerador de Aulas"** e a credencial da WAHA já vêm prontos (montados via
   API durante a implementação) — só falta ligar a credencial Anthropic ao node "Gerar
   LaTeX com Claude" e ativar o workflow.

## O que a LLM recebe como contexto

Antes de gerar qualquer aula, o workflow lê
[`templates/diretrizes-formatacao.md`](templates/diretrizes-formatacao.md) e manda o
conteúdo inteiro como *system prompt* do Claude — pacotes LaTeX disponíveis, estrutura
obrigatória do documento (objetivos, conteúdo teórico, exercícios) e um exemplo mínimo
válido. Isso é reaplicado em toda solicitação, então editar esse arquivo muda o
comportamento da LLM sem precisar tocar no workflow.

## Bugs encontrados e corrigidos durante os testes

Todos encontrados rodando o workflow de ponta a ponta via API do n8n (não só teoricamente
montado)

- **Claude embrulhando o LaTeX em blocos de código Markdown** (` ```latex ... ``` `),
  mesmo com instrução explícita para não fazer isso — o node de compilação agora remove
  esses blocos antes de mandar o conteúdo pro compilador, em vez de confiar cegamente na
  instrução do prompt.
- **Envio do PDF pelo WhatsApp falhando** — a WAHA espera o arquivo em base64 dentro de um
  campo JSON, não como dado binário bruto. Adicionado um node de conversão binário→base64
  antes do envio.

## Status

Testado de ponta a ponta via execução direta pela API do n8n (webhook simulado): o fluxo
completo gera e entrega um PDF real.
