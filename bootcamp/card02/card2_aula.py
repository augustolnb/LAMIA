#!python3

print("printf com python é só print\n")
print("Em python" + " não é necessário" + " ;" + " no final das linhas\n")

from card2-biblioteca_aula import funcaozinha
funcaozinha()

texto = "O último frango da malásia"
print(f"Vendo o tipo direto do método type(): {type(texto)} ")
tipo = type(texto)
print(f"\nChecando o tipo usando uma variável: {tipo}")

import math
print("###### Continhas de matemática: ######\n")
print(f"Adição: 3 + 2 = {3+2}\nSubtração: 3 - 2 = {3-2}\nMultiplicação: 3 * 2 = {3*2}\nDivisão: 3 / 2 = {3/2}\nPotência: 3² = {3**2}\nRadiciação: sqrt(3) = {math.sqrt(3)}")

print("\n\n")

# Criando uma lista usando []
uma_lista = [1,3, 5,7,9]

# Criando outra lista usando o comando list()
outra_lista = list()

print(f"Formato de uma_lista: {type(uma_lista)}\nFormato de outra_lista: {type(outra_lista)}")

print(f"\n\numa_lista : {uma_lista}\noutra_lista : {outra_lista}")
print("Adicionado valores na outra_lista")

for i in range(1,10):
    outra_lista.append(i) # Adicionando valores de 1 a 9

print(f"\n\numa_lista : {uma_lista}\noutra_lista : {outra_lista}")


print("Acessando elementos de uma lista:")
print(uma_lista[0]) # Primeiro elemento
print(uma_lista[-1]) # Último elemento
print(uma_lista[1]) # Segundo elemento
print(uma_lista[-2]) # Penúltimo elemento

# Conjuntos { SET }

conjunto_um = {2,3,5,7,11,13,17,19} # conjunto dos numero primos

print("Este é um conjunto de dados do tipo: ")
print(type(conjunto_um))


print("\n\nAgora vamos criar um dicionario, usando o modelo\ndicionario = { \n\tchave1 : valor1, \n\tchave2 : valor2, \n\tchave3 :  valor3\n}")

pokedex = {
    172: {
        'nome': 'Pichu',
        'tipo': 'Elétrico',
        'altura': 0.3,  # metros
        'peso': 2.0,  # kg
        'habilidade': 'Static',
        'evolui_para': 'Pikachu',
        'cor': 'Amarelo'
    },
    255: {
        'nome': 'Torchic',
        'tipo': 'Fogo',
        'altura': 0.4,  # metros
        'peso': 2.5,  # kg
        'habilidade': 'Blaze',
        'evolui_para': 'Combusken',
        'cor': 'Laranja'
    },
    158: {
        'nome': 'Totodile',
        'tipo': 'Água',
        'altura': 0.6,  # metros
        'peso': 9.5,  # kg
        'habilidade': 'Torrent',
        'evolui_para': 'Croconaw',
        'cor': 'Azul'
    }
}

print(type(pokedex))
print(pokedex)

"""
Conhecendo
os 
operadores
"""

par = 34
impar = 33

print(par % 2 == 0)
print(impar % 2 == 1)

x = 13
y = 17

"""
Operadores relacionais sempre retornam valores BOOLEANOS

Python não possui o operador estritamente igual (verificando se são do mesmo tipo)

Python ja considera a verificação de tipos por padrão, apenas serão iguais se forem do mesmo tipo

"""

print("\nTestando operadores relacionais\n")

print(x > y)
print(x >= y)
print(x < y)
print(x <= y)
print(x == y)
print(x != y)

print("\n\n")

atribuicao = 2
print(f"{atribuicao}")
print(f"{atribuicao}+12")
atribuicao += 12
print(f"{atribuicao}")
print(f"{atribuicao}-6")
atribuicao -= 6
print(f"Valor final = {atribuicao}")


"""
Operadores
Lógicos

and -> função lógica E
or -> função lógica OU
not -> função lógica NEGAÇÂO

"""

b1 = True
b2 = True
b3 = False
b4 = False

