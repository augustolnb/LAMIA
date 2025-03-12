#!python3

def soma(*nums):
	total=0
	for n in nums:
		total += n
	return total

def resultado_final(**kwargs):
	status = 'Aprovado' if kwargs['nota'] > 7 else 'Reprovado'
	return status