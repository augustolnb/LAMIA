"""Motor determinístico de interações medicamentosas.

Base curada com quatro camadas de avaliação, todas resolvidas em Python (nunca pelo LLM):

1. Duplicação terapêutica: mesmo genérico sob nomes diferentes e componentes
   sobrepostos de compostos combinados (ex.: Tarka = trandolapril + verapamil).
2. Farmacocinética via citocromo P450: inibidores potentes de CYP2D6/CYP3A4
   sobre substratos dessas mesmas isoenzimas.
3. Efeitos somatórios/sinérgicos: risco hemorrágico, depressão do SNC e
   respiratória, toxicidade dromotrópica, distúrbios eletrolíticos.
4. Antagonismo farmacodinâmico direto: colinérgico vs. anticolinérgico,
   beta-agonista vs. betabloqueador.

A cobertura é limitada ao que está codificado aqui: a base é auditável e
determinística por decisão de projeto, já que se trata de apoio à decisão
clínica e uma alucinação do modelo teria custo assistencial real.
"""

from __future__ import annotations

import itertools
import re

# --- Camada 1: nomes comerciais, sinônimos em português e compostos combinados ---

_ALIASES: dict[str, tuple[str, ...]] = {
    # anticoagulantes / antiagregantes
    "warfarin": ("warfarin", "warfarina", "varfarina", "coumadin", "marevan"),
    "heparin": ("heparin", "heparina", "heparinized"),
    "aspirin": (
        "aspirin", "aspirina", "aas", "asa", "ecotrin", "ecasa",
        "acido acetilsalicilico", "ácido acetilsalicílico",
    ),
    # AINEs
    "ibuprofen": ("ibuprofen", "ibuprofeno", "motrin", "advil"),
    "diclofenac": ("diclofenac", "diclofenaco", "voltaren"),
    "meloxicam": ("meloxicam", "mobic"),
    "naproxen": ("naproxen", "naproxeno", "aleve", "naprosyn"),
    # corticoides
    "prednisone": ("prednisone", "prednisona"),
    "methylprednisolone": ("methylprednisolone", "metilprednisolona", "solu-medrol", "solumedrol"),
    "fluticasone": ("fluticasone", "fluticasona", "flonase"),
    # cardiovascular
    "digoxin": ("digoxin", "digoxina", "lanoxin"),
    "furosemide": ("furosemide", "furosemida", "lasix"),
    "captopril": ("captopril", "capoten"),
    "lisinopril": ("lisinopril", "prinivil", "zestril"),
    "trandolapril": ("trandolapril", "mavik"),
    "losartan": ("losartan", "losartana", "cozaar"),
    "amlodipine": ("amlodipine", "amlodipina", "norvasc"),
    "nifedipine": ("nifedipine", "nifedipina", "procardia", "adalat"),
    "verapamil": ("verapamil", "verapamila", "calan", "isoptin"),
    "diltiazem": ("diltiazem", "cardizem"),
    "metoprolol": ("metoprolol", "lopressor", "toprol"),
    "propranolol": ("propranolol", "inderal"),
    "labetalol": ("labetalol", "trandate"),
    "esmolol": ("esmolol", "brevibloc"),
    "nitroglycerin": ("nitroglycerin", "nitroglicerina", "tridil"),
    "potassium chloride": ("kcl", "cloreto de potassio", "cloreto de potássio", "potassium chloride"),
    # SNC
    "haloperidol": ("haloperidol", "haldol"),
    "nortriptyline": ("nortriptyline", "nortriptilina", "pamelor"),
    "escitalopram": ("escitalopram", "lexapro"),
    "fluoxetine": ("fluoxetine", "fluoxetina", "prozac"),
    "alprazolam": ("alprazolam", "xanax"),
    "lorazepam": ("lorazepam", "ativan"),
    "oxazepam": ("oxazepam", "serax"),
    "gabapentin": ("gabapentin", "gabapentina", "neurontin"),
    "memantine": ("memantine", "memantina", "namenda"),
    "donepezil": ("donepezil", "donepezila", "aricept"),
    "trihexyphenidyl": ("trihexyphenidyl", "triexifenidil", "artane"),
    "oxybutynin": ("oxybutynin", "oxibutinina", "ditropan"),
    "cyclobenzaprine": ("cyclobenzaprine", "ciclobenzaprina", "flexeril"),
    # analgésicos / opioides
    "acetaminophen": ("acetaminophen", "acetaminofeno", "paracetamol", "tylenol"),
    "hydrocodone": ("hydrocodone", "hidrocodona"),
    "oxycodone": ("oxycodone", "oxicodona"),
    "morphine": ("morphine", "morfina"),
    "propoxyphene": ("propoxyphene", "propoxifeno"),
    # outros
    "simvastatin": ("simvastatin", "simvastatina", "zocor"),
    "atorvastatin": ("atorvastatin", "atorvastatina", "lipitor"),
    "clarithromycin": ("clarithromycin", "claritromicina", "biaxin"),
    "omeprazole": ("omeprazole", "omeprazol", "prilosec", "zegerid"),
    "albuterol": ("albuterol", "salbutamol", "ventolin", "proventil"),
    "metaproterenol": ("metaproterenol", "alupent"),
    "theophylline": ("theophylline", "teofilina"),
    "sildenafil": ("sildenafil", "sildenafila", "viagra"),
    "metformin": ("metformin", "metformina", "glucophage"),
    "iodinated contrast": ("iodinated contrast", "contraste iodado"),
    "fexofenadine": ("fexofenadine", "fexofenadina", "allegra"),
    "hydroxychloroquine": ("hydroxychloroquine", "hidroxicloroquina", "plaquenil"),
    "isotretinoin": ("isotretinoin", "isotretinoina", "isotretinoína", "accutane"),
    "oral contraceptive": ("aco", "anticoncepcional oral", "contraceptivo oral"),
    "intrauterine device": ("diu", "dispositivo intrauterino"),
    "insulin": ("insulin", "insulina", "insulinas"),
    "medroxyprogesterone": ("medroxyprogesterone", "depo-provera"),
    "ferrous sulfate": ("ferrous sulfate", "feso4", "sulfato ferroso"),
    "magnesium oxide": ("magnesium oxide", "oxido de magnesio", "óxido de magnésio", "mag oxide"),
    "docusate": ("docusate", "colace"),
    "calcium carbonate": ("calcium carbonate", "carbonato de calcio", "tums"),
    "antacid": ("mylanta", "antiacido", "antiácido"),
    "protamine": ("protamine", "protamina"),
    "papaverine": ("papaverine", "papaverina"),
}

