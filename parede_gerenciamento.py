import geometria
import eventosTabela
from PyQt5 import QtWidgets
from ast import literal_eval
import math
import matplotlib.pyplot as plt
import numpy as np
from estrutura_dados import Ponto
import random
import time
import limites_horizontais_gerenciamento
import shapely
import shapely.geometry as geom
from shapely.validation import explain_validity
from shapely.geometry import LineString, MultiLineString
import shapely.geometry as geoms
import GeradorParedes
import shapely.geometry as sg
from shapely.geometry import LineString, Point

print("Carregando módulo de gerenciamento de superfícies...")

resolução = 0.01
#divide as paredes quando necesseárias em outras paredes
def AutoCriação_Paredes3(Q_tabela_paredes: QtWidgets.QTableWidget, andares_total, Q_interfaces_horizontais: QtWidgets.QTableWidget, Q_tabela_ambientes, Q_tabela_janelas_portas: QtWidgets.QTableWidget, andar_terreo, dicionario_paredes, pé_direito):
    tabela_ambientes = eventosTabela.ConteudosTabela_ARR(Q_tabela_ambientes)
    tabela_janelas_portas = eventosTabela.ConteudosTabela_ARR(Q_tabela_janelas_portas)
    nova_tabela_paredes = []
    tabela_ambientes_andar = []
    tabela_janelas_portas_andar = []
    areas_janelas_portas = {}
    #adiciona os andares a matriz
    i=0
    while (i<=andares_total): 
        tabela_ambientes_andar.append ([])
        tabela_janelas_portas_andar.append([])
        i+=1
    
    #constroi uma tabela de cada andar com as janelas e portas
#["andar", "x1","y1","x2","y2", "SHGC", "largura", "altura", "tipo", "angulo_rad", "interface", "material", "area", "angulo_Norte"
# , "angulo_horizontal", "interno/ext", "U", "espessura", "k"]

    for elemento in tabela_janelas_portas:
        andar = int(elemento[0])
        x_centro = float(elemento[1])
        y_centro = float(elemento[2])
        SHGC = str(elemento[5])
        largura = float(elemento[6])
        altura = float(elemento[7])
        tipo = elemento[8]
        angulo_rad = float(elemento[9])
        U= float(elemento[16])
        espessura = float(elemento[17])
        k = str(elemento[18])
        interface = "N/A"
        area = altura/100 * largura/100
        angulo_norte = "N/A"
        angulo_horizontal = "N/A"
        tabela_janelas_portas_andar[andar].append([andar, x_centro, y_centro,x_centro, y_centro, SHGC, largura, altura, tipo, angulo_rad, interface, "N/A", area, angulo_norte, angulo_horizontal, "N/A", U,   espessura, k])

    




    #constroi uma tabela de cada andar com os ambientes/poligonos
    # [["ambiente1", 0,0,0,0,poligono1] , ["ambiente2", 0,0,0,0,poligono2] ...]
    for ambiente in tabela_ambientes:
        ambiente_nome  = ambiente[0]
        andar = int(ambiente[8])
        vertices_str_arr = ambiente[7].replace(" ","").split("),(")
        vertices = []
        for vertice_str in vertices_str_arr:

            p1 = float(vertice_str.split(",")[0].replace("(",""))
            p2 = float(vertice_str.split(",")[1].replace(")",""))
            tupla = (p1,p2)
            vertices.append(tupla)
        
        buracos = []
        if(ambiente[13] != "NA" and ambiente[13] != "[]"):
            buracos_str_arr = ambiente[13].replace(" ","").split("],[")
            for buraco_str in buracos_str_arr:
                buraco_str = buraco_str.replace("[","").replace("]","").replace("[","")
                buraco_vertices = []
                buraco_vertices_str_arr = buraco_str.split("),(")
                for buraco_vertice_str in buraco_vertices_str_arr:
                
                    p1 = float(buraco_vertice_str.split(",")[0].replace("(",""))
                    p2 = float(buraco_vertice_str.split(",")[1].replace(")",""))

                    tupla = (p1,p2)
                    buraco_vertices.append(tupla)
                buracos.append(buraco_vertices)
        tabela_ambientes_andar[andar].append([ambiente_nome,0,0,0,0,vertices,buracos])
    
    andar_count = 0
    for tabela_ambientes_i in tabela_ambientes_andar:
        paredes_novas = GeradorParedes.Iniciar(tabela_ambientes_i,andar_count) # encontra todas as paredes e ambientes que pertencem
        
        nova_tabela_paredes.extend(paredes_novas)
        andar_count+=1


    #cria uma tabela de shapely stringline das bordas dos poligonos afim de verificar de onde pertence cada janela ou porta
    #usar método de contain do shapely?
    i_parede = 0
    for parede in nova_tabela_paredes: # varre cada parede
        lado = parede[1]
        nome_ambiente = parede[0]
        andar_parede = parede[2]
        line = shapely.LineString(lado)
        angulo_norte = parede[3]
        i_elemento = 0
        for elemento in tabela_janelas_portas_andar[andar_parede]: #verifica cada janela e porta do andar
            centro_x = float(elemento[1])
            centro_y = float(elemento[2])          
            ponto_shapely = shapely.Point(centro_x, centro_y)
            distancia = ponto_shapely.distance(line)
            if(distancia<0.03):
                area = elemento[9]
                tabela_janelas_portas_andar[andar_parede][i_elemento][10]= nome_ambiente 
                tabela_janelas_portas_andar[andar_parede][i_elemento][13]= angulo_norte 
                nova_tabela_paredes[i_parede].append(area)
            i_elemento+=1
        i_parede +=1

    #limpa a tabela de janelas/portas antes de usar
    row = 0
    while Q_tabela_janelas_portas.rowCount()>0:
        Q_tabela_janelas_portas.removeRow(row)


    #recria a Q Tabela de janelas/portas com os dados da matriz de dados
    i_andar = 0
    while(i_andar<len(tabela_janelas_portas_andar)):
        #de:
        #[x_centro, y_centro, SHGC, largura, altura, tipo, angulo_rad, interface, area]
        #para:
