# Diagrama Multi-Agent System

Este diagrama representa a estrutura hierárquica do sistema multi-agente implementado na pasta `7-multi-agent`.

## Visão Geral da Arquitetura

```mermaid
flowchart TB
    subgraph ROOT["🎯 Root Agent"]
        manager["<b>manager</b><br/><i>gemini-2.0-flash</i><br/>Gerencia e delega tarefas"]
    end
    
    subgraph SUB_AGENTS["📋 Sub-Agents (Delegação Completa)"]
        stock["<b>stock_analyst</b><br/><i>gemini-2.0-flash</i><br/>Análise de ações"]
        funny["<b>funny_nerd</b><br/><i>gemini-2.0-flash</i><br/>Piadas nerds"]
    end
    
    subgraph AGENT_TOOLS["🔧 Agent Tools (Usado como Ferramenta)"]
        news["<b>news_analyst</b><br/><i>gemini-2.0-flash</i><br/>Análise de notícias"]
    end
    
    subgraph TOOLS["⚡ Tools Diretas"]
        time["<b>get_current_time</b><br/>Horário atual"]
    end
    
    manager -->|"sub_agents[]"| stock
    manager -->|"sub_agents[]"| funny
    manager -.->|"AgentTool()"| news
    manager -.->|"tools[]"| time
    
    subgraph STOCK_TOOLS["Tools do Stock Analyst"]
        get_stock["get_stock_price()"]
    end
    
    subgraph FUNNY_TOOLS["Tools do Funny Nerd"]
        get_joke["get_nerd_joke()"]
    end
    
    subgraph NEWS_TOOLS["Tools do News Analyst"]
        google["google_search"]
    end
    
    stock --> get_stock
    funny --> get_joke
    news --> google

    style ROOT fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    style SUB_AGENTS fill:#fff3e0,stroke:#e65100,stroke-width:2px
    style AGENT_TOOLS fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    style TOOLS fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
```

## Legenda

| Tipo de Conexão | Descrição |
|-----------------|-----------|
| `→` (seta sólida) | **Sub-Agent**: Delegação completa - o sub-agente assume o controle da resposta |
| `⇢` (seta pontilhada) | **AgentTool**: O agente é usado como ferramenta - retorna resultado ao manager |

## Estrutura de Arquivos

```mermaid
graph LR
    subgraph FOLDER["7-multi-agent/"]
        readme["README.md"]
        subgraph MANAGER["manager/"]
            agent["agent.py<br/>(root_agent)"]
            init["__init__.py"]
            env[".env"]
            subgraph SUB["sub_agents/"]
                subgraph SA1["stock_analyst/"]
                    sa1_agent["agent.py"]
                end
                subgraph SA2["funny_nerd/"]
                    sa2_agent["agent.py"]
                end
                subgraph SA3["news_analyst/"]
                    sa3_agent["agent.py"]
                end
            end
            subgraph TOOLS_DIR["tools/"]
                tools_file["tools.py"]
            end
        end
    end
    
    style FOLDER fill:#fff,stroke:#333
    style MANAGER fill:#e3f2fd,stroke:#1565c0
    style SUB fill:#fff8e1,stroke:#ff8f00
```

## Fluxo de Interação

```mermaid
sequenceDiagram
    participant U as 👤 Usuário
    participant M as 🎯 Manager
    participant S as 📈 Stock Analyst
    participant F as 😄 Funny Nerd
    participant N as 📰 News Analyst
    participant T as ⏰ get_current_time

    U->>M: "Qual o preço da GOOG?"
    M->>S: Delega (sub_agent)
    S-->>M: Assume controle
    S->>U: Retorna preço da ação

    U->>M: "Conta uma piada de Python"
    M->>F: Delega (sub_agent)
    F-->>M: Assume controle
    F->>U: Conta a piada

    U->>M: "Quais as notícias de hoje?"
    M->>N: Chama como tool (AgentTool)
    N-->>M: Retorna resultado
    M->>U: Formata e responde

    U->>M: "Que horas são?"
    M->>T: Chama ferramenta
    T-->>M: Retorna horário
    M->>U: Informa o horário
```

## Resumo dos Agentes

| Agente | Tipo | Função | Tools |
|--------|------|--------|-------|
| **manager** | Root Agent | Coordena e delega tarefas | `AgentTool(news_analyst)`, `get_current_time` |
| **stock_analyst** | Sub-Agent | Análise de preços de ações | `get_stock_price()` |
| **funny_nerd** | Sub-Agent | Conta piadas nerds | `get_nerd_joke()` |
| **news_analyst** | AgentTool | Busca e analisa notícias | `google_search` |