# Compostos combinados: uma marca que carrega mais de um princípio ativo.
_COMBINATIONS: dict[str, tuple[str, ...]] = {
    "tarka": ("trandolapril", "verapamil"),
    "vicodin": ("hydrocodone", "acetaminophen"),
    "norco": ("hydrocodone", "acetaminophen"),
    "lortab": ("hydrocodone", "acetaminophen"),
    "percocet": ("oxycodone", "acetaminophen"),
    "darvocet-n": ("propoxyphene", "acetaminophen"),
    "darvocet": ("propoxyphene", "acetaminophen"),
}

# alias -> genéricos que ele representa
_ALIAS_TO_GENERICS: dict[str, tuple[str, ...]] = {}
for _generic, _names in _ALIASES.items():
    for _name in _names:
        _ALIAS_TO_GENERICS[_name] = (_generic,)
_ALIAS_TO_GENERICS.update(_COMBINATIONS)

# Aliases mais longos primeiro para "solu-medrol" não perder para "medrol".
_ALIASES_BY_LENGTH = sorted(_ALIAS_TO_GENERICS, key=len, reverse=True)


# --- Camada 2: classes terapêuticas e propriedades farmacológicas ---

_CLASSES: dict[str, set[str]] = {
    "warfarin": {"anticoagulante", "substrato_cyp2c9"},
    "heparin": {"anticoagulante"},
    "aspirin": {"antiagregante_plaquetario", "aine", "lesivo_mucosa_gastrica"},
    "ibuprofen": {"aine", "lesivo_mucosa_gastrica", "nefrotoxico_pre_renal"},
    "diclofenac": {"aine", "lesivo_mucosa_gastrica", "nefrotoxico_pre_renal"},
    "meloxicam": {"aine", "lesivo_mucosa_gastrica", "nefrotoxico_pre_renal"},
    "naproxen": {"aine", "lesivo_mucosa_gastrica", "nefrotoxico_pre_renal"},
    "prednisone": {"corticoide_sistemico", "lesivo_mucosa_gastrica"},
    "methylprednisolone": {"corticoide_sistemico", "lesivo_mucosa_gastrica"},
    "fluticasone": {"corticoide_inalatorio"},
    "digoxin": {"glicosideo_cardiaco", "dromotropico_negativo", "indice_terapeutico_estreito"},
    "furosemide": {"diuretico_de_alca", "hipocalemiante", "nefrotoxico_pre_renal"},
    "captopril": {"ieca", "hipercalemiante"},
    "lisinopril": {"ieca", "hipercalemiante"},
    "trandolapril": {"ieca", "hipercalemiante"},
    "losartan": {"bra", "hipercalemiante"},
    "potassium chloride": {"suplemento_potassio", "hipercalemiante"},
    "amlodipine": {"bcc_diidropiridinico"},
    "nifedipine": {"bcc_diidropiridinico"},
    "verapamil": {"bcc_nao_diidropiridinico", "dromotropico_negativo", "inibidor_cyp3a4_potente"},
    "diltiazem": {"bcc_nao_diidropiridinico", "dromotropico_negativo", "inibidor_cyp3a4_potente"},
    "metoprolol": {"betabloqueador", "dromotropico_negativo", "substrato_cyp2d6"},
    "propranolol": {"betabloqueador", "dromotropico_negativo", "substrato_cyp2d6"},
    "labetalol": {"betabloqueador", "dromotropico_negativo"},
    "esmolol": {"betabloqueador", "dromotropico_negativo"},
    "nitroglycerin": {"nitrato", "vasodilatador"},
    "haloperidol": {
        "antipsicotico_tipico", "prolonga_qtc", "depressor_snc",
        "substrato_cyp2d6", "substrato_cyp3a4",
    },
    "nortriptyline": {
        "adt", "anticolinergico", "prolonga_qtc", "depressor_snc", "substrato_cyp2d6",
    },
    "escitalopram": {"issrs", "prolonga_qtc", "lesivo_mucosa_gastrica"},
    "fluoxetine": {
        "issrs", "prolonga_qtc", "lesivo_mucosa_gastrica", "inibidor_cyp2d6_potente",
    },
    "alprazolam": {"benzodiazepinico", "depressor_snc", "depressor_respiratorio", "substrato_cyp3a4"},
    "lorazepam": {"benzodiazepinico", "depressor_snc", "depressor_respiratorio"},
    "oxazepam": {"benzodiazepinico", "depressor_snc", "depressor_respiratorio"},
    "gabapentin": {"anticonvulsivante", "depressor_snc"},
    "memantine": {"antagonista_nmda"},
    "donepezil": {"colinergico", "bradicardizante"},
    "trihexyphenidyl": {"anticolinergico", "antiparkinsoniano"},
    "oxybutynin": {"anticolinergico", "antiespasmodico_urinario"},
    "cyclobenzaprine": {"relaxante_muscular", "anticolinergico", "depressor_snc"},
    "acetaminophen": {"analgesico_simples", "hepatotoxico_dose_dependente"},
    "hydrocodone": {"opioide", "depressor_snc", "depressor_respiratorio", "substrato_cyp2d6"},
    "oxycodone": {"opioide", "depressor_snc", "depressor_respiratorio", "substrato_cyp2d6"},
    "morphine": {"opioide", "depressor_snc", "depressor_respiratorio"},
    "propoxyphene": {"opioide", "depressor_snc", "depressor_respiratorio", "prolonga_qtc"},
    "simvastatin": {"estatina", "substrato_cyp3a4"},
    "atorvastatin": {"estatina", "substrato_cyp3a4"},
    "clarithromycin": {"macrolideo", "inibidor_cyp3a4_potente", "prolonga_qtc"},
    "omeprazole": {"ibp", "inibidor_cyp2c19"},
    "albuterol": {"beta_agonista", "broncodilatador"},
    "metaproterenol": {"beta_agonista", "broncodilatador"},
    "theophylline": {"metilxantina", "broncodilatador", "indice_terapeutico_estreito"},
    "sildenafil": {"inibidor_pde5", "vasodilatador", "substrato_cyp3a4"},
    "metformin": {"biguanida"},
    "iodinated contrast": {"contraste_iodado", "nefrotoxico_pre_renal"},
    "fexofenadine": {"anti_histaminico"},
    "hydroxychloroquine": {"antimalarico", "prolonga_qtc"},
    "isotretinoin": {"retinoide", "teratogenico"},
    "oral contraceptive": {"contraceptivo", "estrogenio"},
    "intrauterine device": {"contraceptivo"},
    "insulin": {"insulina", "hipoglicemiante"},
    "medroxyprogesterone": {"contraceptivo", "progestogeno"},
    "magnesium oxide": {"reduz_absorcao_gi"},
}

