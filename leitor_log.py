print("Carregando módulo de importação de CAD...")

class ImportCad():
    def __init__(self):
        self.poligonos_não_processados = []
        self.poligonos = []
        self.linhas = []
        self.andares = []
    def ClassificarItems(self, caminho):
        with open(caminho, "r") as f:
            lines = f.readlines()
            estado = ""
            poligono = []
            ultimo_ponto = []
            Z = None
            X1 = None
            Y1 = None
            Z1 = None
            for line in lines:
                if(estado == "LWPOLYLINE" and "at point" in line):
                    _linha = line.replace(" ", "").replace("\n", "")

                    X = int(float(_linha.split("X=")[1].split("Y=")[0]) * 100)
                    Y = int(float(_linha.split("Y=")[1].split("Z=")[0]) * 100)
                    Z = int(float(_linha.split("Z=")[1]) * 100)
                    if(Z not in self.andares):
                        self.andares.append(Z)
                    ultimo_ponto = (X,Y)
                    poligono.append(ultimo_ponto)

                if(estado == "LINE"):
                    _linha = line.replace(" ", "").replace("\n", "")
                    if("from point" in line):
                        X1 = int(float(_linha.split("X=")[1].split("Y=")[0]) * 100)
                        Y1 = int(float(_linha.split("Y=")[1].split("Z=")[0]) * 100)
                        Z1 = int(float(_linha.split("Z=")[1]) * 100)
                    if("to point" in line):
                        X2 = int(float(_linha.split("X=")[1].split("Y=")[0]) * 100)
                        Y2 = int(float(_linha.split("Y=")[1].split("Z=")[0]) * 100)
                        Z2 = int(float(_linha.split("Z=")[1]) * 100)
                        self.linhas.append(((X1,Y1),(X2,Y2)))

                if("LWPOLYLINE" in line):
                    novo_estado = "LWPOLYLINE"
                    self.CriarAção(poligono, estado, novo_estado, ultimo_ponto, Z)
                    estado = "LWPOLYLINE"
                    poligono = []
                if (" LINE" in line):
                    novo_estado = "LINE"
                    self.CriarAção(poligono, estado, novo_estado, ultimo_ponto, Z)
                    estado = "LINE"
                    poligono = []

    def CriarAção(self, poligono, estado, novo_estado, ultimo_ponto, Z):
        if(poligono == []):
            return 0
        
        if(estado == "LWPOLYLINE"):
            if([poligono, Z] not in self.poligonos_não_processados):
                self.poligonos_não_processados.append([poligono, Z])
            poligono = []







    def main(self, caminho):
        self.ClassificarItems(caminho)
        print(str(self.poligonos_não_processados))
        print(str(self.linhas))


        self.andares.sort()
        andares_dict = {}
        i = 0
        for Z in self.andares:
            andares_dict[Z] = i
            i+=1
        return self.poligonos_não_processados, andares_dict

if __name__ == '__main__':
    caminho = "exportado.log"
    importar = ImportCad()
    importar.main(caminho)


from shapely.geometry import LineString, Point, Polygon
from collections import defaultdict
import itertools

# Função para criar o grafo a partir da lista de segmentos
def criar_grafo(segmentos):
    grafo = defaultdict(list)
    for ponto1, ponto2 in segmentos:
        grafo[ponto1].append(ponto2)
        grafo[ponto2].append(ponto1)
    return grafo

# Função para encontrar todos os ciclos (polígonos) no grafo
def encontrar_ciclos(grafo):
    def dfs(no, inicio, caminho, visitados):
        caminho.append(no)
        visitados.add(no)
        
        for vizinho in grafo[no]:
            if vizinho == inicio and len(caminho) > 2:
                ciclo = Polygon(caminho)
                if ciclo.is_valid:
                    ciclos.append(ciclo)
            elif vizinho not in visitados:
                dfs(vizinho, inicio, caminho, visitados)
        
        caminho.pop()
        visitados.remove(no)
    
    ciclos = []
    for no in grafo:
        dfs(no, no, [], set())
    
    return ciclos

from shapely.geometry import LineString, Point, Polygon
from collections import defaultdict
import itertools

# Função para criar o grafo a partir da lista de segmentos
def criar_grafo(segmentos):
    grafo = defaultdict(list)
    for ponto1, ponto2 in segmentos:
        grafo[ponto1].append(ponto2)
        grafo[ponto2].append(ponto1)
    return grafo

# Função para encontrar todos os ciclos (polígonos) no grafo
def encontrar_ciclos(grafo):
    def dfs(no, inicio, caminho, visitados):
        caminho.append(no)
        visitados.add(no)
        
        for vizinho in grafo[no]:
            if vizinho == inicio and len(caminho) > 2:
                ciclo = Polygon(caminho)
                if ciclo.is_valid and len(caminho) == 4:  # Verifica se o polígono é um triângulo (4 pontos, incluindo o ponto inicial)
                    ciclos.append(ciclo)
            elif vizinho not in visitados:
                dfs(vizinho, inicio, caminho, visitados)
        
        caminho.pop()
        visitados.remove(no)
    
    ciclos = []
    for no in grafo:
        dfs(no, no, [], set())
    
    return ciclos

# Função principal para encontrar os menores polígonos (triângulos)
def menores_poligonos(segmentos):
    grafo = criar_grafo(segmentos)
    ciclos = encontrar_ciclos(grafo)
    ciclos.sort(key=lambda p: p.area)  # Ordena os ciclos por área
    menores_ciclos = []
    menor_area = None
    
    for ciclo in ciclos:
        if menor_area is None or ciclo.area == menor_area:
            menores_ciclos.append(ciclo)
            menor_area = ciclo.area
        elif ciclo.area > menor_area:
            break
    
    return menores_ciclos

if __name__ == '__main__':


    # Exemplo de uso
    segmentos = [
        ((3098, 1856), (3232, 1073)), 
        ((3232, 1073), (4063, 1432)), 
        ((4063, 1432), (3098, 1856)), 
        ((1729, 1748), (3007, 817)), 
        ((3007, 817), (2754, 1805)), 
        ((2754, 1805), (1729, 1748)), 
        ((2754, 1805), (3662, 1367)), 
        ((3662, 1367), (3007, 817))
    ]

    # Encontrar os menores polígonos (triângulos)
    menores_ciclos = menores_poligonos(segmentos)

    # Imprimir os menores polígonos (triângulos)
    for i, ciclo in enumerate(menores_ciclos):
        print(f"Triângulo {i+1}: {list(ciclo.exterior.coords)} com área {ciclo.area}")


