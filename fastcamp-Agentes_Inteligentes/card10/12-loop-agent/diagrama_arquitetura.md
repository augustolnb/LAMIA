# Diagrama de Arquitetura - Loop Agent (LinkedIn Post Generator)

```mermaid
flowchart TB
    subgraph RootAgent["🤖 Root Agent"]
        manager["<b>LinkedInPostGenerationPipeline</b><br><i>SequentialAgent</i><br>Gerador de posts LinkedIn"]
    end

    manager -->|"1️⃣ sub_agent"| generator
    manager -->|"2️⃣ sub_agent"| loop

    subgraph SequentialFlow["📋 Pipeline Sequencial"]
        generator["<b>InitialPostGenerator</b><br><i>gpt-4.1-nano</i><br>Gera post inicial<br>output: current_post"]

        subgraph LoopAgent["🔄 PostRefinementLoop (LoopAgent)"]
            loop_desc["<b>Função:</b> Refinamento iterativo<br><b>Tipo:</b> LoopAgent<br><b>Max Iterações:</b> 10"]
            
            subgraph LoopCycle["♻️ Ciclo de Refinamento"]
                reviewer["<b>PostReviewer</b><br><i>claude-haiku-4-5</i><br>Avalia qualidade<br>output: review_feedback"]
                refiner["<b>PostRefinerAgent</b><br><i>gpt-4.1-nano</i><br>Aplica melhorias<br>output: current_post"]
            end
        end
    end

    generator -->|"current_post"| reviewer
    reviewer -->|"review_feedback"| refiner
    refiner -->|"current_post (atualizado)"| reviewer

    reviewer -->|"exit_loop()"| FinalOutput["📤 Post Final"]

    %% --- Estilo do ROOT (Manager) ---
    style RootAgent fill:#ffffff,stroke:#01579b,stroke-width:2px,color:#000
    style manager fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000

    %% --- Estilo do Pipeline Sequencial ---
    style SequentialFlow fill:#ffffff,stroke:#01579b,stroke-width:1px,color:#000

    %% --- Estilo do Gerador Inicial (GPT) ---
    style generator fill:#fff3e0,stroke:#e65100,stroke-width:1px,color:#000

    %% --- Estilo do LoopAgent ---
    style LoopAgent fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#000
    style loop_desc fill:#c8e6c9,stroke:#2e7d32,stroke-width:1px,color:#000
    style LoopCycle fill:#ffffff,stroke:#2e7d32,stroke-width:1px,color:#000

    %% --- Estilo do Reviewer (Claude - azul) ---
    style reviewer fill:#e1f5fe,stroke:#01579b,stroke-width:1px,color:#000

    %% --- Estilo do Refiner (GPT - laranja) ---
    style refiner fill:#fff3e0,stroke:#e65100,stroke-width:1px,color:#000

    %% --- Estilo do output final ---
    style FinalOutput fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
```

---

## 🎨 Legenda de Cores por Modelo

| Cor | Modelo | Agentes |
|-----|--------|---------|
| 🟠 Laranja | **GPT** (`gpt-4.1-nano`) | InitialPostGenerator, PostRefinerAgent |
| 🔵 Azul | **Claude** (`claude-haiku-4-5`) | PostReviewer |
| 🟢 Verde | **LoopAgent** (orquestrador) | PostRefinementLoop |

---

## 🔄 O que é um LoopAgent?

O **LoopAgent** é um tipo de orquestrador que executa seus sub-agentes **repetidamente** em ciclo até que uma condição de saída seja atingida ou o número máximo de iterações seja alcançado.

### Características Principais

| Propriedade | Valor |
|-------------|-------|
| **Nome** | `PostRefinementLoop` |
| **Tipo** | `LoopAgent` |
| **Max Iterações** | 10 |
| **Sub-agentes** | Reviewer (Claude) → Refiner (GPT) |
| **Condição de Saída** | Chamada da função `exit_loop()` |

---

## 📊 Fluxo de Execução

```
📥 Usuário solicita geração de post
         ↓
┌────────────────────────────────────┐
│   InitialPostGenerator (GPT)       │
│   Gera o rascunho inicial          │
│   output: current_post             │
└────────────────────────────────────┘
         ↓
┌────────────────────────────────────────────────────────┐
│              PostRefinementLoop (LoopAgent)            │
│                                                        │
│   ┌──────────────────────────────────────────────┐    │
│   │  Iteração 1, 2, 3... (até 10x)               │    │
│   │                                              │    │
│   │  ┌─────────────────┐                         │    │
│   │  │  PostReviewer   │◄─────────────────┐      │    │
│   │  │  (CLAUDE)       │                  │      │    │
│   │  │  Avalia post    │                  │      │    │
│   │  │  Usa tools:     │                  │      │    │
│   │  │  - count_chars  │                  │      │    │
│   │  │  - exit_loop    │                  │      │    │
│   │  └────────┬────────┘                  │      │    │
│   │           │                           │      │    │
│   │           ▼                           │      │    │
│   │     ┌─────────────┐                   │      │    │
│   │     │ Post OK?    │───SIM───► exit_loop()    │    │
│   │     └──────┬──────┘                          │    │
│   │            │ NÃO                             │    │
│   │            ▼                                 │    │
│   │  ┌─────────────────┐                         │    │
│   │  │ PostRefiner     │                         │    │
│   │  │ (GPT)           │                         │    │
│   │  │ Aplica feedback │─────────────────────────┘    │
│   │  └─────────────────┘                              │
│   │                                                   │
│   └───────────────────────────────────────────────────┘
│                                                        │
└────────────────────────────────────────────────────────┘
         ↓
📤 Post final refinado para o usuário
```

---

## 🧠 Estratégia de Modelos

| Agente | Modelo | Justificativa |
|--------|--------|---------------|
| **InitialPostGenerator** | GPT | Geração criativa de conteúdo |
| **PostReviewer** | Claude | Avaliação crítica e uso de ferramentas |
| **PostRefinerAgent** | GPT | Aplicação de melhorias no texto |

> **💡 Lógica**: O **Claude** é usado para **avaliar criticamente** o conteúdo e decidir quando encerrar o loop, enquanto o **GPT** é usado para tarefas **criativas de escrita** (gerar e refinar o post).

---

## 🛠️ Ferramentas do Reviewer

O agente revisor (Claude) possui duas ferramentas:

| Ferramenta | Função |
|------------|--------|
| `count_characters()` | Verifica se o post está entre 1000-1500 caracteres |
| `exit_loop()` | Encerra o loop quando o post atinge todos os requisitos |

---

## 🔁 Comparativo com Outros Padrões

| Padrão | Execução | Uso Ideal |
|--------|----------|-----------|
| **Sequential** | A → B → C (uma vez) | Pipeline linear com dependências |
| **Parallel** | A, B, C (simultâneo) | Tarefas independentes |
| **Loop** | (A → B) × N (repetido) | Refinamento iterativo até atingir qualidade |
