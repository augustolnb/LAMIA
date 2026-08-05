# Plano: Agente WhatsApp local com n8n + WAHA (Docker)

## Contexto

O diretório do projeto (`/home/augusto/Documentos/LAMIA/FC_Agentes/card12`) está vazio, contendo apenas `TUTORIAL_WAHA.md` (o roteiro de referência) e `CLAUDE.md`. O tutorial descreve uma configuração 100% manual via GUI do Docker Desktop: buscar imagens, clicar em "Pull"/"Run", preencher campos de porta/volume/env var na interface, e depois montar um workflow visual no n8n.

**Decisão confirmada com o usuário:** em vez de reproduzir os cliques manuais no Docker Desktop, a subida dos containers (n8n + WAHA) será automatizada com um `docker-compose.yml` versionado no repositório — isso é reprodutível, revisável e elimina a etapa manual de "Optional settings" do tutorial. Os passos que são inerentemente interativos (parear o WhatsApp via QR Code, instalar o nó comunitário pela UI do n8n, montar o workflow visual, ativar o workflow) continuam manuais, pois é assim que essas ferramentas funcionam — não há ganho em tentar automatizá-los agora (principio da simplicidade).

O comportamento final do agente (lógica de resposta) fica **em aberto** para definição futura. Este plano entrega a infraestrutura pronta e um fluxo de teste "ping-pong" (idêntico ao do tutorial) apenas como **critério de verificação end-to-end** — prova de que WhatsApp → WAHA → n8n → WhatsApp está funcionando.

### Suposição explícita (principio 1)
Os dois containers serão colocados na mesma rede do `docker-compose` e se comunicarão pelo **nome do serviço** (ex: `http://n8n:5678/webhook/...`) em vez de `host.docker.internal`, que o tutorial usa por rodarem containers soltos (sem compose). Isso é funcionalmente equivalente, mais simples e evita a dependência de resolução de `host.docker.internal` no Docker Desktop for Linux. Se preferir manter `host.docker.internal` (por exemplo para bater exatamente com o tutorial), avise antes da execução — é uma troca de uma linha de configuração.

## Passo a passo

1. **Criar `docker-compose.yml`** na raiz do projeto com dois serviços, replicando os parâmetros do tutorial:
   - `n8n`: imagem `n8nio/n8n`, porta `5678:5678`, volume `./n8n_data:/home/node/.n8n`, env `GENERIC_TIMEZONE=America/Sao_Paulo`.
   - `waha`: imagem `devlikeapro/waha`, porta `3000:3000`, volume `./waha_data:/tmp`, envs `WHATSAPP_DEFAULT_ENGINE=WEBJS` e `WHATSAPP_HOOK_EVENTS=message`. `WHATSAPP_HOOK_URL` fica com um placeholder (ex: `http://n8n:5678/webhook/`) — o path final do webhook só é conhecido depois de criar o node `WAHA Trigger` no n8n (passo 5), então esse valor será ajustado então.
   - Ambos os serviços na mesma rede padrão do compose (default bridge criada automaticamente), permitindo resolução por nome de serviço.
   - `verify`: `docker compose up -d` sobe sem erros; `docker compose ps` mostra os dois containers `running`; `curl -s -o /dev/null -w "%{http_code}" http://localhost:5678` e `http://localhost:3000` retornam 200.

2. **Criar `.gitignore`** para excluir `n8n_data/` e `waha_data/` (dados de runtime/sessão, não devem ser versionados).
   - `verify`: `git status` (quando o repo for inicializado) não lista essas pastas como untracked depois do primeiro `up`.

3. **Subir os containers e criar conta no n8n** — abrir `http://localhost:5678`, completar cadastro inicial.
   - `verify`: login no n8n bem-sucedido, dashboard carrega.

4. **Instalar o nó comunitário da WAHA no n8n** — Settings > Community Nodes > Install `@devlikeapro/n8n-nodes-waha`.
   - `verify`: nós com prefixo "WAHA" aparecem no painel de nodes do n8n.

5. **Parear o WhatsApp na WAHA** — abrir `http://localhost:3000` → Dashboard → iniciar sessão `default` → escanear QR Code pelo celular.
   - `verify`: `GET http://localhost:3000/api/sessions` (ou o dashboard) mostra a sessão `default` com status `WORKING`/conectado.

6. **Montar o workflow "Ping-Pong" no n8n**, replicando a seção 6 do tutorial:
   - Node `WAHA Trigger` → copiar a Test Webhook URL, configurá-la como webhook da sessão `default` na WAHA (via dashboard), testar enviando uma mensagem para si mesmo.
   - Node `Edit Fields (Set)` mapeando `session`, `quem_mandou` (`payload.from`), `mensagem` (`payload.body`), `id_mensagem` (`payload.id`).
   - Node `WAHA (Send Seen)` com credencial apontando para `http://waha:3000` (nome do serviço, ver suposição acima), usando `session`, `chatId=quem_mandou`, `messageId=id_mensagem`.
   - Node `WAHA (Send Text)` respondendo com `Você digitou: {{ $json.mensagem }}`.
   - `verify`: "Test step" no n8n captura corretamente o evento ao enviar uma mensagem de teste.

7. **Ativar o workflow em produção** e atualizar o webhook da sessão WAHA para a Production Webhook URL do n8n.
   - `verify` (critério final end-to-end): enviar "oi" de outro número para o WhatsApp conectado e confirmar o recebimento automático de "Você digitou: oi".

## Arquivos a criar
- `docker-compose.yml` — infraestrutura n8n + WAHA
- `.gitignore` — ignora `n8n_data/` e `waha_data/`

## Fora de escopo (deixado para depois, por decisão do usuário)
- Lógica de negócio/resposta do agente além do smoke-test ping-pong.
- Automação da instalação do nó comunitário ou da criação do workflow (permanecem manuais via UI, como no tutorial).
