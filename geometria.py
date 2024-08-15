import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from matplotlib.path import Path
import numpy as np
from operator import itemgetter
from math import gcd
import math
#resolução da malha
dx = 0.5
dy = 0.5
#calculo automatico dos valores dx e dy?
dx_dy_automatico = True
n_partes = 100

def resolução_malha(poligono1):
    if(dx_dy_automatico == True):
      # Inicializar os valores mínimos e máximos
        min_x = float("inf")
        max_x = float("-inf")
        min_y = float("inf")
        max_y = float("-inf")

      # Percorrer a lista de tuplas
        for tupla in poligono1:
            x, y = tupla

            # Atualizar os valores mínimos e máximos se necessário
            if x < min_x:
              min_x = x
            if x > max_x:
              max_x = x
            if y < min_y:
              min_y = y
            if y > max_y:
              max_y = y


    dx = (max_x-min_x)/n_partes
    dy = (max_y-min_y)/n_partes
    print("dx="+str(dx) + " dy="+ str(dy))
    



def find_points_between_vertices(vertex1, vertex2):
    points = []

    print(str(vertex1))
    x1, y1 = vertex1
    x2, y2 = vertex2
    dx = x2 - x1
    dy = y2 - y1
    steps = 30
    if steps == 0:
        return []
    x_increment = dx / steps
    y_increment = dy / steps
    x = x1
    y = y1
    for _ in range(steps):
        x += x_increment
        y += y_increment
        points.append((round(x, 2), round(y, 2)))
    return points

def find_points_between_vertices2(vertex1, vertex2,resolução):
    points = [vertex1]

    x1, y1 = vertex1
    x2, y2 = vertex2
    dx = x2 - x1
    dy = y2 - y1
    steps = abs(int(dx/resolução))


    if(steps!= 0):
        total_incrementado = 0
        x_increment = resolução*dx/abs(dx)
        x = x1
        y = y1
        while(abs(total_incrementado)<abs(x2-x1)):
            x += x_increment
            y += dy/dx * x_increment
            points.append((round(x, 2), round(y, 2)))
            total_incrementado+=x_increment
    else:
        total_incrementado = 0
        steps = abs(int(dy/resolução))
        y_increment = resolução*dy/abs(dy)
        x = x1
        y = y1
        while(abs(total_incrementado)<abs(y2-y1)):
            y += y_increment
            x += dx/dy * y_increment
            points.append((round(x, 2), round(y, 2)))
            total_incrementado+=y_increment

    #remove pontos repetidos
    x_anterior = points[0][0]
    y_anterior = points[0][1]
    pontos = [(x_anterior,y_anterior)]
    for ponto in points:
        x = ponto[0]
        y = ponto[1]
        if(x!=x_anterior or y!=y_anterior):
            pontos.append((x,y))
        x_anterior = x
        y_anterior = y
        
    return pontos


def pontosNotaveisParede(tabela_antiga):
    pontos_notaveis = []
    for linha in tabela_antiga:
        vertices = linha[3]
        p1_str = vertices.split("),(")[0].replace("(","").replace(")","")
        p2_str = vertices.split("),(")[1].replace("(","").replace(")","")
        p1 = (float(p1_str.split(",")[0]),float(p1_str.split(",")[1]) )
        p2 = (float(p2_str.split(",")[0]),float(p2_str.split(",")[1]) )
        pontos_notaveis.append(p1)
        pontos_notaveis.append(p2)

    pontos_notaveis = list(set(pontos_notaveis))
    return pontos_notaveis

def arredondamentoPontosNotaveisParede(tabela_antiga, tabela_nova):
    pontos_notaveis = pontosNotaveisParede(tabela_antiga)
    for linha in tabela_nova:
        p1_str = linha[3].split("),(")[0].replace("(","").replace(")","")
        p2_str = linha[3].split("),(")[1].replace("(","").replace(")","")
        p1 = (float(p1_str.split(",")[0]),float(p1_str.split(",")[1]) )
        p2 = (float(p2_str.split(",")[0]),float(p2_str.split(",")[1]) )
        for ponto_antigo in pontos_notaveis:
            if(abs(ponto_antigo[0]-p1[0]) <=0.03 and abs(ponto_antigo[1]-p1[1])<=0.03 ):
                p1 = ponto_antigo
            if(abs(ponto_antigo[0]-p2[0]) <=0.03 and abs(ponto_antigo[1]-p2[1])<=0.03 ):
                p2 = ponto_antigo

        vertices = str(p1).replace(" ","") + "," + str(p2).replace(" ", "")
        linha[3] = vertices

    return tabela_nova            




def find_points_in_polygon(vertices):
    points = []
    for i in range(len(vertices)):
        vertex1 = vertices[i]
        vertex2 = vertices[(i + 1) % len(vertices)]
        points += find_points_between_vertices(vertex1, vertex2)
    return points




def plot_graph_2_superficies(vertices, pontos_união, points, points2):
    fig, ax = plt.subplots()
    
