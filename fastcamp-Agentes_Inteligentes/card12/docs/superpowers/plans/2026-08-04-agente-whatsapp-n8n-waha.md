# Agente WhatsApp (n8n + WAHA) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Subir localmente, via Docker Compose, uma automação de WhatsApp (n8n + WAHA) reproduzível a partir de arquivos versionados, com um fluxo "ping-pong" funcional de ponta a ponta como prova de que WhatsApp → WAHA → n8n → WhatsApp está operante.

**Architecture:** Dois containers Docker orquestrados por `docker-compose.yml` na mesma rede padrão do Compose: `n8n` (orquestrador de workflow, expõe UI/webhooks na porta 5678) e `waha` (API HTTP que fala com o WhatsApp Web, porta 3000). Os containers se comunicam entre si pelo nome do serviço (`http://n8n:5678`, `http://waha:3000`) em vez de `host.docker.internal`. O pareamento do WhatsApp (QR Code), a instalação do nó comunitário da WAHA e a montagem do workflow são feitos manualmente via UI — não há como (nem vale a pena) automatizar essas interações específicas de ferramenta.

**Tech Stack:** Docker / Docker Compose, imagem `n8nio/n8n`, imagem `devlikeapro/waha`, pacote de nó comunitário `@devlikeapro/n8n-nodes-waha`.

## Global Constraints

- Simplicidade em primeiro lugar: nenhuma abstração, `.env`, script auxiliar ou automação além do estritamente necessário para reproduzir o tutorial (`CLAUDE.md` princípio 2).
- Alterações cirúrgicas: cada arquivo criado tem responsabilidade única; nenhuma funcionalidade além do smoke-test ping-pong (`CLAUDE.md` princípio 3; ver "Fora de escopo" no `PLAN_CARD12.md`).
- Execução orientada a objetivos: toda task tem um critério de verificação explícito e reproduzível — comando de shell ou chamada de API com saída esperada, nunca "deve funcionar" (`CLAUDE.md` princípio 4).
- Suposição já validada com o usuário (`PLAN_CARD12.md`): comunicação entre os dois containers via nome de serviço do Compose (`n8n`, `waha`), não via `host.docker.internal`.
- Fora de escopo: lógica de negócio do agente além do ping-pong; automação da instalação do nó comunitário ou da criação do workflow (permanecem manuais via UI, como no tutorial original).

---

### Task 1: Inicializar repositório git e versionar a documentação base

**Files:**
- Create: `.gitignore`
- (nenhum código de aplicação nesta task — apenas controle de versão)

**Interfaces:**
- Produces: repositório git inicializado na raiz do projeto, com `.gitignore` já excluindo os diretórios de dados que as próximas tasks vão criar (`n8n_data/`, `waha_data/`).

- [ ] **Step 1: Verificar que ainda não existe um repositório git**

Run: `git -C /home/augusto/Documentos/LAMIA/FC_Agentes/card12 status`
Expected: erro `fatal: not a git repository (or any of the parent directories): .git`

- [ ] **Step 2: Inicializar o repositório**

Run: `git -C /home/augusto/Documentos/LAMIA/FC_Agentes/card12 init`
Expected: `Initialized empty Git repository in .../card12/.git/`

- [ ] **Step 3: Criar `.gitignore`**

```
n8n_data/
waha_data/
```

- [ ] **Step 4: Verificar que o git enxerga os arquivos existentes como untracked**

Run: `git -C /home/augusto/Documentos/LAMIA/FC_Agentes/card12 status --short`
Expected: lista `CLAUDE.md`, `TUTORIAL_WAHA.md`, `PLAN_CARD12.md`, `docs/`, `.gitignore` como `??` (untracked)

- [ ] **Step 5: Commit**

```bash
cd /home/augusto/Documentos/LAMIA/FC_Agentes/card12
git add .gitignore CLAUDE.md TUTORIAL_WAHA.md PLAN_CARD12.md docs
git commit -m "chore: inicializa repositório e versiona documentação base"
```

