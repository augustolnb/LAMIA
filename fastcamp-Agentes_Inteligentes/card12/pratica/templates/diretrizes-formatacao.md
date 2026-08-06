# Diretrizes de Formatação — Documentos de Aula em LaTeX

## Sobre este documento

Este arquivo é lido pelo workflow "Gerador de Aulas" e enviado como contexto para a LLM
antes de qualquer geração de documento. Ele define a estrutura, os pacotes disponíveis e
as convenções que o LaTeX gerado **precisa** seguir para compilar sem erros no serviço
local `latex-compiler`.

## Pacotes disponíveis na imagem de compilação

- `inputenc` (`utf8`), `fontenc` (`T1`) — acentuação e caracteres em português.
- `babel` (`brazilian`) — hifenização e convenções em português do Brasil.
- `amsmath`, `amssymb` — notação matemática.
- `geometry` — margens da página.
- `enumitem` — listas numeradas/com marcadores customizáveis.
- `hyperref` — sumário e links clicáveis dentro do PDF.

**Não usar `graphicx` nem qualquer comando que referencie arquivo externo** (imagem,
bibliografia `.bib`, etc.) — o ambiente de compilação não tem acesso a arquivos além do
próprio `.tex` recebido, nem acesso à internet.

## Estrutura obrigatória do documento

1. Preâmbulo com `\documentclass[a4paper,12pt]{article}` e os pacotes listados acima.
2. Cabeçalho com título da aula, matéria e nível de ensino (`\title`, `\author`, `\date` ou
   equivalente manual).
3. Seção **"Objetivos de Aprendizagem"** — de 2 a 4 bullet points objetivos.
4. Seção **"Conteúdo Teórico"** — explicação do tópico pedido, em linguagem acessível e
   adequada ao nível de ensino informado no pedido.
5. Seção **"Exercícios"** — de 3 a 5 exercícios de fixação sobre o conteúdo, sem gabarito
   no mesmo documento.
6. Nenhum pacote, comando ou referência fora do que está descrito acima.

## Formato de saída esperado da LLM

A resposta deve ser **exclusivamente o código-fonte LaTeX completo e compilável** — sem
texto explicativo antes ou depois, sem blocos de código Markdown (` ``` `), começando
literalmente em `\documentclass` e terminando em `\end{document}`. Qualquer texto fora
desse intervalo quebra o passo de compilação, já que o corpo inteiro da resposta é
enviado como está para o compilador.

## Exemplo mínimo válido

```latex
\documentclass[a4paper,12pt]{article}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage[brazilian]{babel}
\usepackage{amsmath,amssymb}
\usepackage[margin=2.5cm]{geometry}
\usepackage{enumitem}
\usepackage{hyperref}

\title{Lei de Ohm}
\author{Aula gerada automaticamente}
\date{\today}

\begin{document}
\maketitle

\section*{Objetivos de Aprendizagem}
\begin{itemize}[leftmargin=*]
  \item Compreender a relação entre tensão, corrente e resistência.
  \item Aplicar a fórmula $V = R \cdot I$ na resolução de problemas simples.
\end{itemize}

\section*{Conteúdo Teórico}
A Lei de Ohm descreve a relação entre tensão ($V$), corrente ($I$) e resistência ($R$)
em um circuito elétrico: $V = R \cdot I$. Isso significa que, para uma resistência
constante, a corrente é diretamente proporcional à tensão aplicada...

\section*{Exercícios}
\begin{enumerate}
  \item Um resistor de $10\,\Omega$ é submetido a uma tensão de $5\,V$. Qual a corrente
  que passa por ele?
  \item Se a corrente em um circuito é de $2\,A$ e a resistência é $15\,\Omega$, qual a
  tensão aplicada?
\end{enumerate}

\end{document}
```