# Classes que caracterizam duplicação quando repetidas (tags de propriedade não contam).
_CLASSES_DUPLICAVEIS = {
    "anticoagulante", "antiagregante_plaquetario", "aine", "corticoide_sistemico",
    "glicosideo_cardiaco", "diuretico_de_alca", "ieca", "bra", "suplemento_potassio",
    "bcc_diidropiridinico", "bcc_nao_diidropiridinico", "betabloqueador", "nitrato",
    "antipsicotico_tipico", "adt", "issrs", "benzodiazepinico", "opioide",
    "anticolinergico", "colinergico", "estatina", "ibp", "macrolideo",
    "anti_histaminico", "corticoide_inalatorio", "biguanida", "inibidor_pde5",
    "contraceptivo", "relaxante_muscular", "analgesico_simples", "metilxantina",
    "beta_agonista",
}

_DUPLICACAO_CRITICA = {
    "anticoagulante", "antiagregante_plaquetario", "aine", "benzodiazepinico",
    "opioide", "adt", "antipsicotico_tipico", "glicosideo_cardiaco", "issrs",
    "betabloqueador", "ieca", "bcc_nao_diidropiridinico", "analgesico_simples",
}

_NOMES_DE_CLASSE = {
    "anticoagulante": "anticoagulantes",
    "aine": "anti-inflamatórios não esteroidais",
    "benzodiazepinico": "benzodiazepínicos",
    "opioide": "opioides",
    "betabloqueador": "betabloqueadores",
    "ieca": "inibidores da ECA",
    "issrs": "inibidores seletivos da recaptação de serotonina",
    "anticolinergico": "anticolinérgicos",
    "estatina": "estatinas",
    "contraceptivo": "métodos contraceptivos",
    "analgesico_simples": "analgésicos simples (paracetamol)",
}