---

### Task 2: Criar `docker-compose.yml` com os serviços n8n e WAHA

**Files:**
- Create: `docker-compose.yml`

**Interfaces:**
- Consumes: nenhuma dependência de tasks anteriores além do `.gitignore` (Task 1) já cobrir `n8n_data/` e `waha_data/`.
- Produces: dois serviços acessíveis em `http://localhost:5678` (n8n) e `http://localhost:3000` (waha); dentro da rede do compose, os serviços se resolvem por nome (`http://n8n:5678`, `http://waha:3000`) — usado pela Task 6 e Task 7.

- [ ] **Step 1: Escrever `docker-compose.yml`**

```yaml
services:
  n8n:
    image: n8nio/n8n:1.122.5
    container_name: n8n
    restart: unless-stopped
    ports:
      - "127.0.0.1:5678:5678"
    volumes:
      - ./n8n_data:/home/node/.n8n
    environment:
      - GENERIC_TIMEZONE=America/Sao_Paulo

  waha:
    image: devlikeapro/waha:latest-2026.7.2
    container_name: waha
    restart: unless-stopped
    ports:
      - "127.0.0.1:3000:3000"
    volumes:
      - ./waha_data:/app/.sessions
    environment:
      - WHATSAPP_DEFAULT_ENGINE=NOWEB
      - WAHA_DASHBOARD_USERNAME=admin
      - WAHA_DASHBOARD_PASSWORD=changeme
      - WAHA_API_KEY=changeme-api-key
```

> **Nota de implementação (estado final, após execução real de ponta a ponta):**
> - **Imagens fixadas por versão**, não `:latest` — evita a deriva de versão que já causou quebras (ver abaixo). `devlikeapro/waha:2025.12.1` não existe como tag literal no registry; a tag real correspondente a essa versão é `devlikeapro/waha:latest-2026.7.2` (confirmada via `docker exec waha env` e logs de inicialização).
> - **Portas publicadas só em loopback** (`127.0.0.1:PORT:PORT`) — as credenciais da WAHA ficam em texto plano neste arquivo versionado, e a exposição em `0.0.0.0` (padrão do Docker) deixaria isso alcançável por qualquer um na rede local.
> - **Volume da WAHA em `/app/.sessions`** (não `/tmp`, que é scratch e não persiste a sessão pareada).
> - **Engine `NOWEB`, não `WEBJS`**: o engine original (`WEBJS`, o mesmo do `TUTORIAL_WAHA.md`) automatiza um navegador Chromium fingindo ser um usuário do WhatsApp Web — abordagem estruturalmente frágil, que quebrou de duas formas diferentes durante a execução real (`getChats` e `sendText` retornando erro por mudanças internas do próprio WhatsApp Web). `NOWEB` fala o protocolo do WhatsApp diretamente (via `@adiwajshing/baileys`), sem depender de scraping de navegador, e não sofre dessa classe de problema. Trocar de engine exige parear o WhatsApp de novo (QR Code), mas não muda nada na configuração do workflow do n8n — a API da WAHA é idêntica entre engines.
> - **Store do NOWEB precisa estar habilitada** para resolver contatos no formato `@lid` (identificador novo do WhatsApp) em tempo razoável — sem isso, `sendText` pode demorar minutos ou nunca completar. Isso é configurado por sessão via API (não é uma env var do container), e um bug conhecido da WAHA faz essa config **não sobreviver a um restart do container** (ver `docs/superpowers/plans/2026-08-04-agente-whatsapp-n8n-waha.md`, seção "Dicas de Operação" abaixo, para o comando de reaplicação).
> - **Removidas `WHATSAPP_HOOK_URL` e `WHATSAPP_HOOK_EVENTS`**: eram configuração morta — as Tasks 6 e 7 deste plano configuram o webhook por sessão via dashboard da WAHA, nunca através dessas variáveis de ambiente do container. Deixá-las apontando para um path de webhook inválido só geraria tentativas de POST com erro 404 nos logs da WAHA sem nenhum efeito útil.

