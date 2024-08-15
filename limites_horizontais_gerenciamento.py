from shapely.geometry import Polygon
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as PolygonPatch
from shapely.geometry import Polygon, MultiPolygon

class InterfaceHorizontal():
    def __init__(self, vertices):
        self.vertices = vertices
        self.k = 1
    def Area(self):
        pgon = Polygon(self.vertices) # Assuming the OP's x,y coordinates
        area = pgon.area
        return area

def Pares_Coordenadas(figura):
    figura = figura.replace(" ","")
    pares_coordenadas = figura.split("),(")
    lista_de_tuplas = [(float(par.split(",")[0].replace("(","").replace(")","")), float(par.split(",")[1].replace("(","").replace(")",""))) for par in pares_coordenadas]
    return lista_de_tuplas

def Pares_CoordenadasInternas(figura):
    figura = figura.replace(" ","")
    furos = figura.split("],[")
    lista_furos = []
    for furo in furos:
        furo = furo.replace("[","")
        furo = furo.replace("]","")
        pares_coordenadas = furo.split("),(")
        lista_de_tuplas = [(float(par.split(",")[0].replace("(","").replace(")","")), float(par.split(",")[1].replace("(","").replace(")",""))) for par in pares_coordenadas]
        lista_furos.append(lista_de_tuplas)
    return lista_furos

# Função para encontrar a interseção de duas figuras
def encontrar_intersecao(poligono1, poligono2):

    intercessao = poligono1.intersection(poligono2)
    #return list(intersecao.exterior.coords), list(intersecao.interior.coords)
    return intercessao



# Função para encontrar as regiões não cobertas pelas figuras menores na figura principal
def encontrar_regioes_nao_cobertas(figura_principal, figuras_menores):
    poligono_principal = Polygon(figura_principal)
    regioes_nao_cobertas = poligono_principal
    for figura in figuras_menores:
        poligono_figura = Polygon(figura)
        regioes_nao_cobertas = regioes_nao_cobertas.difference(poligono_figura)
    return list(regioes_nao_cobertas.exterior.coords)

#encontra as interfaces que não sejam internas

def interfaces_externas(figuras_principais, figuras_menores):

    nova_figura = figuras_principais.difference(figuras_menores)

    return nova_figura

if __name__ == '__main__':
    
    # Exemplo de duas figuras
    figura1 = [(0, 0), (0, 1), (1, 1), (1, 0)]
    figura2 = [(0.3, 0.3), (0.5, 1.5), (1.5, 1.5), (1.5, 0.5)]

    # Encontrar a interseção das duas figuras
    intersecao = encontrar_intersecao(figura1, figura2)
    print("Coordenadas da figura de interseção:", intersecao)


    #fechar figuras
    figura1.append(figura1[0])
    figura2.append(figura2[0])

    x_coords = [tupla[0] for tupla in figura1]
    y_coords = [tupla[1] for tupla in figura1]

    # Plotar as coordenadas
    plt.plot(x_coords, y_coords, marker='o', linestyle='-', color='blue')
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.title('Plot de Lista de Tuplas')
    plt.grid(True)

    x_coords = [tupla[0] for tupla in figura2]
    y_coords = [tupla[1] for tupla in figura2]

    # Plotar as coordenadas
    plt.plot(x_coords, y_coords, marker='o', linestyle='-', color='green')
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.title('Plot de Lista de Tuplas')
    plt.grid(True)

    x_coords = [tupla[0] for tupla in intersecao]
    y_coords = [tupla[1] for tupla in intersecao]

    # Plotar as coordenadas
    plt.plot(x_coords, y_coords, marker='o', linestyle='-', color='red')
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.title('Plot de Lista de Tuplas')
    plt.grid(True)
    plt.show()


    # Definindo as coordenadas da figura original e da figura para subtrair
    figura_original = Polygon([(0, 0), (0, 5), (2, 5), (2, 0)])
    figura_para_subtrair = Polygon([(-1, 1), (-1, 3), (3, 3), (3, 1)])
    figuras_principais = [figura_original]
    figuras_menores = [figura_para_subtrair]
    interfaces_externas(figuras_principais, figuras_menores)