# header_colunas = ["andar", "x1","y1","x2","y2", "SHGC", "largura", "altura", "tipo", 9 "angulo_rad", 10 "interface", 11 "material", 12 "area",13  "angulo_Norte", "angulo_horizontal", 
# 15 "interno/ext", 16 "U", 17 "espessura", 18 "k"]
        for elemento in tabela_janelas_portas_andar[i_andar]:
            
            x_centro = elemento[1]
            y_centro = elemento[2]
            SHGC = elemento[5]
            largura = elemento[6]
            altura = elemento[7]
            tipo = elemento[8]
            angulo_rad = elemento[9]
            interface = elemento[10]
            area = elemento[12]
            angulo_norte = elemento[13]
            angulo_horizontal = 90
            U = elemento[16]
            espessura = elemento[17]
            k = elemento[18]
            rowPosition = Q_tabela_janelas_portas.rowCount()
            Q_tabela_janelas_portas.insertRow(rowPosition)
            Q_tabela_janelas_portas.setItem(rowPosition, 0, QtWidgets.QTableWidgetItem(str(i_andar))) 
            Q_tabela_janelas_portas.setItem(rowPosition, 1, QtWidgets.QTableWidgetItem(str(x_centro))) 
            Q_tabela_janelas_portas.setItem(rowPosition, 2, QtWidgets.QTableWidgetItem(str(y_centro))) 
            Q_tabela_janelas_portas.setItem(rowPosition, 3, QtWidgets.QTableWidgetItem(str(x_centro))) 
            Q_tabela_janelas_portas.setItem(rowPosition, 4, QtWidgets.QTableWidgetItem(str(y_centro))) 
            Q_tabela_janelas_portas.setItem(rowPosition, 5, QtWidgets.QTableWidgetItem(str(SHGC))) 
            Q_tabela_janelas_portas.setItem(rowPosition, 6, QtWidgets.QTableWidgetItem(str(largura)))
            Q_tabela_janelas_portas.setItem(rowPosition, 7, QtWidgets.QTableWidgetItem(str(altura)))        
            Q_tabela_janelas_portas.setItem(rowPosition, 8, QtWidgets.QTableWidgetItem(str(tipo)))     
            Q_tabela_janelas_portas.setItem(rowPosition, 9, QtWidgets.QTableWidgetItem(str(angulo_rad)))
            Q_tabela_janelas_portas.setItem(rowPosition, 10, QtWidgets.QTableWidgetItem(str(interface)))
            Q_tabela_janelas_portas.setItem(rowPosition, 11, QtWidgets.QTableWidgetItem(str("N/A")))
            Q_tabela_janelas_portas.setItem(rowPosition, 12, QtWidgets.QTableWidgetItem(str(area)))
            Q_tabela_janelas_portas.setItem(rowPosition, 13, QtWidgets.QTableWidgetItem(str(angulo_norte)))
            Q_tabela_janelas_portas.setItem(rowPosition, 14, QtWidgets.QTableWidgetItem(str(angulo_horizontal)))
   
            if(len(interface.split(";")) >1):
                Q_tabela_janelas_portas.setItem(rowPosition, 15, QtWidgets.QTableWidgetItem("interna"))
            else:
                Q_tabela_janelas_portas.setItem(rowPosition, 15, QtWidgets.QTableWidgetItem("externa"))
            
            Q_tabela_janelas_portas.setItem(rowPosition, 16, QtWidgets.QTableWidgetItem(str(U)))
            Q_tabela_janelas_portas.setItem(rowPosition, 17, QtWidgets.QTableWidgetItem(str(espessura)))
            Q_tabela_janelas_portas.setItem(rowPosition, 18, QtWidgets.QTableWidgetItem(str(k)))



        i_andar+=1


    #limpa a tabela de paredes antes de usar
    row = 0
    while Q_tabela_paredes.rowCount()>0:
        Q_tabela_paredes.removeRow(row)
    tabela_janelas_portas_arr = eventosTabela.ConteudosTabela_ARR(Q_tabela_janelas_portas)
    #recria a Q Tabela de paredes com os dados da matriz de dados
    for parede in nova_tabela_paredes:
        ambientes = parede[0]
        vertices_str = str(parede[1]).replace("[","").replace("]","")
        vertices = [tuple(map(float, v.strip('()').split(','))) for v in vertices_str.split('), (')]
        linha = LineString(vertices)

        andar = parede[2]
        angulo = parede[3]
        area_subtrair = 0

        for item in tabela_janelas_portas_arr:
            x = float(item[1])
            y = float(item[2])
            ponto = Point(x, y)
            pertence = linha.contains(ponto) or linha.intersects(ponto)
            if(pertence == True):
                area_subtrair+=float(item[12])

        area = geometria.AreaParede(vertices_str, pé_direito) - area_subtrair
        Q_tabela_paredes = eventosTabela.CriarParede(Q_tabela_paredes, vertices_str, ambientes, andar, area, angulo, dicionario_paredes, andar_terreo)



    #LIMITES HORIZONTAIS
    #limpa a tabela antes de usar
    row = 0
    while Q_interfaces_horizontais.rowCount()>0:
        Q_interfaces_horizontais.removeRow(row)
    limites_horizontais = {}
    intefaces_usadas = []

    i = 0
    for linha in tabela_ambientes:
        buracos = linha[13]
        exterior = limites_horizontais_gerenciamento.Pares_Coordenadas(linha[7])
        if(linha[13] != None and linha[13] != "NA" and linha[13] != "[]"):
            interior_buracos = limites_horizontais_gerenciamento.Pares_CoordenadasInternas(linha[13])
            poligon = shapely.Polygon(exterior, interior_buracos )
        else:
            poligon = shapely.Polygon(exterior )
        tabela_ambientes[i][7] = poligon
        i+=1

    interfaces_cridas_shapely = []

    #encontra as coordenadas das intercessões entre intefaces horizontais
    for linha1 in tabela_ambientes:
        for linha2 in tabela_ambientes:
            ambiente1 = linha1[0]
            ambiente2 = linha2[0]
            poligon1 = linha1[7]
            poligon2 = linha2[7]
            andar1 = int(linha1[8])
            andar2 = int(linha2[8])
            interface = ambiente1 + "<->" + ambiente2
            if(ambiente1 != ambiente2 and abs(andar1-andar2) == 1 and (ambiente1+ambiente2) not in intefaces_usadas):
                planos_interface = []  #tem as coordendas dos planos usados nesta interface
                intercessão = limites_horizontais_gerenciamento.encontrar_intersecao(poligon1,poligon2)
                planos_interface.append(intercessão)
                
                interface_andar = str(andar1) + "<->" + str(andar2)
                intefaces_usadas.append(ambiente1+ambiente2)

                classe =""
                andar_pertecente = ""
                ambiente_contato_direto = None
                if(andar1<andar2):
                    classe = "teto"
                    andar_pertecente = andar1
                    ambiente_contato_direto = ambiente1
                else:
                    classe = "piso"
                    andar_pertecente = andar2
                    ambiente_contato_direto = ambiente2
                coordenadas=[]
                buraco = []
                if(isinstance(intercessão, LineString) == False):
                    try:
                        for interior in intercessão.interiors:
                            buraco.append(interior.coords[:])
                        coordenadas = [list(intercessão.exterior.coords),buraco]
                    except: 
                        coordenadas = [list(intercessão.exterior.coords),  []]
                    if(coordenadas[0]!= []):
                        Q_interfaces_horizontais = eventosTabela.CriarInterfaceHorizontal(Q_interfaces_horizontais, interface, classe, coordenadas, "N", interface_andar, intercessão, ambiente_contato_direto, dicionario_paredes, andar_pertecente)
                        interfaces_cridas_shapely.append(intercessão)

    tabela_interfaces_usadas = eventosTabela.ConteudosTabela_ARR(Q_interfaces_horizontais)
    intefaces_usadas_piso = []
    intefaces_usadas_teto = []
    #encontra as coordenadas das intefaces RESTANTES
    for linha1 in tabela_ambientes:
        ambiente1 = linha1[0]
        poligonos1 = linha1[7]
        planos_restantes_teto = poligonos1
        planos_restantes_piso = poligonos1
        andar1 = int(linha1[8])
        for linha2 in tabela_ambientes:
            ambiente2 = linha2[0]
            poligonos2 = linha2[7]
            planos_subtrair = poligonos2
            andar2 = int(linha2[8])
            interface = ambiente1 + "<->" + ambiente2
            if(ambiente1 != ambiente2 and andar1-andar2 == -1 and (ambiente1+ambiente2 not in intefaces_usadas_teto)): 
                planos_restantes_teto = limites_horizontais_gerenciamento.interfaces_externas(planos_restantes_teto, planos_subtrair)
                intefaces_usadas_teto.append(ambiente1+ambiente2)

    
            if(ambiente1 != ambiente2 and andar1-andar2 ==  1 and (ambiente2+ambiente1 not in intefaces_usadas_piso)): 
                planos_restantes_piso = limites_horizontais_gerenciamento.interfaces_externas(planos_restantes_piso, planos_subtrair)
                intefaces_usadas_piso.append(ambiente2+ambiente1)


        if isinstance(planos_restantes_teto, shapely.MultiPolygon):
            # Iterar sobre cada polígono dentro da MultiPolygon

            for i, poly in enumerate(planos_restantes_teto.geoms):
                interface_andar = str(andar1) + "<->" + "Exterior"
                interface  = str(ambiente1) + "<->" + "Exterior"
                ambiente_contato_direto = ambiente1
                coordenadas = []
                buraco = []
                try:
                    for interior in poly.interiors:
                        buraco.append(interior.coords[:])
                    coordenadas = [list(poly.exterior.coords),buraco]
                except: 
                    coordenadas = [list(poly.exterior.coords),  []]
                if(coordenadas[0]!= []):
                    Q_interfaces_horizontais = eventosTabela.CriarInterfaceHorizontal(Q_interfaces_horizontais, interface, "teto", coordenadas, "N", interface_andar, poly, ambiente_contato_direto, dicionario_paredes, andar1)
                    interfaces_cridas_shapely.append(poly)
        else:

            interface_andar = str(andar1) + "<->" + "Exterior"
            interface  = str(ambiente1) + "<->" + "Exterior"
            ambiente_contato_direto = ambiente1
            coordenadas = []
            buraco = []
            try:
                for interior in planos_restantes_teto.interiors:
                    buraco.append(interior.coords[:])
                coordenadas = [list(planos_restantes_teto.exterior.coords),buraco]
            except: 
                coordenadas = [list(planos_restantes_teto.exterior.coords), []]
            if(coordenadas[0]!= []):
                Q_interfaces_horizontais = eventosTabela.CriarInterfaceHorizontal(Q_interfaces_horizontais, interface, "teto", coordenadas, "N", interface_andar, planos_restantes_teto, ambiente_contato_direto, dicionario_paredes, andar1)
                interfaces_cridas_shapely.append(planos_restantes_teto)

        if isinstance(planos_restantes_piso, shapely.MultiPolygon):
            # Iterar sobre cada polígono dentro da MultiPolygon
            for i, poly in enumerate(planos_restantes_piso.geoms):
                interface_andar = "Exterior"  + "<->" +  str(andar1) 
                interface = "Exterior"  + "<->" +  str(ambiente1)
                ambiente_contato_direto = ambiente1 
                coordenadas = []
                buraco = []
                try:
                    for interior in poly.interiors:
                        buraco.append(interior.coords[:])
                    coordenadas = [list(poly.exterior.coords),buraco]
                except: 
                    coordenadas = [list(poly.exterior.coords), []]
                if(coordenadas[0]!= []):
                    Q_interfaces_horizontais = eventosTabela.CriarInterfaceHorizontal(Q_interfaces_horizontais, interface, "piso", coordenadas, "N", interface_andar, poly, ambiente_contato_direto, dicionario_paredes, andar1)
                    interfaces_cridas_shapely.append(poly)

        else:
            interface_andar = "Exterior"  + "<->" +  str(andar1) 
            interface = "Exterior"  + "<->" +  str(ambiente1) 
            ambiente_contato_direto = ambiente1
            coordenadas = []
            buraco = []
            try:
                for interior in planos_restantes_piso.interiors:
                    buraco.append(interior.coords[:])
                coordenadas = [list(planos_restantes_piso.exterior.coords),buraco]
            except: 
                coordenadas = [list(planos_restantes_piso.exterior.coords),  []]
            if(coordenadas[0]!= []):
                Q_interfaces_horizontais = eventosTabela.CriarInterfaceHorizontal(Q_interfaces_horizontais, interface, "piso", coordenadas, "N", interface_andar, planos_restantes_piso, ambiente_contato_direto,dicionario_paredes, andar1)
                interfaces_cridas_shapely.append(planos_restantes_piso)
    interfaces_horizontais_arr = eventosTabela.ConteudosTabela_ARR(Q_interfaces_horizontais)

    #limpa a tabela antes de usar
    row = 0
    while Q_interfaces_horizontais.rowCount()>0:
        Q_interfaces_horizontais.removeRow(row)
        
    interfaces_horizontais_arr_nova =[]
    i1=0
    for linha1 in interfaces_horizontais_arr:
        if(linha1!= "Usado"):
            continuar_ = True
            interface1 = linha1[1]
            classe1 = linha1[2]
            vertices1 = linha1[3] 
            cond_contorno1 = linha[4]
            interface_andar1 = linha1[5]
            area1 = linha1[6]
            buraco1 = linha1[7]
            ambiente_contato_direto1 = linha1[8]
            cor1 = linha1[9]
            coordenadas1 = interfaces_cridas_shapely[i1]
            i2=0
            andar1=linha1[10]
            exterior1_bool = "Exterior" in interface_andar1.split("<->")[0]
            for linha2 in interfaces_horizontais_arr:
                if(linha2!="Usado" and linha1!= "Usado" and continuar_ == True):
                    interface2 = linha2[1]
                    classe2 = linha2[2]
                    vertices2 = linha2[3] 
                    buraco2 = linha2[7]
                    interface_andar2 = linha2[5]
                    coordenadas2 = interfaces_cridas_shapely[i2]
                    ambiente_contato_direto2 = linha2[8]
                    andar2 =linha2[10]
                    exterior2_bool = "Exterior" in interface_andar2.split("<->")[0]
                    if(Superficies_identicas(coordenadas1, coordenadas2) == True):
                       print("\n")
                       print(classe1)
                       print(interface_andar1)
                       print(ambiente_contato_direto1)
                       print(classe2)
                       print(interface_andar2)
                       print(ambiente_contato_direto2)
                       None
                       
                    if(Superficies_identicas(coordenadas1, coordenadas2) == True and classe1!= classe2 and ((interface_andar1.split("<->")[0] == interface_andar2.split("<->")[1] and interface_andar1.split("<->")[1] == interface_andar2.split("<->")[0])) and ambiente_contato_direto1 == ambiente_contato_direto2 and exterior1_bool == False and exterior2_bool == False):
                        classe = "conjunto"
                        cond_contorno1 = "adibatica"
                        Q_interfaces_horizontais = eventosTabela.CriarInterfaceHorizontal_tipoB(Q_interfaces_horizontais, interface1, classe, vertices1, cond_contorno1, interface_andar1, area1, buraco1, cor1)
                        interfaces_horizontais_arr[i1] = "Usado"
                        interfaces_horizontais_arr[i2] = "Usado"
                        continuar_ = False
                i2+=1
        i1+=1
    i1 = 0
    andar_terreo = int(andar_terreo)
    for linha1 in interfaces_horizontais_arr:
        if(linha1!= "Usado"):
            interface1 = linha1[1]
            classe1 = linha1[2]
            vertices1 = linha1[3] 
            cond_contorno1 = linha[4]
            interface_andar1 = linha1[5]
            area1 = linha1[6]
            buraco1 = linha1[7]
            cor1 = linha1[9]
            coordenadas1 = interfaces_cridas_shapely[i1]
            i1+=1
            andar_piso = None
            if (classe1 == "piso"):
                andar_piso = int(interface_andar1.split("<->")[1])
                if(andar_piso<=andar_terreo):
                    cond_contorno1 = "contato c/solo"
                elif(andar_piso>andar_terreo):
                    cond_contorno1 = "atmosfera s/sol"
            if (classe1 == "teto"):   
                andar_teto = int(interface_andar1.split("<->")[0])
                if(andar_teto>=andar_terreo ):
                    cond_contorno1 = "atmosfera"
                elif(andar_teto<andar_terreo):
                    cond_contorno1 = "contato c/solo"
            Q_interfaces_horizontais = eventosTabela.CriarInterfaceHorizontal_tipoB(Q_interfaces_horizontais, interface1, classe1, vertices1, cond_contorno1, interface_andar1, area1, buraco1, cor1)


    return Q_tabela_paredes, Q_interfaces_horizontais, Q_tabela_janelas_portas