# --- Camada 3: regras por classe, avaliadas em ordem de precedência clínica ---

_M_SOMATORIO = "Efeito somatório/sinérgico"
_M_CYP = "Interação farmacocinética (CYP450)"
_M_ANTAGONISMO = "Antagonismo farmacodinâmico"
_M_DUPLICACAO = "Duplicação terapêutica"

# (classes_a, classes_b, nível, mecanismo, descrição)
_REGRAS: list[tuple[set[str], set[str], str, str, str]] = [
    (
        {"anticoagulante"}, {"antiagregante_plaquetario", "aine"}, "Crítico", _M_SOMATORIO,
        "Risco aumentado de sangramento grave (inclusive intracraniano e digestivo) pela "
        "associação de anticoagulante com antiagregante/AINE.",
    ),
    (
        {"diuretico_de_alca"}, {"glicosideo_cardiaco"}, "Crítico", _M_SOMATORIO,
        "A hipocalemia induzida pelo diurético de alça potencializa a toxicidade digitálica, "
        "com risco de arritmia ventricular fatal.",
    ),
    (
        {"hipercalemiante"}, {"hipercalemiante"}, "Crítico", _M_SOMATORIO,
        "Risco de hipercalemia grave por retenção somatória de potássio, com potencial "
        "arritmogênico.",
    ),
    (
        {"aine"}, {"ieca", "bra", "diuretico_de_alca"}, "Moderado", _M_SOMATORIO,
        "Redução do efeito anti-hipertensivo e risco de lesão renal aguda (piora da função "
        "renal por inibição das prostaglandinas).",
    ),
    (
        {"prolonga_qtc"}, {"prolonga_qtc"}, "Crítico", _M_SOMATORIO,
        "Prolongamento somatório do intervalo QTc, com risco de Torsades de Pointes e parada "
        "cardíaca.",
    ),
    (
        {"depressor_respiratorio"}, {"depressor_respiratorio"}, "Crítico", _M_SOMATORIO,
        "Depressão respiratória e sedação profunda por efeito somatório sobre o SNC, com risco "
        "de parada respiratória.",
    ),
    (
        {"depressor_snc"}, {"depressor_snc"}, "Crítico", _M_SOMATORIO,
        "Efeito somatório de depressão do SNC (sedação excessiva, confusão, quedas e risco de "
        "depressão respiratória).",
    ),
    (
        {"betabloqueador"}, {"bcc_nao_diidropiridinico"}, "Crítico", _M_SOMATORIO,
        "Toxicidade dromotrópica e cronotrópica somatória: risco de bradicardia grave, bloqueio "
        "atrioventricular total e colapso hemodinâmico.",
    ),
    (
        {"glicosideo_cardiaco"}, {"bcc_nao_diidropiridinico"}, "Crítico", _M_SOMATORIO,
        "Toxicidade dromotrópica somatória com elevação dos níveis de digoxina: risco de "
        "bloqueio atrioventricular avançado.",
    ),
    (
        {"inibidor_cyp2d6_potente"}, {"substrato_cyp2d6"}, "Crítico", _M_CYP,
        "Inibição potente da CYP2D6 eleva os níveis séricos do substrato, com risco de "
        "toxicidade dose-dependente (ex.: bradicardia e hipotensão severas).",
    ),
    (
        {"inibidor_cyp3a4_potente"}, {"substrato_cyp3a4"}, "Crítico", _M_CYP,
        "Inibição potente da CYP3A4 eleva os níveis séricos do substrato, com risco de "
        "toxicidade dose-dependente (ex.: miopatia e rabdomiólise com estatinas).",
    ),
    (
        {"issrs"}, {"aine", "anticoagulante"}, "Crítico", _M_SOMATORIO,
        "Risco aumentado de sangramento gástrico: o ISRS reduz a agregação plaquetária e soma-se "
        "à lesão de mucosa causada pelo AINE.",
    ),
    (
        {"aine"}, {"corticoide_sistemico"}, "Crítico", _M_SOMATORIO,
        "Risco elevado de úlcera péptica e sangramento gástrico por lesão somatória da mucosa.",
    ),
    (
        {"beta_agonista"}, {"betabloqueador"}, "Crítico", _M_ANTAGONISMO,
        "Antagonismo farmacodinâmico direto no receptor beta-2: o betabloqueador anula a "
        "broncodilatação e pode precipitar broncoespasmo.",
    ),
    (
        {"colinergico"}, {"anticolinergico"}, "Crítico", _M_ANTAGONISMO,
        "Antagonismo farmacodinâmico direto: o anticolinérgico anula o efeito do inibidor da "
        "acetilcolinesterase e pode agravar o declínio cognitivo.",
    ),
    (
        {"inibidor_pde5"}, {"nitrato"}, "Crítico", _M_SOMATORIO,
        "Hipotensão grave e risco de colapso cardiovascular por potencialização vasodilatadora.",
    ),
    (
        {"biguanida"}, {"contraste_iodado"}, "Crítico", _M_SOMATORIO,
        "Risco de acidose lática em caso de insuficiência renal aguda induzida por contraste.",
    ),
    (
        {"anticolinergico"}, {"anticolinergico"}, "Moderado", _M_SOMATORIO,
        "Carga anticolinérgica somatória: risco de confusão, retenção urinária, constipação e "
        "delirium, sobretudo em idosos.",
    ),
    (
        {"metilxantina"}, {"beta_agonista"}, "Moderado", _M_SOMATORIO,
        "Sinergismo estimulante entre metilxantina e beta-agonista: risco de taquiarritmia e "
        "agravamento de hipocalemia.",
    ),
    (
        {"reduz_absorcao_gi"}, {"glicosideo_cardiaco"}, "Moderado", _M_SOMATORIO,
        "Redução da absorção/biodisponibilidade oral por quelação ou alteração do trânsito "
        "gastrointestinal — relevante pelo índice terapêutico estreito do glicosídeo cardíaco.",
    ),
    (
        {"reduz_absorcao_gi"}, {"ieca"}, "Baixo", _M_SOMATORIO,
        "Redução leve da absorção/biodisponibilidade oral por quelação ou alteração do "
        "trânsito gastrointestinal.",
    ),
]


