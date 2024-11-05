#!python3


total = 0
qtde = 0
nota = 0


while nota != -1:
	nota = float(input("Nota: "))
	if nota != -1:
		qtde += 1
		total += nota
		

print(f"O valor da media é: {total/qtde}")
	
print("Fim\n")
