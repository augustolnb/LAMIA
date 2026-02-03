# Diagrama de Arquitetura - Sequential Agent

```mermaid
flowchart TB
    subgraph RootAgent["🤖 Root Agent"]
        manager["<b>LeadQualificationPipeline</b><br><i>SequentialAgent</i><br>Pipeline de qualificação de leads"]
    end

    manager -->|"1️⃣ sub_agent"| validator
    manager -->|"2️⃣ sub_agent"| scorer
    manager -->|"3️⃣ sub_agent"| recommender

    subgraph SubAgents["👥 Sub-Agents (Execução Sequencial)"]
        validator["<b>LeadValidatorAgent</b><br><i>claude-haiku-4-5</i><br>Validação de informações"]
        scorer["<b>LeadScorerAgent</b><br><i>claude-haiku-4-5</i><br>Pontuação do lead (1-10)"]
        recommender["<b>ActionRecommenderAgent</b><br><i>claude-haiku-4-5</i><br>Recomendação de ações"]
    end

    validator -->|"output_key: validation_status"| scorer
    scorer -->|"output_key: lead_score"| recommender

    %% --- Estilo do ROOT (Manager) ---
    %% Container em branco, Nó em Azul Claro
    style RootAgent fill:#ffffff,stroke:#01579b,stroke-width:2px,color:#000
    style manager fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000

    %% --- Estilo dos SUB_AGENTS ---
    %% Container em branco, Nós em Laranja Claro
    style SubAgents fill:#ffffff,stroke:#e65100,stroke-width:2px,color:#000

    style validator fill:#fff3e0,stroke:#e65100,stroke-width:1px,color:#000
    style scorer fill:#fff3e0,stroke:#e65100,stroke-width:1px,color:#000
    style recommender fill:#fff3e0,stroke:#e65100,stroke-width:1px,color:#000
```

## Fluxo de Execução

1. **LeadValidatorAgent**: Recebe as informações do lead e valida se estão completas
   - Saída: `validation_status` (valid/invalid)

2. **LeadScorerAgent**: Analisa o lead e atribui uma pontuação de 1-10
   - Saída: `lead_score` (pontuação + justificativa)

3. **ActionRecommenderAgent**: Recomenda ações baseadas na validação e pontuação
   - Saída: `action_recommendation` (recomendação para equipe de vendas)