print("------------------------------------")
print("AND\n------------------------------------")
# and
print(b1 and b2)
print(b2 and b3)
print(b3 and b4)
print(b4 and b1)

print("------------------------------------")
print("OR\n------------------------------------")
# or
print(b1 or b2)
print(b2 or b3)
print(b3 or b4)
print(b4 or b1)
print("------------------------------------")

"""
# Entrada de texto e operadores condicionais
nota = int(input("Informe a nota do jovem guerreirinho: "))

# palavras reservadas pela linguagem : if (se), elif(se não, se), else (se não)

if nota >= 9:
    print("É o brabo, não tem jeito")

elif nota >= 6:
    print("Aprovado, sem louvores")

else:
    print("Ja era meu nobre, agora só ano que vem")
"""

for primos in conjunto_um:
    print(f"Um número primo: {primos}")

"""
for atributo in pokedex:
    print(atributo, ' >> ', pokedex[atributo])
"""

# FOR ANINHADO
for id_pokemon, atributos in pokedex.items(): # Percorre todas as chaves do dicionario maior, os ID's de cada pokemon
    print(f"ID: {id_pokemon}")
    for chave, valor in atributos.items(): # Para cada ID, há outro dicionário vinculado, de forma que deve ser percorrido para a apresentação de seus atributos
        print(f"  {chave.capitalize()}: {valor}")
    print("-" * 30)  # Linha de separação entre os Pokémons


# Laço de repetição WHILE

x = 5

while x != 0:
    print("##################################")
    print('1 > Soma\n2 > Subtração\n3 > Multiplicação\n4 > Divisão\n\n0 >> Sair')
    print("##################################")

    x = int(input("Qual operação deseja realizar? \n>> "))
    if x == 0:
        break

    a = int(input('Primeiro valor: '))
    b = int(input('Segundo valor: '))

    print("Resultado: ")
    if x == 1:
        print(a+b)
    elif x == 2:
        print(a-b)
    elif x == 3:
        print(a*b)
    elif x == 4:
        print(a/b)
    print("\n\n")

from biblioteca import *

"""
nome = input("Nome do aluno: ")
nota = float(input("Nota do aluno: "))

print(situacao_aluno(nome=nome, nota=nota))

"""

print(f"{calculadora(div, 40, 3)}")

print("\n\n")

from functools import reduce

"""
for i, nota in enumerate(notas):
    notas[i] = nota + 1.5

"""

def somar_notas(delta):
    def somar(nota):
        return nota+delta
    return somar

notas = [6.4, 7.2, 5.8, 8.4]
nota_final = map(somar_notas(1.5), notas)

print(list(nota_final))

# soma arcaica
total = 0
for n in notas:
    total += n
print(f"\nSoma arcaica: {total:.2f}")

# soma elegante
# reduce(funcao, obj_iteravel, valor_inicial)
print(f"\nSoma elegante: {reduce(soma, notas, 0):.2f}")

"""
FUNÇÃO LAMBDA
"""

pilotos_eva = [
    {"Nome": "Shinji Ikari", "Unidade": "EVA-01", "Sincronização" : 95},
    {"Nome": "Asuka Langley", "Unidade": "EVA-02", "Sincronização" : 32},
    {"Nome": "Rei Ayanami", "Unidade": "EVA-00", "Sincronização" : 72}
]
                # lambda parâmetro : valor_de_retorno
piloto_aprovado = lambda piloto: piloto['Sincronização'] >= 80
obter_taxa = lambda piloto: piloto['Sincronização']

pilotos_aprovados = list(filter(piloto_aprovado, pilotos_eva))
taxa_pilotos_aprovados = map(obter_taxa, pilotos_aprovados)

print("\n\nPilotos de EVA: ")
print([piloto["Nome"] for piloto in pilotos_eva])

print("\nPilotos aprovados: ")
print(list([piloto["Nome"] for piloto in pilotos_aprovados]))
"""
print("\n\n")
print(obter_taxa(pilotos_eva[0]))
"""
print(f"\nTaxa de sincronização do piloto aprovado: {int(list(taxa_pilotos_aprovados)[0])}%")

