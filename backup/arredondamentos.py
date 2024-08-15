proximidade = 0.2
def main(salas):
    salas_novo = []
    for sala in salas:
        vertices = sala
        vertices = aproximar_para_multiplo(vertices)
        salas_novo.append(vertices)
    return salas_novo

def aproximar_para_multiplo(lista):
    lista_aproximada = []
    for numero in lista:
        multiplo = round(numero / proximidade) * proximidade
        multiplo = round(multiplo, 1)
        lista_aproximada.append(multiplo)
    return lista_aproximada

def arredondar_int(numero, resolução):
    multiplo = round(numero / resolução) * resolução
    multiplo = round(multiplo, 1)
    return int(multiplo)

# Exemplo de uso:
sala1 = [2.23, 2.4, 3.12]
sala2 = [4.6, 3.1, 7.7]
x = 0.3
salas = [sala1, sala2]
novas_salas = main(salas)
print("Lista original:", salas)
print("Lista aproximada para múltiplos de", x, ":", novas_salas)