def Superficies_identicas(superficie1, superficie2):
    diferença1 = superficie1.difference(superficie2)
    diferença2 = superficie2.difference(superficie1)
    try:

        if (list(diferença1.exterior.coords) == list(diferença2.exterior.coords)):
            return True
    except:
        print(str(superficie1))
        print(str(superficie2))
        None
    return False
 


def CoordenadasString_para_Vertices(string, escala):
    vertices_ambiente_str = string.replace(" ","")
    # Dividir a string em sub-strings
    vertices_arr_str = vertices_ambiente_str.split("),(")
    vertices_ambiente = []
    for tuplas_str in vertices_arr_str:
        x = int(float(tuplas_str.split(",")[0].replace("(", "")) * escala)
        y = int(float(tuplas_str.split(",")[1].replace(")", "")) * escala)
        vertices_ambiente.append((x,y))

    return vertices_ambiente

def EncontrarParedes(tabela_paredes, escala):
    
    nova_tabela_paredes = []
    pares_paredes_1 = []
    
    for parede1 in tabela_paredes:
        segmentos = []
        ambiente_parede1 = parede1[0] 
        vertices_parede1_str = parede1[3]
        vertices_parede1 = CoordenadasString_para_Vertices(vertices_parede1_str, escala)
        reta1 = LineString(vertices_parede1) #começa como uma reta e vai sendo reduzindo em uma ou varias retas menores
        retas1 = [reta1]
        
        for parede2 in tabela_paredes:
        # Definindo as linhas
            ambiente_parede2 = parede2[0] 
            vertices_parede2_str = parede2[3]
            vertices_parede2 = CoordenadasString_para_Vertices(vertices_parede2_str, escala)
            reta2 = LineString(vertices_parede2)
            # Verificando se a reta2 está contida na reta1
            if reta2.within(reta1) and ambiente_parede1!= ambiente_parede2:
                # Encontrando a interseção entre as duas linhas
                intersecao = reta1.intersection(reta2)
                
                
                # Separando a interseção em segmentos
                if isinstance(intersecao, LineString):
                    # Uma única linha foi formada
                    segmentos.append(intersecao)
                    
                    parede_nova = [ambiente_parede1+";"+ambiente_parede2, 0, 0, list(intersecao.coords)]
                    nova_tabela_paredes.append(parede_nova) 
                else:
                    # Duas linhas foram formadas
                    segmentos.append(intersecao[0]) 
                    segmentos.append(intersecao[1])
                    parede_nova1 = [ambiente_parede1+";"+ambiente_parede2, 0, 0, list(intersecao[0].coords)]
                    nova_tabela_paredes.append(parede_nova1) 
                    parede_nova2 = [ambiente_parede1+";"+ambiente_parede2, 0, 0, list(intersecao[1].coords)]
                    nova_tabela_paredes.append(parede_nova2) 
                
                _segmentos = segmentos.copy()
                #pega as porções restantes
                for segmento in _segmentos:
                    segmentos_restantes = reta1.difference(segmento)
                    if isinstance(segmentos_restantes, LineString):
                        segmentos.append(segmentos_restantes)
                        parede_nova = [ambiente_parede1+";"+ambiente_parede2, 0, 0, list(segmentos_restantes.coords)]
                        nova_tabela_paredes.append(parede_nova) 
                    else:
                        segmentos.append(segmentos_restantes.geoms[0])
                        segmentos.append(segmentos_restantes.geoms[1])
                        parede_nova1 = [ambiente_parede1+";"+ambiente_parede2, 0, 0, list(segmentos[0].coords)]
                        nova_tabela_paredes.append(parede_nova1) 
                        parede_nova2 = [ambiente_parede1+";"+ambiente_parede2, 0, 0, list(segmentos[1].coords)]
                        nova_tabela_paredes.append(parede_nova2)                         

            else:
                # As retas não se interceptam
                print("As retas não se interceptam.")

        segmentos_finais = [reta1]
        
        continuar = True
        for segmento_final in segmentos:
            for segmento in segmentos:
                    resultado = segmento_final.difference(segmento)
                    print(str(segmento_final) + "=" + str(segmento_final) + " - " + str(segmento))
                    if isinstance(resultado, LineString) and resultado not in segmentos:
                        segmentos_finais.append(resultado)
                       
                    elif resultado not in segmentos:
                        segmentos_finais.append(resultado.geoms[0])
                        segmentos_finais.append(resultado.geoms[1])
                        
                    if(resultado == segmento_final):
                        parede_nova2 = [ambiente_parede1, 0, 0, list(resultado.coords)]
                        nova_tabela_paredes.append(parede_nova2) 

    # Imprimindo os segmentos
    print(f"Segmento: {nova_tabela_paredes}")
    return nova_tabela_paredes