##    x_values = [vertex[0] for vertex in vertices]
##    y_values = [vertex[1] for vertex in vertices]
##    ax.plot(x_values, y_values, marker='o', linestyle='-')
    
    unique_points = list(set(points))  # Removendo pontos duplicados
    x_points = [point[0] for point in unique_points]
    y_points = [point[1] for point in unique_points]
    ax.plot(x_points, y_points, marker='o', linestyle='', color='red', markersize = 1)

    unique_points2 = list(set(points2))  # Removendo pontos duplicados
    x_points2 = [point[0] for point in unique_points2]
    y_points2 = [point[1] for point in unique_points2]
    ax.plot(x_points2, y_points2, marker='o', linestyle='', color='blue', markersize = 1)

    unique_points_união = list(set(pontos_união))
    x_points_união = [point[0] for point in pontos_união]
    y_points_união = [point[1] for point in pontos_união]
    ax.plot(x_points_união, y_points_união, marker='o', linestyle='', color='green', markersize = 1)


##    poly = Polygon(vertices, closed=True, fill=True, edgecolor='none', facecolor='yellow', alpha=0.3)
##    ax.add_patch(poly)

    ax.set_title('Graph')
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.grid(True)
    plt.show()

#verifica se o ponto dado tá dentro do poligono
def point_inside_polygon(x, y, poly):
    path = Path(poly)
    return path.contains_point((x, y))

def Intercessão(list1, list2):
    common_points = []
    exclusive_points_list1 = []
    exclusive_points_list2 = []

    set1 = set(list1)
    set2 = set(list2)

    # Pontos em comum
    common_points = list(set1.intersection(set2))

    # Pontos exclusivos da lista 1
    exclusive_points_list1 = list(set1.difference(set2))

    # Pontos exclusivos da lista 2
    exclusive_points_list2 = list(set2.difference(set1))

    return common_points, exclusive_points_list1, exclusive_points_list2

#área = dx*nx * dy*ny =  dx*dy*nx*ny = dx*dy * num_pontos
def Area(pontos):
    return len(pontos)*dx*dy
    
#gera camadas adicionais na discretização dos pontos internos garantindo que n]ao vai faltar pontos
def MargemSegurança(pontos, dx_,dy_, camadas_contorno):

    #retas tem zero pontos internos, logo len é zero
    if(len(pontos) == 0):
        return []

    #organiza com base no segundo valor de cada tupla em ordem crescente, por exemplo se tenho as tuplas (3,5),(7,1),(5,5),(8,2) 
    #quero que elas fiquem na ordem (7,1),(8,2),(3,5),(5,5)
    coordenadas_ordenadas_em_y = sorted(pontos, key=itemgetter(1))
    coordenadas_ordenadas_em_x = sorted(pontos, key=itemgetter(0))

    contorno = []
    #vai subindo em y, cada "linha horizontal" é analizado ql é o extremo menor e maior em função de x
    y = coordenadas_ordenadas_em_y[0][1]
    x_menor = coordenadas_ordenadas_em_y[0][0]
    x_maior = coordenadas_ordenadas_em_y[0][0]
    for coordenada in coordenadas_ordenadas_em_y:
        #coordenadas atuais
        x_i = coordenada[0]
        y_i = coordenada[1]
        #agora passou para um y maior, registra o valor antigo
        if(y_i != y):
            #registra o contorno com folga de n vezes para cada lado para este determinado y que passou
            camada = 1
            while (camada<=camadas_contorno):
                x_contorno_menor = x_menor - dx_*camada
                x_contorno_maior = x_menor + dx_*camada
                contorno.append((x_contorno_menor,y))
                contorno.append((x_contorno_maior,y))
                camada+=1
            #reinicia os valores de analise para x
            x_menor = x_i
            x_maior = x_i
            y = y_i

        
        if(x_i<x_menor):
            x_menor = x_i
        if(x_i>x_maior):
            x_maior = x_i

    #registra a coordenada final
    while (camada<=camadas_contorno):
        x_contorno_menor = x_menor - dx_*camada
        x_contorno_maior = x_maior + dx_*camada
        contorno.append((x_contorno_menor,y))
        contorno.append((x_contorno_maior,y))
        camada+=1

    #vai subindo em x, cada "linha horizontal" é analizado ql é o extremo menor e maior em função de x
    x = coordenadas_ordenadas_em_x[0][0]
    y_menor = coordenadas_ordenadas_em_x[0][1]
    y_maior = coordenadas_ordenadas_em_x[0][1]
    for coordenada in coordenadas_ordenadas_em_x:
        #coordenadas atuais
        x_i = coordenada[0]
        y_i = coordenada[1]
        #agora passou para um y maior, registra o valor antigo
        if(x_i != x):
            #registra o contorno com folga de n vezes para cada lado para este determinado y que passou
            camada = 1
            while (camada<=camadas_contorno):
                y_contorno_menor = y_menor - dy_*camada
                y_contorno_maior = y_maior + dy_*camada
                contorno.append((x,y_contorno_menor))
                contorno.append((x,y_contorno_maior))
                camada+=1
            #reinicia os valores de analise para y
            y_menor = y_i
            y_maior = y_i
            x = x_i

        
        if(y_i<y_menor):
            y_menor = y_i
        if(y_i>y_maior):
            y_maior = y_i

    #registra a coordenada final
    while (camada<=camadas_contorno):
        y_contorno_menor = y_menor - dy_*camada
        y_contorno_maior = y_maior + dy_*camada
        contorno.append((x,y_contorno_menor))
        contorno.append((x,y_contorno_maior))
        camada+=1



    return contorno

