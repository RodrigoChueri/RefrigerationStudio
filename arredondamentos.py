import math
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
        multiplo = round(multiplo, 4)
        lista_aproximada.append(multiplo)
    return lista_aproximada

def arredondar_int(numero, resolução):
    multiplo = round(numero / resolução) * resolução
    
    i = 1
    while (resolução*math.pow(10,i)<=1):
        i+=1
    i-=1
    if(resolução>=1):
        multiplo = round(multiplo, 1)
    print(str(numero) + " -> " + str(multiplo))
    return int(multiplo)

if __name__ == '__main__':
   
    # Exemplo de uso:
    sala1 = [2.23, 2.4, 3.12]
    sala2 = [4.6, 3.1, 7.7]
    x = 0.3
    salas = [sala1, sala2]
    novas_salas = main(salas)
    print("Lista original:", salas)
    print("Lista aproximada para múltiplos de", x, ":", novas_salas)