def normalize_drug(drug: str) -> tuple[str, ...]:
    """Resolve um nome de fármaco nos princípios ativos genéricos que ele representa.

    Tolera dosagem/posologia junto do nome e expande compostos combinados
    ("Tarka" -> trandolapril + verapamil). Se nada for reconhecido, devolve o
    próprio texto normalizado, para que o par ainda apareça na contagem.
    """
    texto = " ".join(drug.strip().lower().split())
    encontrados: list[str] = []
    for alias in _ALIASES_BY_LENGTH:
        if re.search(rf"(?<!\w){re.escape(alias)}(?!\w)", texto):
            for generico in _ALIAS_TO_GENERICS[alias]:
                if generico not in encontrados:
                    encontrados.append(generico)
    if not encontrados:
        return (texto,)
    return tuple(sorted(encontrados))


def _classes(genericos: tuple[str, ...]) -> set[str]:
    conjunto: set[str] = set()
    for generico in genericos:
        conjunto |= _CLASSES.get(generico, set())
    return conjunto


def _duplicacao_por_generico(
    par: str, gen_a: tuple[str, ...], gen_b: tuple[str, ...]
) -> dict | None:
    compartilhados = sorted(set(gen_a) & set(gen_b))
    if not compartilhados:
        return None
    nomes = ", ".join(compartilhados)
    return {
        "par": par,
        "nivel": "Crítico",
        "mecanismo": _M_DUPLICACAO,
        "descricao": (
            f"Ambos os itens contêm {nomes} — duplicação terapêutica com dose somatória "
            "involuntária e risco de toxicidade."
        ),
    }


