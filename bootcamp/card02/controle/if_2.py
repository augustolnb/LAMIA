#!python3

a = "valor" 	#True
a = -0.000001 	#True
a = " " 	#True
a = "" 		#False
a = 0 		#False
a = [] 		#False
a = {} 		#False

if a:
	print("Existe\n")
else:
	print("Não existe ou é vazio\n")