def EncontrarVizinhos(tabela_paredes, tabela_ambientes, escala):
    i=0
    for parede_arr in tabela_paredes:
        vertices_parede = parede_arr[3]
        andar_parede = int(parede_arr[5])
        p1_str = vertices_parede.split("),(")[0].replace("(","").replace(")","")
        p2_str = vertices_parede.split("),(")[1].replace("(","").replace(")","")
        p1 = (   int(float(p1_str.split(",")[0])) *escala,             int(float(p1_str.split(",")[1]) *escala)   )
        p2 = (   int(float(p2_str.split(",")[0])) *escala,             int(float(p2_str.split(",")[1]) *escala)   )
        print(str([p1,p2]))
        segmento_parede = geom.LineString([p1, p2])
        ambientes_vizinhos = []
        for ambiente_arr in tabela_ambientes:
            ambiente_nome = ambiente_arr[0]
            vertices_ambiente_str = ambiente_arr[7].strip()
            # Dividir a string em sub-strings
            vertices_arr_str = vertices_ambiente_str.split("),(")
            vertices_ambiente = []
            for tuplas_str in vertices_arr_str:
                x = int(float(tuplas_str.split(",")[0].replace("(", "")) * escala)
                y = int(float(tuplas_str.split(",")[1].replace(")", "")) * escala)
                vertices_ambiente.append((x,y))
            andar_ambiente = int(ambiente_arr[8])
            if(andar_parede == andar_ambiente):
                poligono = geom.Polygon(vertices_ambiente)
                if segmento_parede.touches(poligono):
                    ambientes_vizinhos.append(ambiente_nome)
        tabela_paredes[i][1] = ambientes_vizinhos
        i+=1
    return tabela_paredes
        


