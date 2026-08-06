# Plano: Gerador de Aulas via WhatsApp (LLM + LaTeX + WAHA + n8n)

## Contexto

Este projeto (`card12`) já tem uma infraestrutura local funcional de n8n + WAHA, com um
workflow de ping-pong validado de ponta a ponta (ver `README.md` e `Relatório 12 - Lucas
Augusto.pdf` na raiz do projeto). Esta prática estende essa base: em vez de só ecoar a
mensagem recebida, o bot deve entender um pedido de aula em linguagem natural, gerar o
conteúdo com uma LLM seguindo diretrizes de formatação, compilar esse conteúdo em LaTeX
para PDF, e responder com o PDF pronto pelo próprio WhatsApp.

Conceitualmente, isso é uma reaplicação do "Planejador de Aulas" já feito no Relatório 11
(teoria + exercícios, lá via ADK/Streamlit e saída em Markdown/Obsidian) — aqui entregue
por WhatsApp e em PDF, usando a stack n8n + WAHA já validada neste card.

## Decisões confirmadas com o usuário

- **LLM:** Anthropic Claude, via credencial de API configurada diretamente no n8n (chave
  fornecida pelo usuário — não fica em nenhum arquivo do repositório).
- **Compilação LaTeX → PDF:** novo container local rodando TeX Live, exposto como uma API
  HTTP interna que o n8n chama — mantém tudo local, sem depender de serviço externo.
- **Escopo do workflow:** um workflow **novo e separado** no n8n, dedicado a esta
  funcionalidade.
- **Diretrizes de formatação:** arquivo próprio, já criado como parte deste plano —
  [`templates/diretrizes-formatacao.md`](templates/diretrizes-formatacao.md).
- **Stack própria e independente:** em vez de alterar a infraestrutura documentada do
  ping-pong (`docker-compose.yml` na raiz do projeto), foi feita uma **cópia** desse
  arquivo para [`pratica/docker-compose.yml`](docker-compose.yml), e é essa cópia que
  recebe as alterações necessárias (novo serviço `latex-compiler`, volume de templates no
  `n8n`). O `docker-compose.yml` original, na raiz, **não é tocado** — continua sendo a
  documentação fiel de como o ping-pong foi implementado e validado (ver `README.md` e o
  Relatório 12 na raiz).
- **Ping-pong não precisa ficar ativo:** já que aquele workflow está documentado e
  validado, esta prática assume a stack da raiz parada (`docker compose down` lá) e só a
  stack de `pratica/` rodando. Isso elimina de saída qualquer problema de duas sessões
  WAHA/dois workflows competindo pela mesma mensagem — cada prática tem sua própria sessão
  do WhatsApp, pareada de forma independente.

## Arquitetura proposta

```
WhatsApp (pedido, ex: "/aula Física - Lei de Ohm - Ensino Médio")
  │
  ▼
WAHA (nova sessão, própria desta stack)
  │
  ▼
n8n — novo workflow "Gerador de Aulas"
  1. WAHA Trigger
  2. Filter — só segue se payload.body começar com "/aula"
     (controle de custo/spam: evita chamar a LLM para qualquer mensagem)
  3. Read/Write File from Disk — lê templates/diretrizes-formatacao.md
     (montado como volume somente-leitura no container do n8n)
  4. Anthropic Chat Model — system prompt = diretrizes + pedido do usuário;
     saída esperada = LaTeX puro (ver diretrizes)
  5. HTTP Request → latex-compiler (POST /compile, body: {"tex": "<fonte>"})
  6. IF (compilação OK?)
       sucesso → WAHA (Send File) — envia o PDF binário recebido
       erro    → WAHA (Send Text) — envia mensagem de erro amigável
  │
  ▼
WAHA → WhatsApp (PDF da aula, ou aviso de erro)
```

### `pratica/docker-compose.yml`

Cópia de `docker-compose.yml` (raiz), já criada, com dois ajustes em relação ao original:

```yaml
  n8n:
    # ...igual ao original, mais o volume de templates:
    volumes:
      - ./n8n_data:/home/node/.n8n
      - ./templates:/data/templates:ro

  latex-compiler:
    build: ./compiler
    container_name: latex-compiler
    restart: unless-stopped
    ports:
      - "127.0.0.1:8001:8000"
```

`latex-compiler` não tem volumes: o serviço é stateless — recebe o `.tex` no corpo da
requisição e devolve os bytes do PDF na resposta, sem persistir nada em disco entre
chamadas. Os caminhos de volume (`./n8n_data`, `./waha_data`, `./templates`) são relativos
a `pratica/`, então essa stack usa seus próprios dados, independentes dos da raiz.

**Atenção operacional:** como os `container_name` (`n8n`, `waha`) e as portas publicadas
são iguais aos do compose da raiz, as duas stacks não podem rodar ao mesmo tempo. Antes de
subir esta (`docker compose up -d` dentro de `pratica/`), pare a da raiz
(`docker compose down`, executado na raiz do projeto).

## Passo a passo (com critérios de verificação)

