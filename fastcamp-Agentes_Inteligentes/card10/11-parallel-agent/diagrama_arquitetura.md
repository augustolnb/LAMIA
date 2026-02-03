# Diagrama de Arquitetura - Parallel Agent (System Monitor)

```mermaid
flowchart TB
    subgraph RootAgent["🤖 Root Agent"]
        manager["<b>system_monitor_agent</b><br><i>SequentialAgent</i><br>Monitor de sistema"]
    end

    manager -->|"1️⃣ sub_agent"| gatherer
    manager -->|"2️⃣ sub_agent"| synthesizer

    subgraph SequentialFlow["📋 Pipeline Sequencial"]
        subgraph ParallelGatherer["⚡ system_info_gatherer (ParallelAgent)"]
            direction LR
            gatherer_desc["<b>Função:</b> Coleta simultânea de métricas<br><b>Tipo:</b> ParallelAgent<br><b>Execução:</b> Todos os sub-agentes rodam ao mesmo tempo"]
            
            subgraph Collectors["📊 Agentes Coletores"]
                cpu["<b>CpuInfoAgent</b><br><i>gpt-4.1-nano</i><br>output: cpu_info"]
                memory["<b>MemoryInfoAgent</b><br><i>gpt-4.1-nano</i><br>output: memory_info"]
                disk["<b>DiskInfoAgent</b><br><i>gpt-4.1-nano</i><br>output: disk_info"]
            end
        end

        synthesizer["<b>SystemReportSynthesizer</b><br><i>claude-haiku-4-5</i><br>Sintetizador de Relatório"]
    end

    cpu -->|"cpu_info"| synthesizer
    memory -->|"memory_info"| synthesizer
    disk -->|"disk_info"| synthesizer

    %% --- Estilo do ROOT (Manager) ---
    style RootAgent fill:#ffffff,stroke:#01579b,stroke-width:2px,color:#000
    style manager fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000

    %% --- Estilo do Pipeline Sequencial ---
    style SequentialFlow fill:#ffffff,stroke:#01579b,stroke-width:1px,color:#000

    %% --- Estilo do ParallelAgent (Gatherer) ---
    style ParallelGatherer fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000
    style gatherer_desc fill:#ffe0b2,stroke:#e65100,stroke-width:1px,color:#000
    style Collectors fill:#ffffff,stroke:#e65100,stroke-width:1px,color:#000

    %% --- Estilo dos Coletores (usam GPT) ---
    style cpu fill:#fff3e0,stroke:#e65100,stroke-width:1px,color:#000
    style memory fill:#fff3e0,stroke:#e65100,stroke-width:1px,color:#000
    style disk fill:#fff3e0,stroke:#e65100,stroke-width:1px,color:#000

    %% --- Estilo do Synthesizer (usa Claude) ---
    style synthesizer fill:#e1f5fe,stroke:#01579b,stroke-width:1px,color:#000
```

---

## 🔄 O que é o `system_info_gatherer`?

O **`system_info_gatherer`** é um **ParallelAgent** — um tipo especial de agente orquestrador que executa múltiplos sub-agentes **simultaneamente** ao invés de sequencialmente.

### Características Principais

| Propriedade | Valor |
|-------------|-------|
| **Nome** | `system_info_gatherer` |
| **Tipo** | `ParallelAgent` |
| **Modelo LLM** | Nenhum (apenas orquestra) |
| **Sub-agentes** | 3 agentes coletores |
| **Execução** | Paralela (simultânea) |

### Função no Pipeline

```
📥 Usuário solicita relatório do sistema
         ↓
    ┌────────────────────────────────────┐
    │     system_info_gatherer           │
    │        (ParallelAgent)             │
    ├────────────────────────────────────┤
    │  Executa SIMULTANEAMENTE:          │
    │                                    │
    │  ┌──────────┐ ┌──────────┐ ┌──────────┐
    │  │ CPU Info │ │ Memory   │ │ Disk     │
    │  │  Agent   │ │ Info     │ │ Info     │
    │  │ (GPT)    │ │ (GPT)    │ │ (GPT)    │
    │  └────┬─────┘ └────┬─────┘ └────┬─────┘
    │       │            │            │
    │       ▼            ▼            ▼
    │   cpu_info    memory_info   disk_info
    │       │            │            │
    └───────┴────────────┴────────────┘
                    ↓
         (dados salvos no estado)
                    ↓
    ┌────────────────────────────────────┐
    │   SystemReportSynthesizer          │
    │         (Claude)                   │
    │   Combina: {cpu_info}              │
    │            {memory_info}           │
    │            {disk_info}             │
    └────────────────────────────────────┘
                    ↓
📤 Relatório consolidado para o usuário
```

### Por que usar Parallel ao invés de Sequential?

| Aspecto | Sequential | Parallel (atual) |
|---------|-----------|------------------|
| **Tempo** | CPU → Memory → Disk (soma dos tempos) | Todos ao mesmo tempo |
| **Eficiência** | Mais lento | ~3x mais rápido |
| **Dependência** | Um agente pode depender do anterior | Agentes independentes |
| **Uso ideal** | Quando há dependência entre etapas | Quando tarefas são independentes |

### Modelos Utilizados

| Agente | Modelo | Justificativa |
|--------|--------|---------------|
| **CpuInfoAgent** | `gpt-4.1-nano` | Tarefas simples de coleta |
| **MemoryInfoAgent** | `gpt-4.1-nano` | Tarefas simples de coleta |
| **DiskInfoAgent** | `gpt-4.1-nano` | Tarefas simples de coleta |
| **SystemReportSynthesizer** | `claude-haiku-4-5` | Síntese complexa de múltiplas fontes |

> **💡 Estratégia**: Modelos menores e mais baratos (GPT nano) para coleta paralela de dados, modelo mais capaz (Claude) para a síntese final que requer compreensão mais profunda.