- [ ] **Step 2: Validar a sintaxe do compose**

Run: `docker compose -f /home/augusto/Documentos/LAMIA/FC_Agentes/card12/docker-compose.yml config`
Expected: imprime o YAML resolvido sem erros (sem `service ... has neither an image nor a build context`, sem erro de parsing)

- [ ] **Step 3: Pré-criar `./n8n_data` e `./waha_data` com o dono correto**

O processo `n8n` dentro do container roda como UID/GID `1000:1000` (usuário `node`). Se `./n8n_data` não existir, o Docker o cria automaticamente como `root:root` ao subir os containers, e o n8n falha com `EACCES` ao tentar escrever `/home/node/.n8n/config`, entrando em crash loop. Para evitar isso, crie ambos os diretórios como o usuário atual **antes** do primeiro `docker compose up`:

```bash
cd /home/augusto/Documentos/LAMIA/FC_Agentes/card12
mkdir -p n8n_data waha_data
```

**Se `./n8n_data` já existir com dono `root:root`** (de uma tentativa anterior que falhou) **e ainda não contiver dados reais** (nenhuma conta n8n criada — Task 3 não rodou ainda), é seguro remover e recriar:

```bash
docker compose down
rm -rf n8n_data
mkdir -p n8n_data
```

**Se `./n8n_data` já contiver dados reais** (conta criada, workflow montado — depois da Task 3 em diante), **não use `rm -rf`** — isso apagaria a conta e o workflow. Corrija a posse no lugar, sem apagar nada:

```bash
sudo chown -R 1000:1000 n8n_data
```

(`1000` é o UID esperado dentro do container n8n; coincide com o UID do usuário `augusto` neste host, mas o valor fixo `1000` é o que importa, não o nome do usuário.)

O mesmo raciocínio vale para `./waha_data` caso precise ser recriado (o WAHA roda como root no container, então não sofre o problema de permissão do n8n, mas ainda assim `rm -rf` destruiria a sessão do WhatsApp pareada — só remova antes da Task 5, nunca depois).

Verify: `stat -c '%U:%G' n8n_data waha_data` deve mostrar o usuário atual do host (não `root:root`) para `n8n_data`.

- [ ] **Step 4: Subir os containers**

Run: `cd /home/augusto/Documentos/LAMIA/FC_Agentes/card12 && docker compose up -d`
Expected: Docker baixa as imagens `n8nio/n8n` e `devlikeapro/waha` (primeira execução) e reporta `Container n8n Started` / `Container waha Started`

- [ ] **Step 5: Verificar que os dois containers estão rodando**

Run: `docker compose ps`
Expected: duas linhas, ambas com status `running`/`Up`, container `n8n` mapeando `127.0.0.1:5678->5678/tcp` e `waha` mapeando `127.0.0.1:3000->3000/tcp` (loopback apenas, não `0.0.0.0` — ver nota de segurança no Step 1). Se `n8n` aparecer como `Restarting`, o Step 3 não foi aplicado corretamente — confira a posse de `n8n_data`.

- [ ] **Step 6: Verificar acessibilidade HTTP**

Run (de dentro da própria máquina — as portas não são mais alcançáveis pela rede local, apenas via `localhost`/`127.0.0.1`):
```bash
curl -s -o /dev/null -w "n8n: %{http_code}\n" http://localhost:5678
curl -s -o /dev/null -w "waha (sem auth): %{http_code}\n" http://localhost:3000
curl -s -o /dev/null -w "waha (com auth): %{http_code}\n" -u admin:changeme http://localhost:3000/dashboard
```
Expected: `n8n: 200`; `waha (sem auth)` pode retornar `401` (dashboard protegido por padrão — não é falha); `waha (com auth): 200`, `302` ou `301` usando as credenciais definidas no Step 1 (qualquer redirect/sucesso distingue-se claramente de `401`), confirmando que a autenticação está configurada corretamente.

