from functools import reduce

def somar_nota(delta):
	def soma(nota):
		return nota+delta
	return somar

notas = [6.4, 7.2, 8.4]
notas_finais1 = map(somar_nota(1.5), notas)
notas_finais2 = map(somar_nota(1.6), notas)

print(notas_finais1)
print(notas_finais2)

def somar(a, b):
	return a+b

total = reduce(somar, notas, 0)
print(total)