#gera a lista de pontos dentro do poligono dado
#marge de segurança garante que pontos mesmo que levemente para fora sejam preenchidos mas grantindo que nenhuma região dentro dos poligonos não tenha preenchimento
def listar_pontos_dentro_poligono(vertices, dx_, dy_, camadas_contorno):
    
    border_points = find_points_in_polygon(vertices)

    # Encontrando os pontos dentro do polígono usando método de preenchimento de polígono
    x_min, y_min = np.min(vertices, axis=0)
    print(str(x_min))
    x_max, y_max = np.max(vertices, axis=0)
    points_inside = []
    for x in np.arange(x_min, x_max, dx_):
        for y in np.arange(y_min, y_max, dy_):
            if point_inside_polygon(x, y, vertices):
                points_inside.append((round(x, 2), round(y, 2)))

    margens_externas = MargemSegurança(points_inside, dx_,dy_, camadas_contorno)
    points_inside = points_inside + margens_externas
    return points_inside


def razão_area_intercessão(area,area_intercessão):
    return area_intercessão/(area)



def discretizar_interno(poligono):
    resolução_malha(poligono)
    None




    


#serve para criar suvparedes a partir de paredes que sejam colineares
#separa dois segmentos colineares
#por exemplo ((0,0),(10,100)) com ((2,20),(4,40)) que seria identificado como colinear e retornaria ((0,0),(2,20)), ((2,20),(4,40)), ((4,40),(10,100))
def separar_em_subparedes(linha1, linha2, ambiente1, ambiente2, resolução):
    
    linha1_discretizada = find_points_between_vertices2(linha1[0], linha1[1], resolução)
    linha2_discretizada = find_points_between_vertices2(linha2[0], linha2[1], resolução)

    print(str(linha1) + str(linha2))
    colinear, pontos_em_comum = Colinear(linha1_discretizada, linha2_discretizada)
    if(colinear == True):
        todos_pontos = [linha1[0],linha1[1]]
        todos_pontos.extend([linha2[0],linha2[1]])
        #remove pontos repetidos
        todos_pontos = list(set(todos_pontos))
        #ordena a lista
        todos_pontos.sort(key=lambda ponto: ponto[0])

        #cria os segmentos
        segmentos = []
        ambientes = []
        i=0
        ponto_anterior = ()
        for ponto in todos_pontos:
            if(i!=0):
                segmento_novo = (ponto_anterior,ponto)
                segmento_novo_discretizado = find_points_between_vertices2(segmento_novo[0], segmento_novo[1], resolução)
                ambiente_novo = ""


                parte_do_ambiente1, pontos_em_comum = Colinear(linha1_discretizada, segmento_novo_discretizado)
                parte_do_ambiente2, pontos_em_comum = Colinear(linha2_discretizada, segmento_novo_discretizado)
                if(parte_do_ambiente1 == True):
                    ambiente_novo += ambiente1 + "&"
                if(parte_do_ambiente2 == True):
                    ambiente_novo += ambiente2 + "&"


                segmentos.append(segmento_novo)
                ambientes.append(ambiente_novo)
            i+=1
            ponto_anterior = ponto
        
    
    else:
        segmentos = [linha1, linha2]
        ambientes = [ambiente1, ambiente2]
    
    return segmentos, ambientes, colinear



#se tiver dois ou mais pontos em comum é colinear
def Colinear(linha1_discretizada, linha2_discretizada):
    pontos_em_comum = list(set(linha1_discretizada) & set(linha2_discretizada))

    numero_comum = len(pontos_em_comum)
    if(numero_comum>1):
        return True, pontos_em_comum
    else:
        return False, []
    
def Comprimento(tupla):
    p1 = tupla[0]
    p2 = tupla[1]
    x1 = p1[0]
    x2 = p2[0]
    y1 = p1[1]
    y2 = p2[1]
    a = x2 - x1
    b = y2 - y1
    l = math.sqrt(math.pow(a,2) + math.pow(b,2))
    return l

def AreaParede(vertices, pé_direito):
    altura = pé_direito
    vertices = vertices.replace(" ","").split("),(")
    p1 = (float(vertices[0].replace(")", "").replace("(","").split(",")[0]),float(vertices[0].replace(")", "").replace("(","").split(",")[1]))
    p2 = (float(vertices[1].replace(")", "").replace("(","").split(",")[0]),float(vertices[1].replace(")", "").replace("(","").split(",")[1]))

    comprimento = Comprimento((p1,p2))
    area = comprimento * altura
    return area


def teste():
    vertice1 = (2.2,1.1)
    vertice2 = (4.9,1.1)
    pontos = find_points_between_vertices2(vertice1, vertice2, 0.1)



if __name__ == '__main__':
    teste()

