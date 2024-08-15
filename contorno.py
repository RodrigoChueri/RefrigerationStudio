from shapely.geometry import Point, Polygon
import matplotlib.pyplot as plt
import math
import geometria
import numpy as np
import matematica
from operator import itemgetter
from estrutura_dados import Ponto

def discretização_interna(planos_poligonos, resolucao, camadas_contorno):


    #cria uma lista que vai acomodar todos os poligonos que serão analisados separando por andar
    total_andares = len(planos_poligonos)
    pontos_internos = []
    pontos_contorno = []
    pontos_discretizados =[]
    for i in range(total_andares):
        pontos_internos.append([])
        pontos_contorno.append([])
        pontos_discretizados.append([])

    #varre cada andar
    andar = 0
    for andar_poligonos in planos_poligonos:
        #varre cada poligono em determinado andar
        pontos_discretizados_andar = {}
        for poligono, cor, ambiente, dados_adicionais in andar_poligonos:
            
            #[(x1,y1),...]
            pontos_internos = geometria.listar_pontos_dentro_poligono(poligono, resolucao,resolucao, camadas_contorno)
            pontos_contorno = discretizar(poligono, resolucao, fechar_poligono=True)
            pontos_discretizados_andar[ambiente] = {"pontos internos": pontos_internos, "pontos contorno": pontos_contorno }
        pontos_discretizados[andar] = pontos_discretizados_andar
        andar += 1


    #A partir daqui podemos levar as duas listas a uma função que faça uma matriz tridimencional [z][x][y] onde z é o andar
    valor_min_x, valor_max_x ,  valor_min_y,  valor_max_y = LimitesDiscretiveis(pontos_discretizados, margem_extra=10)
    

    return valor_min_x, valor_max_x ,  valor_min_y,  valor_max_y, pontos_discretizados



# encontra os limites que devem ser usados para trabalhar
def LimitesDiscretiveis(pontos_discretizados, margem_extra):
    valor_max_x = pontos_discretizados[0][list(pontos_discretizados[0].keys())[0]]["pontos contorno"][0][0]
    valor_min_x = pontos_discretizados[0][list(pontos_discretizados[0].keys())[0]]["pontos contorno"][0][0]
    valor_max_y = pontos_discretizados[0][list(pontos_discretizados[0].keys())[0]]["pontos contorno"][0][1]
    valor_min_y = pontos_discretizados[0][list(pontos_discretizados[0].keys())[0]]["pontos contorno"][0][1]
        
    for andar in pontos_discretizados:
        pontos_contorno = []
        for ambiente_key,ambiente in andar.items():
            pontos_contorno.extend(ambiente["pontos contorno"])

        andar_count = 0
        for andar in pontos_contorno:
            lista_x, lista_y = zip(*(pontos_contorno))
            _valor_max_x = max(lista_x)
            _valor_min_x = min(lista_x)
            _valor_max_y = max(lista_y)
            _valor_min_y = min(lista_y)
            if(_valor_max_x>valor_max_x):
                valor_max_x = _valor_max_x
            if(_valor_max_y>valor_max_y):
                valor_max_y = _valor_max_y
            if(_valor_min_x<valor_min_x):
                valor_min_x = _valor_min_x
            if(_valor_min_y<valor_min_y):
                valor_min_y = _valor_min_y
            andar_count+=1

    valor_min_x = valor_min_x - margem_extra
    valor_max_x = valor_max_x + margem_extra
    valor_min_y = valor_min_y - margem_extra
    valor_max_y = valor_max_y + margem_extra

    print("Valor máximo em X:", valor_max_x)
    print("Valor mínimo em X:", valor_min_x)
    print("Valor máximo em Y:", valor_max_y)
    print("Valor mínimo em Y:", valor_min_y)
    
    return  valor_min_x, valor_max_x ,  valor_min_y,  valor_max_y 
    