1. **Escrever as diretrizes de formatação.**
   Arquivo: `pratica/templates/diretrizes-formatacao.md` — já criado como parte deste
   plano, com pacotes disponíveis, estrutura obrigatória do documento e um exemplo mínimo
   válido.
   - `verify`: arquivo existe e cobre pacotes disponíveis, estrutura de seções
     obrigatórias e um exemplo de documento LaTeX completo e válido.

2. **Criar o microsserviço de compilação LaTeX.**
   Arquivos: `pratica/compiler/Dockerfile`, `pratica/compiler/app.py`,
   `pratica/compiler/requirements.txt`. Imagem baseada em uma distribuição TeX Live,
   com uma API FastAPI expondo `POST /compile`, que recebe `{"tex": "<fonte>"}`, escreve
   em um diretório temporário, roda `pdflatex -interaction=nonstopmode` duas vezes
   (necessário para resolver sumário/referências internas do `hyperref`), e devolve o PDF
   gerado como resposta binária (ou um erro 422 com o log do `pdflatex`, em caso de falha
   de compilação).
   - `verify`: `docker build` da imagem completa sem erro; `curl -X POST
     http://localhost:8001/compile -d '{"tex": "..."}' --output teste.pdf` com o exemplo
     mínimo das diretrizes gera um arquivo cujos primeiros bytes são `%PDF`.

3. **Subir a stack de `pratica/`.**
   Parar a stack da raiz (`docker compose down`, na raiz do projeto) e subir a nova
   (`docker compose up -d`, dentro de `pratica/`).
   - `verify`: os três serviços (`n8n`, `waha`, `latex-compiler`) sobem sem erro; de
     dentro do container do n8n, uma chamada ao `latex-compiler` pelo nome do serviço
     (`http://latex-compiler:8000/compile`) funciona.

4. **Criar a conta no n8n, instalar o nó comunitário da WAHA, parear o WhatsApp e criar a
   credencial da Anthropic.**
   Como esta é uma instância nova do n8n (dados em `pratica/n8n_data`, ainda sem nada
   configurado), os passos manuais já feitos para o ping-pong precisam ser refeitos aqui:
   criar conta em `http://localhost:5678`, instalar `@devlikeapro/n8n-nodes-waha` em
   Settings → Community Nodes, parear o WhatsApp via QR Code no dashboard da WAHA
   (`http://localhost:3000`), e criar a credencial Anthropic em Settings → Credentials,
   colando a chave de API fornecida pelo usuário.
   - `verify`: login no n8n funciona; nós com prefixo "WAHA" aparecem no painel de nodes;
     `GET /api/sessions` da WAHA mostra a sessão em `WORKING`; um teste manual do node
     "Anthropic Chat Model" no n8n retorna uma resposta válida.

5. **Montar o workflow "Gerador de Aulas" no n8n**, seguindo a arquitetura acima: WAHA
   Trigger → Filter (`/aula`) → Read File (diretrizes) → Anthropic Chat Model → HTTP
   Request (compilar) → IF (sucesso/erro) → WAHA Send File / WAHA Send Text.
   - **Atenção:** o nome exato da operação de envio de arquivo no nó comunitário da WAHA
     (`Send File`, `Send Document` ou similar) não foi confirmado neste plano — verificar
     no dropdown "Operation" do node WAHA dentro do n8n durante a implementação, e ajustar
     este passo com o nome real encontrado.
   - `verify`: usando o "Test workflow" do n8n com uma mensagem de teste simulando
     `/aula Física - Lei de Ohm - Ensino Médio`, o fluxo completa sem erro e produz um PDF
     coerente com as diretrizes.

6. **Registrar o webhook na sessão WAHA e ativar o workflow em produção.**
   Editar `config.webhooks` da sessão via API (mesmo padrão usado no workflow de
   ping-pong), apontando para a Production Webhook URL deste workflow, e ativar o
   workflow no n8n.
   - `verify` (critério de aceite final): enviar `/aula Física - Lei de Ohm - Ensino
     Médio` de outro número resulta no recebimento automático de um PDF de aula gerado
     pela LLM, formatado de acordo com as diretrizes, sem intervenção manual.

## Arquivos a criar

- `pratica/PLANO_PRATICA.md` — este plano (criado).
- `pratica/templates/diretrizes-formatacao.md` — diretrizes de formatação (criado).
- `pratica/docker-compose.yml` — cópia do compose original com os ajustes desta prática
  (criado).
- `pratica/.gitignore` — ignora `n8n_data/` e `waha_data/` desta stack (criado).
- `pratica/compiler/Dockerfile` — imagem do serviço de compilação.
- `pratica/compiler/app.py` — API FastAPI do serviço de compilação.
- `pratica/compiler/requirements.txt` — dependências Python do serviço.

## Fora de escopo

- Suporte a formatos de documento além do definido nas diretrizes (slides, apostilas
  multi-aula, etc.).
- Cache ou reaproveitamento de PDFs gerados para pedidos repetidos/similares.
- Autenticação de quem pode pedir uma aula — qualquer contato que envie `/aula ...` para o
  número conectado recebe uma resposta.
- Rodar a stack do ping-pong e a de `pratica/` simultaneamente (mesmos nomes de container
  e portas — ver nota operacional acima).