def _duplicacao_por_classe(
    par: str, cls_a: set[str], cls_b: set[str]
) -> dict | None:
    compartilhadas = sorted((cls_a & cls_b) & _CLASSES_DUPLICAVEIS)
    if not compartilhadas:
        return None
    classe = compartilhadas[0]
    nivel = "Crítico" if classe in _DUPLICACAO_CRITICA else "Moderado"
    rotulo = _NOMES_DE_CLASSE.get(classe, classe.replace("_", " "))
    return {
        "par": par,
        "nivel": nivel,
        "mecanismo": _M_DUPLICACAO,
        "descricao": (
            f"Dois fármacos da mesma classe ({rotulo}) — duplicação terapêutica com efeito "
            "somatório e risco aumentado de eventos adversos."
        ),
    }


def _regra_por_classe(par: str, cls_a: set[str], cls_b: set[str]) -> dict | None:
    for lado_1, lado_2, nivel, mecanismo, descricao in _REGRAS:
        casa = (cls_a & lado_1 and cls_b & lado_2) or (cls_b & lado_1 and cls_a & lado_2)
        if casa:
            return {"par": par, "nivel": nivel, "mecanismo": mecanismo, "descricao": descricao}
    return None


def evaluate_pair(drug_a: str, drug_b: str) -> dict | None:
    """Avalia um par de fármacos. Devolve o alerta, ou None se nada for identificado.

    A avaliação é simétrica e determinística: mesma entrada, mesma saída.
    """
    par = f"{drug_a} + {drug_b}"
    gen_a, gen_b = normalize_drug(drug_a), normalize_drug(drug_b)
    cls_a, cls_b = _classes(gen_a), _classes(gen_b)

    return (
        _duplicacao_por_generico(par, gen_a, gen_b)
        or _duplicacao_por_classe(par, cls_a, cls_b)
        or _regra_por_classe(par, cls_a, cls_b)
    )