def PlotarVertices_LimitesHorizontais(andares):
    for andar in andares:
        for dicionario_key, tuplas in andar.items():
            fig, ax = plt.subplots()
            # Extrair coordenadas x e y das tuplas
            x_coords = [t[0] for t in tuplas]
            y_coords = [t[1] for t in tuplas]

            # Plotar as retas
            plt.plot(x_coords, y_coords, marker='o')
            plt.title(dicionario_key)
            # Configurar rótulos dos eixos
            plt.xlabel('Coordenada X')
            plt.ylabel('Coordenada Y')



            # Exibir o gráfico
            plt.grid(True)
            plt.show()

# encontra as coordenadas das bordas dos limites horizontais
def BordasLimitesHorizontais(pontos_interfaces_horizontais):

    bordas_ordenadas = []
    andar_count=0
    #iterando andar
    for dicionario in pontos_interfaces_horizontais:
        novo_dicionario_interfaces = {}
        #iterandoo interfaces
        for chave, valores in dicionario.items(): #chave e valor são atrelados a uma interface unica de ambiente com ambiente
            # Criando matriz local
            x_max = max(coordenada[0] for coordenada in valores)
            y_max = max(coordenada[1] for coordenada in valores)
            matriz_local = [[0 for _ in range(y_max)] for _ in range(x_max)]
            for tupla in valores:
                x, y = tupla
                try:
                    matriz_local[x][y] = 1
                except:
                    None

            matriz_np = np.array(matriz_local)
            bordas = encontrar_bordas(matriz_np)

            bordas = ordenar_bordas(bordas, matriz_local)
            plot_bordas_ambiente(bordas)
            novo_dicionario_interfaces[chave] = bordas

        bordas_ordenadas.append(novo_dicionario_interfaces)
        andar_count+=1    

    bordas_vertices = []

    for andar in bordas_ordenadas:
        interfaces_andar = {}
        for interface_key, interface_value in andar.items():
            ponto_anterior = interface_value[0]
            direção_anterior = (0,0)
            primeiro_ponto = interface_value[0]
            interface_vertices = []
            for ponto in interface_value:
                direção_atual = (ponto[0]-ponto_anterior[0], ponto[1]-ponto_anterior[1])
                if(direção_atual==direção_anterior):
                    None
                else:
                    vertice1 = primeiro_ponto
                    vertice2 = ponto
                    deltax = vertice2[0] - vertice1[0]
                    deltay = vertice2[1] - vertice1[1]
                    distancia = math.sqrt(math.pow(deltax,2) + math.pow(deltay,2))
                    if(vertice1!=vertice2 and distancia >5):
                        reta = (vertice1,vertice2)
                        interface_vertices.append(reta)
                        primeiro_ponto = ponto
                direção_anterior = direção_atual
                ponto_anterior = ponto
            interfaces_andar[interface_key] = interface_vertices
        bordas_vertices.append(interfaces_andar)
                
    return bordas_ordenadas
                


