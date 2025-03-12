#!python3

class Produto:
	def __init__(self, nome, preco=1.9, desc=0):
		self.nome = nome
		self.__preco = preco
		self.desc = desc

	@property
	def preco(self):
		return self.__preco
	
	@preco.setter
	def preco(self, novo_preco):
		
		if novo_preco > 0:
			return f'R$ {self.__preco}'

	@property
	def preco_final(self):
		return (1-self.desc) * self.__preco

p1 = Produto('Caneta', 5.99, 0.1)
p1 = Produto('Caderno', 13.99, 0.15)


p1.preco = 71.89
p2.preco = 17.98

print(p1.nome, p1.preco, p1.desc, p1.preco_final
print(p2.nome, p2.preco, p2.desc, p2.preco_final)


