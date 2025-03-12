#!python

#for i in range(10):
#	print(i)
	
#for i in range(1, 11):
#	print(i)
	
#for i in range(1, 100, 7):
#	print(i)

#for i in range(20, 0, -3):
#	print(i)

nums = [2, 4, 6, 8, 10]

for n in nums:
	print(n, end=" ")
	
print("\n\n")

texto = "Um texto qualquer"

for letra in texto:
	print(letra)
	
print("\n\n")

produto = {
	"nome" : "Caneta",
	"preco" : 8.80,
	"desconto_max" : 0.5
}

for atrib in produto:
	print(atrib, "==>", produto[atrib])
	
print("----------------------------------------------")

for atrib, valor in produto.items():
	print(atrib, "==>", valor)

print("----------------------------------------------\nApenas valores:")

for valor in produto.values():
	print(valor, end="\n")

print("----------------------------------------------\nApenas atributos:")

for atrib in produto.keys():
	print(atrib, end="\n")

print("----------------------------------------------")

