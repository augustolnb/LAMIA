# ag-clinico-adk

Pipeline de agentes clínicos (Extractor, Safety, Report, orquestrados por um Router
hierárquico) construído sobre o Google ADK, usando DeepSeek como LLM. Processa casos do
dataset mtsamples e produz extração estruturada, alertas de interação medicamentosa e um
RELATÓRIO clínico conciso em português — como apoio à decisão clínica, nunca como
diagnóstico definitivo.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # preencha DEEPSEEK_API_KEY
```

Salve o CSV mtsamples em `data/mtsamples.csv` (colunas `description`, `transcription`,
`medical_specialty`).

## Rodar os testes

```bash
pytest
```

## Rodar a demo

```bash
python run_demo.py
```

Ou abra `demo.ipynb` em Jupyter.

## Aviso

Este sistema é apoio à decisão clínica. Não substitui avaliação médica presencial nem
constitui diagnóstico definitivo.

## Arquitetura

O pipeline ao vivo (`run_case_async()`) chama apenas dois LLMs, diretamente, sem orquestrador:

- **Extractor Agent**: extrai `{sintomas, historico, farmacos, alergias}` do texto livre — nunca
  infere diagnóstico; ignora insumos/materiais cirúrgicos (fios de sutura, curativos, drenos,
  material de osteossíntese) que não são fármacos; isola fármacos citados em seção de alergia
  (`ALLERGIES: ...`) em `alergias`, fora de `farmacos` e fora da checagem de interação; e exclui
  de `sintomas` queixas negadas ("denies chest pain") — só sintomas ativos entram.
- **Checagem de segurança** (Python puro, sem LLM): cruza todas as combinações da lista de
  fármacos extraída via `src/interactions.py` — ver seção abaixo.
- **Report Agent**: consolida tudo em um RELATÓRIO em Markdown com as seções
  `**Subjetivo:**`, `**Objetivo:**`, `**Avaliação:**` e `**Plano:**`, sempre com o disclaimer
  de apoio à decisão.

`Router Agent` e `Safety Agent` (uma versão do checador de interações mediada por LLM, usando
a tool `check_all_drug_interactions`) continuam definidos e testados em `src/agents.py`
(`build_router_agent()`, `build_safety_agent()`), mas **não são usados pelo pipeline ao vivo**.
Motivo: quando o `report_agent` era chamado como `AgentTool` do `router_agent`, o texto de
handoff entre eles era composto livremente pelo LLM do router — o que produzia incoerências
entre o JSON de segurança e a Avaliação escrita (ex.: o router parafraseando dados de forma
inconsistente, ou o `safety_agent` chamando a tool de par único em vez da tool em lote e
injetando um alerta "Baixo" espúrio que o motor determinístico nunca geraria). Chamar
`extractor_agent` e `report_agent` diretamente, com o Python compondo o handoff entre eles,
elimina esse intermediário de LLM e garante que o JSON de segurança retornado e o texto do
relatório nunca divirjam — ver `pipeline.py::_format_report_request`.

### Checagem de segurança determinística

O cruzamento das `N*(N-1)/2` combinações de fármacos é feito em Python
(`src/interactions.py`), **não** pelo LLM. Isso existe porque delegar o pareamento ao modelo
truncava a cobertura em listas longas (14–17 fármacos retornavam 0 alertas). Antes de parear,
a lista passa por `deduplicate_drugs()`: menções repetidas da MESMA substância — variação de
dose/via ("heparin" x "Heparin IV") ou sinônimo marca/genérico exato ("Xanax" x "alprazolam")
— contam como um único fármaco, não dois, evitando alerta artificial de duplicação entre
grafias da mesma prescrição.

O resultado (`safety_report`) é passado diretamente, como JSON verbatim, na mensagem enviada
ao `report_agent` — nenhum LLM intermediário o reescreve ou resume antes disso.

A base cobre quatro mecanismos, com normalização de marca comercial e nome em português
(Lasix → furosemide, AAS → aspirin) e expansão de compostos combinados
(Tarka → trandolapril + verapamil):

1. **Duplicação terapêutica** — mesmo princípio ativo sob nomes diferentes ou dentro de um
   composto combinado, e repetição de classe.
2. **Farmacocinética (CYP450)** — inibidores potentes de CYP2D6/CYP3A4 sobre seus substratos.
3. **Efeitos somatórios/sinérgicos** — risco hemorrágico, depressão do SNC e respiratória,
   toxicidade dromotrópica, distúrbios eletrolíticos.
4. **Antagonismo farmacodinâmico** — colinérgico vs. anticolinérgico, beta-agonista vs.
   betabloqueador.

A cobertura é limitada ao que está codificado na base: determinística e auditável por
decisão de projeto, já que uma alucinação do modelo teria custo assistencial real.

Ver `docs/superpowers/specs/2026-08-17-clinical-agents-adk-design.md` para o design completo.

## Estrutura

```
src/
  data_prep.py     # filtragem de amostra do mtsamples
  interactions.py  # base curada + motor determinístico de interações
  tools.py         # check_all_drug_interactions / check_drug_interaction (tools do ADK)
  agents.py        # Extractor, Report (ADK, usados ao vivo); Safety/Router (ADK, não usados
                   #   ao vivo — ver seção Arquitetura)
  pipeline.py      # run_case_async() / run_case() — usados por run_demo.py e demo.ipynb
tests/             # testes de lógica pura (sem rede/LLM), incl. casos-ouro revisados
run_demo.py      # CLI de demonstração
demo.ipynb       # notebook de demonstração
```