def plot_bordas_ambiente(bordas):
    # ... (seu código para encontrar as bordas)

    # Extrair as coordenadas x e y das bordas
    bordas_x = [coordenada[0] for coordenada in bordas]
    bordas_y = [coordenada[1] for coordenada in bordas]

    # Plotar a matriz (opcional)
    # plt.imshow(matriz, cmap="binary")  # cmap define a cor (preto e branco)

    # Plotar as bordas
    plt.plot(bordas_x, bordas_y, marker='o', color='red', linestyle='-', linewidth=2)  # Ajustes para visualização


    # Configurar e exibir o plot
    plt.xlabel("X")
    plt.ylabel("Y")
    plt.title("Bordas da Superfície")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

def é_borda(i, j, matriz):

    try:
        vizinhos = [
            matriz[i - 1] [j], matriz[i + 1][j], matriz[i][j - 1], matriz[i] [j + 1]
        ]
        if (0 in vizinhos and matriz[i,j] == 1):
            return True
    except:
        if(matriz[i,j] == 1):
            return True
  
    return False

def ordenar_bordas(bordas, matriz):
    inicio = time.time()

    bordas_ordenadas = []
    coordenada_atual = bordas[0]
    bordas_ordenadas.append(coordenada_atual)
    i=0
    coordenada_atual  = bordas[0]
    while(len(bordas_ordenadas)!= len(bordas)):
        
        x1 = coordenada_atual[0]
        y1 = coordenada_atual[1]
        proximo_ponto = (x1,y1)
        menor_distancia = 10000000
        for coordenada in bordas:
            if(coordenada not in bordas_ordenadas):
                x2 = coordenada[0]
                y2 = coordenada[1]
                delta_x = x2-x1
                delta_y = y2-y1
                #distancia = math.sqrt(math.pow(delta_x,2) + math.pow(delta_y,2))
                if(delta_x<=1 and delta_y<=1 ):
                    proximo_ponto = (x2,y2)
                    
        bordas_ordenadas.append(proximo_ponto)
        coordenada_atual = proximo_ponto

    fim = time.time()

    tempo_execucao = fim - inicio
    print(f"Tempo de execução: {tempo_execucao} segundos")

    return bordas_ordenadas