- [ ] **Step 7: Verificar que `n8n_data/` e `waha_data/` foram criados mas ignorados pelo git**

Run: `git status --short`
Expected: `docker-compose.yml` aparece como `??` (untracked); `n8n_data/` e `waha_data/` **não** aparecem (ignorados)

- [ ] **Step 8: Commit**

```bash
cd /home/augusto/Documentos/LAMIA/FC_Agentes/card12
git add docker-compose.yml
git commit -m "feat: adiciona docker-compose com n8n e WAHA"
```

---

### Task 3: Criar a conta inicial do n8n

Não há arquivo de código nesta task — é a etapa de bootstrap da UI do n8n, pré-requisito para a Task 4.

**Files:** nenhum (ação operacional via browser)

**Interfaces:**
- Consumes: n8n acessível em `http://localhost:5678` (Task 2).
- Produces: conta "owner" do n8n criada e autenticada, necessária para instalar nós comunitários (Task 4) e criar workflows (Task 6).

- [ ] **Step 1: Verificar healthcheck do n8n antes de configurar a conta**

Run: `curl -s http://localhost:5678/healthz`
Expected: `{"status":"ok"}`

- [ ] **Step 2: Abrir o setup inicial no navegador**

Acesse `http://localhost:5678`. O n8n deve exibir a tela "Set up owner account" (primeira execução).

- [ ] **Step 3: Completar o cadastro**

Preencha nome, e-mail e senha do usuário owner e conclua o cadastro.

- [ ] **Step 4: Verificar login bem-sucedido**

Expected: após o cadastro, o navegador é redirecionado para o dashboard do n8n (`http://localhost:5678/home/workflows`), sem exibir a tela de setup novamente ao recarregar a página.

Não há commit nesta task (nenhum arquivo do repositório foi alterado; o estado da conta vive dentro do volume `n8n_data/`, que é ignorado pelo git por design — ver Task 1).

---

### Task 4: Instalar o nó comunitário `@devlikeapro/n8n-nodes-waha`

**Files:** nenhum (ação operacional via UI do n8n)

**Interfaces:**
- Consumes: conta do n8n autenticada (Task 3).
- Produces: nós com prefixo "WAHA" disponíveis no painel de nodes do n8n, usados na Task 6 (`WAHA Trigger`, `WAHA` genérico para Send Seen / Send Text).

- [ ] **Step 1: Abrir as configurações de nós comunitários**

No n8n, vá em **Settings** (ícone de engrenagem) → **Community Nodes**.

- [ ] **Step 2: Instalar o pacote**

Clique em **Install a community node**, cole `@devlikeapro/n8n-nodes-waha`, marque a caixa de concordância com os termos e confirme.

- [ ] **Step 3: Verificar a instalação**

Expected: o pacote `@devlikeapro/n8n-nodes-waha` aparece na lista de "Installed" em Community Nodes, sem erro de instalação.

- [ ] **Step 4: Verificar que os nós aparecem no editor de workflow**

Crie um novo workflow em branco, clique em "+" para adicionar um node e busque por "WAHA".
Expected: aparecem pelo menos os nós `WAHA Trigger` e `WAHA`.

Não há commit nesta task (estado vive no volume `n8n_data/`).

---

### Task 5: Parear o WhatsApp na sessão `default` da WAHA

**Files:** nenhum (ação operacional: escanear QR Code com o celular)

**Interfaces:**
- Consumes: WAHA acessível em `http://localhost:3000` (Task 2).
- Produces: sessão `default` da WAHA com status `WORKING`, necessária para a WAHA conseguir enviar/receber mensagens usadas nas Tasks 6 e 7.

- [ ] **Step 1: Verificar o estado inicial da sessão**

