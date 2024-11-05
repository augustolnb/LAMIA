#!python3

def soma(a, b):
	return a+b
def sub(a, b):
	return a-b

def op_aritmetica(fn, a, b):
	return fn(a, b)

resultado = op_aritmetica(soma, 13, 48)

print(resultado)

def soma_parcial(a):
	def concluir_soma(b)
		return a+b
	return concluir_soma

soma_1 = soma_parcial(1)
r1 = soma_1(2)
r2 = soma_1(3)
r3 = soma_1(4)

resultado_final = soma_parcial(10)(12)
print(resultado_final, r1, r2, r3)