def encontrar_bordas(matriz):
  """
  Encontra todas as coordenadas de borda na matriz.

  Args:
      matriz (numpy.ndarray): Matriz da superfície.

  Returns:
      list: Lista de tuplas com as coordenadas de borda.
  """
  bordas = []
  for i in range(matriz.shape[0]):
    for j in range(matriz.shape[1]):
      if é_borda(i, j, matriz):
        bordas.append((i, j))
  return bordas

def RemoverInterfacesDesnecessárias(dados):
    novo_dados = []
    i = 0
    for dicionario in dados:
        novo_dados.append({})
        for chave, valores in dicionario.items():
            ambientes_internos_cout = 2
            ambientes = chave.split(",")
            for ambiente in range(len(ambientes)):
                if("limite minimo" in ambientes[ambiente]):
                    ambientes_internos_cout-=1
                if("NaoDefinido" in ambientes[ambiente]):
                    ambientes_internos_cout-=1
                if("limite maximo" in ambientes[ambiente]):
                    ambientes_internos_cout-=1
            if(ambientes_internos_cout >0):
                novo_dados[i][chave] = valores
        i+=1

    return novo_dados


def PlotarLimitesHorizontais(dados):

    andar_count=0
    for dicionario in dados:
        fig, ax = plt.subplots()
        plt.xlabel("Eixo X")
        plt.ylabel("Eixo Y")
        plt.grid(True)
        plt.legend()
        plt.title("Pontos Internos e da interface: " + str(andar_count), fontweight="bold", fontsize=14, color="black")
        for chave, valores in dicionario.items():
            # Criando listas de x, y e cores
            lista_x = []
            lista_y = []
            lista_cores = []

            r = np.round(np.random.rand(),1)
            g = np.round(np.random.rand(),1)
            b = np.round(np.random.rand(),1)
            cor = [r,g,b]
            for tupla in valores:
                x, y = tupla
                lista_x.append(x)
                lista_y.append(y)

                lista_cores.append(cor)
            # Convertendo as listas para arrays NumPy
            x = np.array(lista_x)
            y = np.array(lista_y)
            cores = np.array(lista_cores)
            plt.scatter(x, y, c=cores)
        plt.show()
        andar_count+=1


def RemoveParedeRepetida(tabela,andares_total):
    paredes_usadas = []
    i=0
    while (i<=andares_total): 
        paredes_usadas.append ([])
        i+=1
    tabela_nova = []
    for linha in tabela:
        vertices = linha[3].split("),(")
        andar = int(linha[5])
        p1 = vertices[0].replace(")", "").replace("(","")
        p2 = vertices[1].replace(")", "").replace("(","")
        parede = (p1,p2)
        if(parede not in paredes_usadas[andar] and p1!=p2):
            tabela_nova.append(linha)
        paredes_usadas[andar].append((p1,p2))
        paredes_usadas[andar].append((p2,p1))

    return tabela_nova



def AmbientesVizinhos(matriz, _x, _y):
    x = int(_x)
    y = int(_y)
    try:
        NO,N,NE = matriz[x-1][y+1],matriz[x][y+1],matriz[x+1][y+1]
        O, E = matriz[x-1][y], matriz[x+1][y]
        SO,S,SE = matriz[x-1][y-1],matriz[x][y-1],matriz[x+1][y-1]
        ambientes = []
        if(NO.Tipo() == "interno"):
            ambientes.append(NO.Ambiente())
        if(N.Tipo() == "interno"):
            ambientes.append(N.Ambiente())
        if(NE.Tipo() == "interno"):
            ambientes.append(NE.Ambiente())
        if(O.Tipo() == "interno"):
            ambientes.append(O.Ambiente())
        if(E.Tipo() == "interno"):
            ambientes.append(E.Ambiente())
        if(SO.Tipo() == "interno"):
            ambientes.append(SO.Ambiente())
        if(S.Tipo() == "interno"):
            ambientes.append(S.Ambiente())
        if(SE.Tipo() == "interno"):
            ambientes.append(SE.Ambiente())
    except:
        print("erro vizinhos")

    ambientes = list(set(ambientes))

    return ambientes


#matriz [x][y]
def CriarMatriz2D(resolucao, valor_min_x, valor_max_x ,  valor_min_y,  valor_max_y):
    # Criando uma lista vazia
    matriz = []
    m = int((valor_max_x - valor_min_x)/resolucao +1)
    n = int((valor_max_y - valor_min_y)/resolucao +1)
    # Adicionando linhas à matriz
    for i in range(m):
        linha = []
        for j in range(n):
            # Adicionando elementos à linha
            x=int((i+valor_min_x)*resolucao)
            y=int((j+valor_min_y)*resolucao)
            ponto = Ponto(x,y,"NaoDefinido","NaoDefinido")
            linha.append(ponto)
        # Adicionando a linha à matriz
        matriz.append(linha)
    
    print("tamanho da matriz é de " + str(m) + " x " + str(n))
    return matriz