def deduplicate_drugs(drugs: list[str]) -> list[str]:
    """Colapsa menções redundantes do MESMO fármaco antes do cruzamento de pares.

    Duas entradas são a mesma entidade quando normalize_drug() devolve
    exatamente o mesmo conjunto de genéricos — cobre variação de via/dose
    ("heparin" vs. "Heparin IV", "Prednisone 80mg qd" vs. "Prednisone 60mg qd")
    e sinônimo marca/genérico exato ("Xanax" vs. "alprazolam"). Conjuntos que
    apenas SE SOBREPÕEM (Tarka ⊃ verapamil) permanecem entidades distintas —
    isso é duplicação terapêutica genuína, não redundância de menção, e
    continua sendo detectada por evaluate_pair/_duplicacao_por_generico.

    Mantém a primeira grafia vista de cada entidade, na ordem original.
    """
    vistos: set[tuple[str, ...]] = set()
    resultado: list[str] = []
    for drug in drugs:
        chave = normalize_drug(drug)
        if chave not in vistos:
            vistos.add(chave)
            resultado.append(drug)
    return resultado


def evaluate_all_pairs(drugs: list[str]) -> dict:
    """Avalia TODAS as N*(N-1)/2 combinações da lista, sem truncamento.

    O pareamento é feito em Python (itertools.combinations) justamente para não
    depender de o LLM iterar corretamente sobre uma lista longa. Antes de
    parear, a lista passa por deduplicate_drugs(): menções repetidas da mesma
    substância (grafia, via ou dose diferentes, ou marca vs. genérico) não
    formam par entre si — isso evitaria alertas artificiais de "duplicação"
    quando na verdade é uma única prescrição mencionada mais de uma vez.

    Returns:
        dict com "farmacos_normalizados" (lista deduplicada), "duplicatas_removidas"
        (quantas menções brutas foram colapsadas), "pares_avaliados" (sobre a
        lista já deduplicada) e "alertas" (só os pares com achado).
    """
    entidades = deduplicate_drugs(drugs)
    alertas: list[dict] = []
    total = 0
    for a, b in itertools.combinations(entidades, 2):
        total += 1
        alerta = evaluate_pair(a, b)
        if alerta is not None:
            alertas.append(alerta)

    ordem = {"Crítico": 0, "Moderado": 1, "Baixo": 2}
    alertas.sort(key=lambda x: ordem.get(x["nivel"], 3))
    return {
        "farmacos_normalizados": entidades,
        "duplicatas_removidas": len(drugs) - len(entidades),
        "pares_avaliados": total,
        "alertas": alertas,
    }
