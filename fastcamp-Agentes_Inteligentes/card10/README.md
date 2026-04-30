# Google ADK Masterclass - Desenvolvimento de Agentes

Este diretório contém a implementação prática baseada no framework **Google ADK**, explorando desde a criação de agentes fundamentais até arquiteturas complexas de sistemas multiagentes.

## Visão Geral

As atividades aqui documentadas abordam o ciclo de vida completo de um agente, incluindo gerenciamento de estado, persistência em banco de dados, callbacks de segurança e orquestração hierárquica.

---

## Agentes Desenvolvidos

### 1. Agentes de Propósito Único
- **Greeting Agent:** Estrutura inicial que valida o conceito de "personalidade" e instruções de comportamento.
- **Tools Agent:** Agente capaz de decidir autonomamente entre ferramentas integradas (Google Search) e funções Python customizadas (ex: `get_current_time`).
- **Dad Joke Agent:** Demonstração de interoperabilidade usando a biblioteca **LiteLLM** para conectar o ADK a modelos externos como GPT-4 (OpenAI) e Claude (Anthropic).

### 2. Gestão de Contexto e Persistência
- **Memory Agent:** Implementação de persistência assíncrona utilizando **SQLite**, permitindo que o agente armazene e recupere lembretes entre diferentes sessões de conversação.
- **Structured Output:** Configuração de esquemas (JSON) para garantir que as saídas do agente sejam previsíveis e prontas para integração em outros sistemas.

### 3. Arquiteturas de Orquestração
- **Sistema Hierárquico:** Um **Root Agent** (gerente) que avalia solicitações e delega tarefas para subagentes especializados (Análise de Notícias, Ações ou Piadas Nerds).
- **Estado Compartilhado:** Sistema de atendimento ao cliente onde múltiplos subagentes (vendas, suporte, políticas) acessam e modificam um contexto único, evitando que o usuário repita informações.

---
## Camadas de Controle (Callbacks)
Foram implementados mecanismos de interceptação em três níveis para garantir a robustez do sistema:

| **Nível**  | **Callback Before**                         | **Callback After**                          |
| ---------- | ------------------------------------------- | ------------------------------------------- |
| **Agente** | Preparação de recursos e dados do usuário.  | Registro de logs e validação de resultados. |
| **Modelo** | Filtragem de conteúdo (Segurança/Bloqueio). | Sanitização e formatação de respostas.      |
| **Tools**  | Normalização de argumentos de entrada.      | Enriquecimento de resultados com metadados. |

---
Este projeto faz parte do **Fastcamp de Agentes Inteligentes** do laboratório **LAMIA**.