def AutoCriação_Paredes(Q_tabela_paredes: QtWidgets.QTableWidget):
    tabela_paredes = eventosTabela.ConteudosTabela_ARR(Q_tabela_paredes)
            
    header_colunas = ["Indice", "Ambiente", "Classe", "Vértices"]

    
    nova_tabela_paredes = []
    paredes_analisados = [] #evita que se analize a mesmma parede mais de uma vez
    cout_linha1 = 0
    for parede_row1 in tabela_paredes: 
        linha_1 = literal_eval(parede_row1[3])
        ambiente_1 = parede_row1[1]
        cout_linha2 = 0
        for _parede_row2 in tabela_paredes:
            parede_row2 = _parede_row2.split(";")
            ambiente_2 = parede_row2[1]
            linha_2 = literal_eval(parede_row2[3])
            segmentos, ambientes, colinear = geometria.separar_em_subparedes(linha_1, linha_2, ambiente_1, ambiente_2, resolução)
            if(colinear == True):
                i = 0
                
                for segmento in segmentos:
                    ambiente_novo = ambientes[i]

                    linha_nova =  ["", ambiente_novo, parede_row1[2], str(segmento)]
                    nova_tabela_paredes.append(linha_nova)
                    paredes_analisados.append(((linha_1,linha_2),(linha_2,linha_1)))



                i+=1
            

            #caso não seja achado nada em comum entre duas paredes
            else:
                nova_tabela_paredes.append(parede_row1)
                nova_tabela_paredes.append(parede_row2)


            cout_linha2 +=1
        cout_linha1 +=1
    
    for item in nova_tabela_paredes:
        print(item)




    tabela_paredes_limpa = []

    paredes_analisadas = []
    i=0
    #remove duplicadas:
    for linha in nova_tabela_paredes:
        parede = literal_eval(linha[3])           
        parede_str = str(parede[0])+"," + str(parede[1])
        parede_str = parede_str.replace(" ", "")
        #caso não exista a parede na lista ela é adicionada normalmente
        if( parede_str not in paredes_analisadas ):
            _linha =linha
            _linha[0] = i
            _linha[3] = _linha[3].replace(" ", "")
            tabela_paredes_limpa.append(_linha)
            i+=1
            print(i)
            parede_analisada1 = str(parede[1])+"," + str(parede[0])
            parede_analisada1 = parede_analisada1.replace(" ", "")
            parede_analisada2 = str(parede[0])+"," + str(parede[1])
            parede_analisada2 = parede_analisada2.replace(" ", "")
            paredes_analisadas.append(parede_analisada1)
            paredes_analisadas.append(parede_analisada2)
        
        #caso a parede já esteja na lista só se modifica o espaço "ambiente"
        else:
            _parede_str = str(parede[0])+"," + str(parede[1])
            _parede_str = _parede_str.replace(" ", "")
            indice = int(math.floor (paredes_analisadas.index(  _parede_str   )/2))
            
            print(tabela_paredes_limpa)
            print(paredes_analisadas)
            print("\n")
            tabela_paredes_limpa[indice][1] = tabela_paredes_limpa[indice][1] + "&" + linha[1]


    
    # plotar
    cor = {
    1: "blue",
    2: "red",
    3: "black"
    }
    pontos = []
    cores = []
    vizinhos =[]
    for linha in tabela_paredes_limpa:
        coordenadas = linha[3].replace("(","").replace(")","").replace(" ","").split(",")
        coordenadas = list(map(float, coordenadas))
        pontos.append([coordenadas[0:2], coordenadas[2:4]])
        ambientes = removeAmbientesRepetidos(linha[1]).split("&")
        num_ambientes = len(ambientes)
        vizinhos.append(num_ambientes)
    # Combinar os pontos em pares
    retas = []
    vizinhos_par = []
    for par in pontos:
        retas.append(list(zip(*par)))

    for vizinho in vizinhos:
        vizinhos_par.append(vizinho)
    # Plotar as retas
    i=0
    for reta in retas:
        plt.plot(*reta, linewidth=vizinhos_par[i], color=cor[vizinhos_par[i]])

        i+=1

    plt.xlabel("Coordenada X")
    plt.ylabel("Coordenada Y")
    plt.title("Retas do Ambiente 1")
    plt.show()


    #zera a tabela
 
    while(Q_tabela_paredes.rowCount()!=0):

        Q_tabela_paredes.removeRow(0)


    for linha in tabela_paredes_limpa:
        vertices = linha[3].replace("((", "(").replace("))",")")
        ambientes = linha[1]
        ambientes = removeAmbientesRepetidos(ambientes)
        Q_tabela_paredes = eventosTabela.CriarParede(Q_tabela_paredes, vertices, ambientes)

    print(Q_tabela_paredes.rowCount())
    return Q_tabela_paredes

def removeAmbientesRepetidos(ambiente_original):
    ambientes_arr = ambiente_original.split("&")
    ambientes_arr = list(set(ambientes_arr))
    lista_sem_vazias = []

    for item in ambientes_arr:
        if item != "":
            lista_sem_vazias.append(item)

    ambiente = "&".join(lista_sem_vazias)
    return ambiente


if __name__ == '__main__':
    reta1 = "(0, 0), (10, 0)"
    reta2 = "(4, 0), (6, 0)"
    parede1 = ["amb1",0,0,reta1]
    parede2 = ["amb2",0,0,reta2]
    tabela_paredes = [parede1,parede2]
    EncontrarParedes(tabela_paredes, 1)
 