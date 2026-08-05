Os Quatro Princípios em Detalhe
1. Pense antes de programar
Não faça suposições. Não esconda a confusão. Deixe as vantagens e desvantagens à mostra.

Muitas vezes, os mestres em direito escolhem uma interpretação silenciosamente e a adotam. Este princípio força o raciocínio explícito:

Declare as suposições explicitamente — em caso de dúvida, pergunte em vez de supor.
Apresente múltiplas interpretações — Não escolha uma sem questionar quando houver ambiguidade.
Resista quando necessário — Se existir uma abordagem mais simples, diga isso.
Pare se estiver confuso — Nomeie o que não está claro e peça esclarecimentos.
2. Simplicidade em Primeiro Lugar
Código mínimo que resolva o problema. Nada de especulações.

Combater a tendência ao excesso de engenharia:

Nenhuma funcionalidade além do que foi solicitado.
Sem abstrações para código de uso único.
Nenhuma "flexibilidade" ou "configurabilidade" que não tenha sido solicitada.
Sem tratamento de erros para cenários impossíveis
Se 200 linhas pudessem ser reduzidas a 50, reescreva-as.
O teste: um engenheiro sênior diria que isso é muito complicado? Se sim, simplifique.

3. Alterações cirúrgicas
Toque apenas no que for necessário. Limpe apenas a sua própria sujeira.

Ao editar um código existente:

Não "aprimore" o código, os comentários ou a formatação adjacentes.
Não refatore coisas que não estão quebradas.
Combine com o estilo existente, mesmo que você o fizesse de forma diferente.
Se você encontrar código morto não relacionado, mencione-o — não o apague.
Quando suas alterações criam arquivos órfãos:

Remova as importações/variáveis/funções que SUAS alterações tornaram não utilizadas.
Não remova código morto preexistente, a menos que seja solicitado.
O teste: Cada linha alterada deve estar diretamente relacionada à solicitação do usuário.

4. Execução orientada a objetivos
Defina os critérios de sucesso. Repita o processo até que sejam verificados.

Transformar tarefas imperativas em objetivos verificáveis:

Em vez de...	Transformar-se em...
"Adicionar validação"	"Escreva testes para entradas inválidas e, em seguida, faça com que eles sejam aprovados."
"Corrigir o bug"	"Escreva um teste que reproduza o problema e, em seguida, faça com que ele seja aprovado."
"Refatorar X"	"Garantir a aprovação nos testes antes e depois"
Para tarefas com várias etapas, apresente um plano resumido:

1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
Critérios de sucesso rigorosos permitem que o LLM funcione de forma independente. Critérios fracos ("fazer funcionar") exigem esclarecimentos constantes.
