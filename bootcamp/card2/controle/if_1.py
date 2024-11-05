#!python3

nota = float(input("Nota: "))
comportado = True if input("Comportado? (s/n): ") == "s" else False

if nota >= 9:
	print("\nAprovado com mérito!!\n\n")
elif nota >=7:
	print("\nAprovado!!\n\n")
elif nota >= 6:
	print("\nAprovado no talo, precisa estudar mais.\n\n")
elif nota >= 2 and nota < 6:
	print("\nRecuperação.\n\n")
else:
	print("\nReprovado direto!!\n\n")
	
print(nota)
