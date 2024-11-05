#!python3

pessoas = ['Ana', 'Mayra']
adjs = ['Charmosa', 'Bonita']

for p in pessoas:
	for a in adjs:
		print(f"{p} é {a}")
		
for i in [1, 2, 3]:
	pass
	
for i in range(1,11):
	if i % 2:
		continue
	print(i)
	
for i in range(1,11):
	if i % 2:
		break
	print(i)