Run: `curl -s -u admin:changeme http://localhost:3000/api/sessions` (credenciais definidas na Task 2 — sem `-u`, a API responde `401`)
Expected: um JSON contendo a sessão `default`, provavelmente com `"status": "STOPPED"` (ainda não iniciada).

- [ ] **Step 2: Abrir o dashboard da WAHA**

Acesse `http://localhost:3000/dashboard` e faça login com as credenciais definidas na Task 2 (`admin` / `changeme`).

- [ ] **Step 3: Iniciar a sessão `default`**

Na sessão `default`, clique em **Start**/**Login**. A WAHA deve exibir um QR Code.

- [ ] **Step 4: Escanear o QR Code**

No celular: WhatsApp → Menu/Configurações → **Dispositivos conectados** → **Conectar dispositivo** → escanear o QR Code exibido na tela.

- [ ] **Step 5: Verificar que a sessão conectou**

Run: `curl -s -u admin:changeme http://localhost:3000/api/sessions/default`
Expected: `"status": "WORKING"` no JSON de resposta.

Não há commit nesta task (estado da sessão vive no volume `waha_data/`, ignorado pelo git por design).

---

### Task 6: Construir o workflow "Ping-Pong" no n8n

**Files:** nenhum arquivo de repositório (o workflow é um artefato interno do n8n, persistido em `n8n_data/`, fora do controle de versão por decisão da Task 1)

**Interfaces:**
- Consumes: nós `WAHA Trigger` e `WAHA` instalados (Task 4); sessão `default` `WORKING` (Task 5); resolução de nome `http://waha:3000` dentro da rede do compose (Task 2).
- Produces: workflow em modo de teste capaz de capturar um evento de mensagem recebida e responder — validado com "Test step" nesta task; ativado em produção na Task 7.

- [ ] **Step 1: Criar o node `WAHA Trigger`**

No workflow, adicione o node `WAHA Trigger`. Copie a **Test Webhook URL** gerada por ele (formato `http://localhost:5678/webhook-test/<id>`).

- [ ] **Step 2: Registrar a Test Webhook URL na sessão da WAHA**

No dashboard da WAHA (`http://localhost:3000/dashboard`, login `admin`/`changeme`), edite a sessão `default` → **Webhooks** → adicione a URL copiada, substituindo `localhost` por `n8n` (nome do serviço no compose): `http://n8n:5678/webhook-test/<id>`.

- [ ] **Step 3: Capturar um evento de teste**

No n8n, clique em **Test step** no node `WAHA Trigger`. Envie uma mensagem para si mesmo no WhatsApp conectado.
Expected: o n8n captura o evento e mostra o payload recebido (contendo `payload.from`, `payload.body`, `payload.id`, `session`).

- [ ] **Step 4: Adicionar o node `Edit Fields (Set)`**

Conecte-o à saída do `WAHA Trigger`. Configure os campos:
- `session` ← `{{ $json.payload.session }}` (ou `{{ $json.session }}`, conforme o payload capturado no Step 3)
- `quem_mandou` ← `{{ $json.payload.from }}`
- `mensagem` ← `{{ $json.payload.body }}`
- `id_mensagem` ← `{{ $json.payload.id }}`

- [ ] **Step 5: Adicionar o node `WAHA` configurado para "Send Seen"**

Conecte-o à saída do `Edit Fields`. Crie a credencial WAHA apontando para `http://waha:3000` (nome do serviço, não `host.docker.internal` — ver Global Constraints), usando a API key definida na Task 2 (`changeme-api-key`). Configure a operação **Send Seen** com:
- `session` ← `{{ $json.session }}`
- `chatId` ← `{{ $json.quem_mandou }}`
- `messageId` ← `{{ $json.id_mensagem }}`

Remova o campo `participant` (não usado em chats individuais).

- [ ] **Step 6: Adicionar o node `WAHA` configurado para "Send Text"**

Conecte-o à saída do "Send Seen". Configure a operação **Send Text** com:
- `session` ← `{{ $json.session }}`
- `chatId` ← `{{ $json.quem_mandou }}`
- `text` ← `Você digitou: {{ $json.mensagem }}`

> **Cuidado (erro real cometido na execução):** é fácil confundir `chatId` com `id_mensagem` nesse node — os dois são strings parecidas e ficam lado a lado no `Edit Fields`. Usar `id_mensagem` como `chatId` faz a WAHA tentar resolver um "contato" que na verdade é um ID de mensagem, o que nunca funciona e se manifesta como timeout silencioso (sem erro claro) minutos depois. Confira o campo com atenção antes de testar.

- [ ] **Step 7: Verificar o fluxo completo em modo de teste**

Clique em **Test workflow**, envie uma mensagem de teste pelo WhatsApp conectado.
Expected: a execução no n8n mostra os 4 nodes com status de sucesso (verde), e o WhatsApp recebe automaticamente a resposta `Você digitou: <mensagem enviada>`.

Não há commit nesta task (workflow persiste em `n8n_data/`).

---

### Task 7: Ativar o workflow em produção e validar end-to-end

**Files:** nenhum

**Interfaces:**
- Consumes: workflow validado em modo de teste (Task 6).
- Produces: automação ativa e respondendo a mensagens reais — este é o critério de aceite final do projeto.

- [ ] **Step 1: Ativar o workflow**

No n8n, alterne o toggle **Active** do workflow para ligado (canto superior direito do editor).

- [ ] **Step 2: Obter a Production Webhook URL**

No node `WAHA Trigger`, copie a **Production Webhook URL** (formato `http://localhost:5678/webhook/<id>`, sem o sufixo `-test`).

- [ ] **Step 3: Atualizar o webhook da sessão WAHA para a URL de produção**

No dashboard da WAHA (login `admin`/`changeme`), edite a sessão `default` → **Webhooks** → substitua a URL de teste pela URL de produção, novamente trocando `localhost` por `n8n`: `http://n8n:5678/webhook/<id>`.

- [ ] **Step 4: Validar de um número diferente**

De outro celular (não o número conectado à WAHA), envie a mensagem `oi` para o número conectado ao WhatsApp.

- [ ] **Step 5: Verificar a resposta automática (critério de aceite final)**

Expected: o número de destino recebe automaticamente a resposta `Você digitou: oi`, sem qualquer intervenção manual — confirma o fluxo completo WhatsApp → WAHA → n8n → WAHA → WhatsApp funcionando de ponta a ponta.

**Status real (agosto de 2026):** a cadeia completa (Trigger → Edit Fields → Send Seen → Send Text) foi validada e funciona corretamente de ponta a ponta, com entrega confirmada em teste real feito por outra pessoa a partir de um número diferente.

**Causa raiz real dos problemas de entrega:** uma inspeção posterior do JSON completo do workflow (não apenas da UI) revelou que o node "Send a text message" ainda usava `chatId={{ $('Edit Fields').item.json.id_mensagem }}` — ou seja, o ID da mensagem recebida, não o contato de destino (`quem_mandou`). A correção aplicada anteriormente não tinha sido salva/persistida como se acreditava. Depois de corrigir esse campo para `quem_mandou`, a entrega passou a funcionar de forma consistente nos testes. Ver "⚠️→✅ Limitação conhecida (resolvida)" abaixo para o histórico completo da investigação, incluindo a ressalva de que parte do comportamento antes atribuído a um bug upstream da WAHA pode ter sido, na verdade, esse `chatId` incorreto mascarado como problema de biblioteca.

Não há commit nesta task (mudança foi feita diretamente no workflow do n8n, que vive no volume `n8n_data/`, fora do controle de versão deste repositório). O projeto está funcionalmente completo e validado. A lógica de resposta além do ping-pong fica para uma iteração futura (ver "Fora de escopo" em `PLAN_CARD12.md`).

---

## Dicas de Operação (pós-implementação)

**Depois de QUALQUER restart do container `waha`** (`docker compose restart waha`, `docker compose up -d` após editar o compose, reboot da máquina), reaplique a config da store do NOWEB — é um bug conhecido da WAHA essa config não sobreviver ao restart, e sem ela o `sendText` pode demorar minutos para contatos `@lid`:

```bash
curl -s -X PUT -H "X-Api-Key: changeme-api-key" -H "Content-Type: application/json" \
  -d '{
    "config": {
      "webhooks": [
        {"url": "http://n8n:5678/webhook/<id-do-webhook-de-producao>/waha", "events": ["message"]}
      ],
      "noweb": {"store": {"enabled": true, "fullSync": true}}
    }
  }' \
  http://localhost:3000/api/sessions/default
```

Verifique com `curl -H "X-Api-Key: changeme-api-key" http://localhost:3000/api/sessions/default` — a resposta deve mostrar `"status":"WORKING"` e o `config.noweb.store.enabled: true`.

## ⚠️→✅ Limitação conhecida (RESOLVIDA): entrega não confiável do `sendText`

Durante a validação end-to-end, observamos que o `sendText` podia retornar sucesso (`201`, com um `key`/`id` de mensagem válido) **sem a mensagem chegar de verdade** no WhatsApp de destino. Investigação na época:

- **Sintoma nos logs:** `docker logs waha` mostrava `timed out waiting for message` repetindo para o mesmo `msgId` a cada ~2 minutos, às vezes acompanhado de `USync fetch yielded no results for pending PNs`.
- **Causa suposta na época:** um problema upstream nas bibliotecas open-source do protocolo WhatsApp (`Baileys`/NOWEB, `whatsapp-web.js`/WEBJS), ligado à migração do WhatsApp para o identificador `@lid`.
- **O que essa investigação errou:** na época, o bug do `chatId` (node "Send a text message" usando `id_mensagem` — um ID de mensagem — em vez de `quem_mandou` — o contato de destino) tinha sido considerado "já corrigido e confirmado à parte". Uma inspeção posterior do JSON completo do workflow mostrou que essa correção **não estava de fato salva**: o campo continuava apontando para `id_mensagem`. Isso significa que a WAHA/Baileys estava recebendo uma string de ID de mensagem como se fosse um contato de destino em toda tentativa de envio — o que explica plenamente o padrão de "timed out waiting" e falsos sucessos observados.

**Resolução:** corrigido o `chatId` do node "Send a text message" para `={{ $('Edit Fields').item.json.quem_mandou }}`. Após a correção, testes de ponta a ponta (incluindo teste feito por terceiro, de número diferente) confirmaram entrega rápida e consistente.

**Ressalva honesta:** não é possível descartar 100% que também existisse um problema upstream genuíno coexistindo com o bug do `chatId` — a investigação original encontrou sintomas (`identity key changed`, issues abertas nos repositórios oficiais sobre `@lid`) que são reais e documentados por terceiros, mesmo que não fossem a causa principal aqui. Se sintomas semelhantes voltarem a aparecer mesmo com o `chatId` correto, os passos de mitigação abaixo continuam válidos: reiniciar a sessão e reaplicar a config da store do NOWEB.

```bash
curl -s -X POST -H "X-Api-Key: changeme-api-key" http://localhost:3000/api/sessions/default/restart
```

**Se quiser aprofundar essa ressalva no futuro:** acompanhar os repositórios `devlikeapro/waha` e `WhiskeySockets/Baileys` no GitHub por menções a `@lid`/`USync`.

## Dicas de Operação (pós-implementação)

**Depois de QUALQUER restart do container `waha`** (`docker compose restart waha`, `docker compose up -d` após editar o compose, reboot da máquina), reaplique a config da store do NOWEB — é um bug conhecido da WAHA essa config não sobreviver ao restart, e sem ela o `sendText` pode demorar minutos para contatos `@lid`:

```bash
curl -s -X PUT -H "X-Api-Key: changeme-api-key" -H "Content-Type: application/json" \
  -d '{
    "config": {
      "webhooks": [
        {"url": "http://n8n:5678/webhook/<id-do-webhook-de-producao>/waha", "events": ["message"]}
      ],
      "noweb": {"store": {"enabled": true, "fullSync": true}}
    }
  }' \
  http://localhost:3000/api/sessions/default
```

Verifique com `curl -H "X-Api-Key: changeme-api-key" http://localhost:3000/api/sessions/default` — a resposta deve mostrar `"status":"WORKING"` e o `config.noweb.store.enabled: true`.

---

## Referências

Fontes pesquisadas (via WebSearch) durante a investigação dos bugs do WEBJS e do NOWEB documentados neste plano:

- **`getChats` retornando 500 no engine WEBJS** — https://github.com/devlikeapro/waha/issues/486 (issue no repositório da WAHA, bug de inicialização do Store ligado a mudanças no frontend do WhatsApp Web, corrigido em versões mais novas da WAHA/`whatsapp-web.js`).
- **`sendText` falhando no engine WEBJS** (`Cannot read properties of undefined (reading 'markedUnread')`, reportado localmente como `TypeError: t` em build minificado) — classe de bug recorrente, sem correção estável única, documentada em várias issues do mesmo repositório: https://github.com/devlikeapro/waha/issues/1810, https://github.com/devlikeapro/waha/issues/1814, https://github.com/devlikeapro/waha/issues/1820, https://github.com/devlikeapro/waha/issues/1827, https://github.com/devlikeapro/waha/issues/1868, https://github.com/devlikeapro/waha/issues/1905.
- **Fila de envio travada por retry infinito no engine NOWEB (`timed out waiting for message`)** — https://github.com/WhiskeySockets/Baileys/issues/853 (issue no repositório da biblioteca `Baileys`, usada pelo engine NOWEB).
- **Documentação oficial da WAHA** — https://waha.devlike.pro/ — usada para confirmar comportamento de tags de imagem, engines disponíveis (WEBJS, NOWEB, GOWS) e configuração de sessão/store via API.
- **Repositório da `@devlikeapro/n8n-nodes-waha`** — https://github.com/devlikeapro/n8n-nodes-waha — nó comunitário do n8n usado neste projeto.

Nota: os links dos repositórios `devlikeapro/waha` e `WhiskeySockets/Baileys` foram usados de forma mais ampla, além das issues específicas listadas acima, para acompanhar discussões sobre a migração do WhatsApp para o identificador `@lid`.

---

## Self-Review

**Cobertura do PLAN_CARD12.md:**
- Passo 1 (docker-compose) → Task 2. ✓
- Passo 2 (.gitignore) → Task 1. ✓
- Passo 3 (conta n8n) → Task 3. ✓
- Passo 4 (nó comunitário) → Task 4. ✓
- Passo 5 (parear WhatsApp) → Task 5. ✓
- Passo 6 (workflow ping-pong) → Task 6. ✓
- Passo 7 (ativar produção + validação end-to-end) → Task 7. ✓

**Placeholders:** nenhum "TBD"/"implementar depois" — cada step tem conteúdo concreto (YAML completo, comandos `curl`/`docker compose` com saída esperada, valores exatos de configuração de nodes).

**Consistência de nomes:** `session`, `quem_mandou`, `mensagem`, `id_mensagem` usados de forma idêntica entre Task 6 Step 4 (definição) e Steps 5–6 (consumo). URLs de webhook (`webhook-test` na Task 6, `webhook` na Task 7) diferenciadas corretamente. Nome de serviço `n8n`/`waha` usado de forma consistente com a suposição declarada no `PLAN_CARD12.md` e nas Global Constraints.
