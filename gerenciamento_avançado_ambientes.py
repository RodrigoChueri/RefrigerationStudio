import shapely
import eventosTabela
from PyQt5 import QtWidgets

#deixa em um formato que o shapely use
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


def CriaPoligonoShapely(coordenadas_externas, coordenadas_internas = None):
    if(coordenadas_internas != None and coordenadas_internas != "NA" and coordenadas_internas != "[]"):
        coordenadas_internas = Pares_CoordenadasInternas(coordenadas_internas)
        coordenadas_externas = Pares_Coordenadas(coordenadas_externas)
        print(str(coordenadas_externas))
        print(str(coordenadas_internas))
        plano_novo_poligono = shapely.Polygon(coordenadas_externas, holes = coordenadas_internas)
    else:
        coordenadas_externas = Pares_Coordenadas(coordenadas_externas)
        plano_novo_poligono = shapely.Polygon(coordenadas_externas)
    return plano_novo_poligono

#quando criado um poligono verifica todos os poligonos do andar e vai subtraindo os que tiverem interseção
def subtrai_de_todos_poligonos(Q_tabela_ambientes, coordenadas_novo_poligono, andar1, nome_ambiente):
    tabela_ambientes = eventosTabela.ConteudosTabela_ARR(Q_tabela_ambientes)
    intefaces_usadas_piso = []
    intefaces_usadas_teto = []
    #encontra as coordenadas das intefaces RESTANTES
    plano_novo_poligono = shapely.Polygon(coordenadas_novo_poligono)
    rowPosition=0
    linhas_a_remover = [] #lista de linhas que devem ser removidas completamente
    for linha2 in tabela_ambientes:
        andar2 = linha2[8]
        ambiente2 = linha2[0]
        if(andar1 == andar2 and nome_ambiente != ambiente2):
            print(ambiente2)
            coordenadas_externas = linha2[7]
            coordenadas_internas = linha2[13]
            planos_poligono2 = CriaPoligonoShapely(coordenadas_externas,  coordenadas_internas)
            planos_subtraidos = planos_poligono2.difference(plano_novo_poligono)
            # se restar mais de um poligono também é adicionado um ambiente novo, por exemplo se um ambiente maior virar dois ambientes menores porque foi cortado
            if isinstance(planos_subtraidos, shapely.MultiPolygon):
                for i, poly in enumerate(planos_subtraidos.geoms):
                    coordenadas = []
                    buraco = []
                    try:
                        for interior in poly.interiors:
                            buraco.append(interior.coords[:])
                        coordenadas = [list(poly.exterior.coords),buraco]
                    except: 
                        coordenadas = [list(poly.exterior.coords),  []]
            elif isinstance(planos_subtraidos, shapely.MultiLineString):
                None
            else:
                buraco = []
                for interior in planos_subtraidos.interiors:
                    buraco.append(interior.coords[:])
                try:
                    coordenadas_externas_list = list(planos_subtraidos.exterior.coords)
                    coordenadas_externas_list.pop()
                    coordenadas_externas = str(coordenadas_externas_list).replace("[","").replace("]","").replace(" ","")
                    Q_tabela_ambientes.setItem(rowPosition, 7, QtWidgets.QTableWidgetItem(str(coordenadas_externas)))
                    Q_tabela_ambientes.setItem(rowPosition, 13, QtWidgets.QTableWidgetItem(str(buraco)))
                    area = planos_subtraidos.area
                    Q_tabela_ambientes.setItem(rowPosition, 11, QtWidgets.QTableWidgetItem(str(area)))
                except:
                    linhas_a_remover.append(rowPosition)

        rowPosition+=1
        
    #remove as linhas que estão com poligonos vazios da tabela
    removidos = 0
    for item in linhas_a_remover:
        Q_tabela_ambientes.removeRow(item-removidos)
        removidos +=1
    return Q_tabela_ambientes


