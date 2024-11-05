#!python3

class Contador:

	contador = 0

	@classmethod
	def inc(cls):
		cls.contador += 1
		return cls.contador

	@classmethod
	def dec(cls):
		cls.contador -= 1
		return cls.contador


c1 = Contador()

print(c1.inc)
print(c1.inc)
print(c1.inc)
print(c1.inc)
print(c1.dec)
print(c1.dec)
print(c1.inc)
print(c1.inc)
