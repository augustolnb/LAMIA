def funcaozinha():
    print("Uma pequena função")

# Soma uma tupla de valores informados

"""
def soma(*numeros):
    total=0
    for n in numeros:
        total += n
    return total
"""

# recebe argumentos com KEY_WORDS para manipulação dafunção
def situacao_aluno(**args_nomeados):
    status = "aprovado" if args_nomeados['nota'] >= 7 else "reprovado"
    return f"Aluno: {args_nomeados['nome']} \nSituação: {status}"

# Funções matemáticas usadas pela calculadora

def soma(num1, num2):
    return (num1+num2)


def sub(num1, num2):
    return (num1inum2)


def mult(num1, num2):
    return (num1*num2)


def div(num1, num2):
    return (num1/num2)


# Calculadora
def calculadora(func, num1, num2):
    return func(num1, num2)