def unir_poligonos(poligonos):


    # Combinar as coordenadas
    coordenadas = []
    for poligono in poligonos:
        print("numero total de pontos" + str(len(poligono)))
        coordenadas.extend(poligono)

    # Encontrar a casca convexa
    pontos = [Point(x, y) for x, y in coordenadas]
    casca_convexa = Polygon(pontos).convex_hull

    # Extrair as coordenadas da casca convexa
    coordenadas_figura = [(x, y) for x, y in casca_convexa.exterior.coords]



    # Plotar os polígonos originais
    plt.subplot(121)
    for poligono in poligonos:
        plt.plot(*zip(*poligono), color='blue')
    plt.title('Polígonos originais')

    # Plotar o novo polígono
    plt.subplot(122)
    plt.plot(*zip(*coordenadas_figura), color='red')
    plt.title('Casca convexa')

    # Mostrar o gráfico
    plt.show()

    return coordenadas_figura



#discretiza as bordas
def discretizar(poligono, resolucao, fechar_poligono):

    #garante a reta final entre a coordenada final e a inicial
    if fechar_poligono == True:
        poligono.append(poligono[0])

    # Gerando pontos
    pontos = []

    ponto_i0 = poligono[0]
    ponto_i1 = poligono[1]
    x0=0
    y0=0
    x1=0
    y1=0

    i=0
    for ponto in poligono:
        ponto_i1 = ponto
        (x0, y0) = ponto_i0
        (x1, y1) = ponto_i1
        ponto_i0 = [x0,y0]
        ponto_i1 = [x1,y1]
        # comprimento do lado
        comprimento = math.dist(ponto_i0,ponto_i1)


        comprimento_x = abs(x1-x0)
        comprimento_y = abs(y1-y0)

        sentido_crescimento_x = 0
        sentido_crescimento_y = 0
        if(x0>x1):
            sentido_crescimento_x= -1
        if(x1>x0):
            sentido_crescimento_x= 1

        if(y0>y1):
            sentido_crescimento_y= -1
        if(y1>y0):
            sentido_crescimento_y= 1
        
        if(i!=0):

            # quero que tudo esteja em função do crescimento do maior lado
            j = 0
            if(comprimento_x>comprimento_y):
                inclinação = abs((y1-y0)/(x1-x0))

                x = x0 
                y = y0
                #eqnt ainda estivermos entre os vertices 1 e 2
                while ( (x>=x0 and x<=x1) or (x<=x0 and x>=x1) ):
                    pontos.append((x, y))
                    x = x0 + j*resolucao*sentido_crescimento_x
                    y = y0 + inclinação*j*resolucao*sentido_crescimento_y
                    j+=1
                    
            if(comprimento_x<comprimento_y):
                inclinação = abs((x1-x0)/(y1-y0))

                y = y0
                x = x0
                #eqnt ainda estivermos entre os vertices 1 e 2
                while ( (y>=y0 and y<=y1) or (y<=y0 and y>=y1) ):
                    pontos.append((x, y))
                    y = y0 + j*resolucao*sentido_crescimento_y
                    x = x0 + inclinação*j*resolucao*sentido_crescimento_x
                    j+=1                 
            
        ponto_i0 = ponto_i1
        i+=1


    # Plotando os pontos
    # plt.plot(*zip(*pontos), marker="o", color="black", markersize=1)
    # plt.show()

    return pontos





def main(poligonos,resolucao):
    poligonos_discretizados = []
    for poligono in poligonos:
        plt.plot(*zip(*poligono), color="black")
        plt.show()
        poligono_discretizado = discretizar(poligono,resolucao, fechar_poligono=False)

        poligonos_discretizados.append(poligono_discretizado)

    pontos_contorno = unir_poligonos(poligonos_discretizados)
    pontos_internos = geometria.listar_pontos_dentro_poligono(pontos_contorno, resolucao, resolucao, 0)
    data_array = np.array(pontos_internos)
    # Separar valores X e Y
    x_values = data_array[:, 0]
    y_values = data_array[:, 1]
    # # Plotar pontos
    plt.plot(x_values, y_values, "o", markersize=1)
    plt.show()




resolucao = 0.2
# Lista de polígonos
poligonos = [
    [(0, 0), (10, 0), (10, 10), (0, 10),(0,0)],
        [(-11, 0), (4, 11), (11, 0), (-11,0)]
    ]

if __name__ == '__main__':
    main(poligonos,resolucao)
