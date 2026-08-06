# Agente WhatsApp local com n8n + WAHA

Agente de automação de WhatsApp rodando 100% local: recebe mensagens, marca como lidas e responde automaticamente, usando [WAHA](https://waha.devlike.pro/) (WhatsApp HTTP API) para falar com o WhatsApp e [n8n](https://n8n.io/) para orquestrar a lógica.

## Como funciona

```
WhatsApp (quem manda) → WAHA → n8n (webhook) → WAHA → WhatsApp (resposta automática)
```

1. Alguém manda uma mensagem para o número conectado.
2. A WAHA recebe e repassa via webhook para um workflow no n8n.
3. O workflow extrai remetente, texto e ID da mensagem, marca como lida (`Send Seen`) e responde (`Send Text`).

## Infraestrutura

Tudo sobe com um único comando, via `docker-compose.yml`:

```bash
mkdir -p n8n_data waha_data   # evita bug de permissão na primeira subida
docker compose up -d
```

- **n8n** — `http://localhost:5678`
- **WAHA** — `http://localhost:3000`

Os dois serviços conversam entre si pelo nome do serviço no Docker (`waha`, `n8n`), sem depender de `host.docker.internal`.

## Setup (resumo)

1. Suba os containers.
2. Crie uma conta no n8n.
3. Instale o nó comunitário `@devlikeapro/n8n-nodes-waha` (Settings → Community Nodes).
4. Pareie o WhatsApp escaneando o QR Code no dashboard da WAHA (`http://localhost:3000`).
5. Monte o workflow: `WAHA Trigger → Edit Fields → Send Seen + Send Text`.
6. Ative o workflow e aponte o webhook da sessão WAHA para a URL de produção do n8n.

Passo a passo completo em [`Relatório 12 - Lucas Augusto.pdf`](Relatório%2012%20-%20Lucas%20Augusto.pdf).

## Principais problemas encontrados

- **Crash loop no n8n (EACCES):** o Docker criava a pasta de dados como `root`, mas o container roda como usuário `node`. Corrigido criando as pastas manualmente antes do `docker compose up`.
- **Engine WEBJS instável:** a engine padrão da WAHA (automação de navegador) quebrava ao listar conversas e ao enviar mensagens — bugs conhecidos e sem correção estável no momento da implementação. Resolvido trocando para a engine **NOWEB**, que fala o protocolo do WhatsApp diretamente.
- **Mensagens "enviadas" que não chegavam:** a causa raiz era um campo mal configurado no node de envio (`chatId` apontando para o ID da mensagem em vez do contato de destino). Depois de corrigido, a entrega passou a ser rápida e consistente.

## Status

Funcional e validado de ponta a ponta. A lógica de resposta é um teste "ping-pong" (ecoa a mensagem recebida) — uma lógica de resposta mais elaborada fica para uma iteração futura.
