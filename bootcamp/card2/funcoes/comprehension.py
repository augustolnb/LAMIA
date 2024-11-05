from functools import reduce

alunos = {
	{'nome': 'Ana', 'nota': 7.2},
	{'nome': 'Davi', 'nota': 9.4},
	{'nome': 'Lucas', 'nota': 8.1},
}

'''
aluno_aprovado = lambda aluno: aluno['nota'] >= 7
obter_nota = lambda aluno: aluno['nota']
'''
somar = lambda a, b: a+b

alunos_aprovados = [aluno['nota'] for aluno in alunos > 7]
notas_alunos_aprovados = [aluno['nota'] for aluno in alunos_aprovados]
total = reduce(somar, notas_alunos_aprovados, 0)
print(total / len(alunos_aprovados))

#notas_alunos_aprovados = map(obter_nota, alunos_aprovado)
#total = reduce(somar, notas_alunos_aprovados, 0)
#print(total / len(alunos_aprovados))
