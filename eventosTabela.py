from PyQt5 import QtWidgets, QtGui
from shapely.geometry import Polygon
from PyQt5 import QtQuick
import geometria
import matematica
import parametros
import gerenciamento_avançado_ambientes

print("Carregando módulo de gerenciamento de tabelas...")

def ConstruirTabela(tabela, keyPressEventTable, header_colunas):
    # Cria e configura a tabela para mostrar as coordenadas dos retângulos
    tabela.setColumnCount(len(header_colunas))  # Adiciona uma coluna extra para os vértices
    tabela.setHorizontalHeaderLabels(header_colunas
        )  # Cabeçalhos da tabela
    tabela.setMaximumWidth(350)  # Limita a largura da tabela a 200 pixels

    # Definindo a largura das colunas da tabela
    for i in range(tabela.columnCount()):
        tabela.setColumnWidth(i, 50)

    # Conectar evento keyPressEvent da tabela
    tabela.keyPressEvent = keyPressEventTable

    tabela.setFont(QtGui.QFont('Arial', 8))

    return tabela


def apagar_todas_linhas(tabela):

    while (tabela.rowCount()!=0):
        print(tabela.rowCount())
        tabela.removeRow(0)
        
    return tabela

def novasParedes(tabela_paredes, vertices_str, nome_ambiente, andar, pé_direito):

    # lista todas as paredes já usadas
    tabela_paredes_arr = ConteudosTabela_ARR(tabela_paredes)
    paredes_usadas = []
    for coordenadas in tabela_paredes_arr:
        _vertices_str = coordenadas[3]  
        paredes_usadas.append(_vertices_str)


    vertices_str_arr = vertices_str.replace(" ", "").split("),(")
    pontos = []
    for ponto_str in vertices_str_arr:
        ponto_str_divido = ponto_str.replace("(", "").replace(")", "").split(",")
        x_float = float(ponto_str_divido[0])
        y_float = float(ponto_str_divido[1])
        pontos.append((x_float, y_float))


    i = 0
    for ponto in pontos:
        parede = str(pontos[i-1]) + "," + str(pontos[i])
        area = geometria.AreaParede(parede, pé_direito)    
        if(parede in paredes_usadas):
            indice = paredes_usadas.index(parede)
            #tabela_paredes = AtualizarParede(indice, tabela_paredes, nome_ambiente, andar)
        else:
            #tabela_paredes = CriarParede(tabela_paredes, parede, nome_ambiente, andar,area, "desconhecido")
            None
        i+=1

    return tabela_paredes

def AtualizarParede(indice, tabela_paredes: QtWidgets.QTableWidget, nome_ambiente):


    ambientes_atuais = tabela_paredes.item(indice,1).text()
    tabela_paredes.setItem(indice, 1, QtWidgets.QTableWidgetItem(ambientes_atuais + "," + str(nome_ambiente)))

    return tabela_paredes

def CriarParede(tabela_paredes, parede, nome_ambiente, andar, area, angulo, paredes_default, andar_terreo):
    rowPosition = tabela_paredes.rowCount()
    cond_tipo_paredes_list = ["interna", "externa", "contato c/solo", "adiabatico"]
    combobox_cond_contorno = QtWidgets.QComboBox()
    combobox_cond_contorno.addItems(cond_tipo_paredes_list)
    cor_paredes_list = parametros.cores_paredes_list
    if(len(nome_ambiente.split(";"))>1):
        tipo = "paredes_internas"
        combobox_cond_contorno.setCurrentText("interna")
    if(len(nome_ambiente.split(";"))==1):
        tipo = "paredes_externas"
        if(andar>=andar_terreo):
            combobox_cond_contorno.setCurrentText("externa")  
        elif(andar<andar_terreo):
            combobox_cond_contorno.setCurrentText("contato c/solo")  
    combobox_cor = QtWidgets.QComboBox()
    combobox_cor.addItems(cor_paredes_list)
    cor = paredes_default[tipo]["cor"]
    combobox_cor.setCurrentText(cor)
    tabela_paredes.insertRow(rowPosition)
    tabela_paredes.setItem(rowPosition, 0, QtWidgets.QTableWidgetItem(str(rowPosition)))
    tabela_paredes.setItem(rowPosition, 1, QtWidgets.QTableWidgetItem(str(nome_ambiente)))
    tabela_paredes.setCellWidget(rowPosition, 2, combobox_cond_contorno)
    tabela_paredes.setItem(rowPosition, 3, QtWidgets.QTableWidgetItem(str(parede)))
    tabela_paredes.setItem(rowPosition, 4, QtWidgets.QTableWidgetItem(str("N/A")))
    tabela_paredes.setItem(rowPosition, 5, QtWidgets.QTableWidgetItem(str(andar)))
    tabela_paredes.setItem(rowPosition, 6, QtWidgets.QTableWidgetItem(str(area)))
    tabela_paredes.setItem(rowPosition, 7, QtWidgets.QTableWidgetItem(str("N/A")))
    tabela_paredes.setCellWidget(rowPosition, 8, combobox_cor)
    tabela_paredes.setItem(rowPosition, 9, QtWidgets.QTableWidgetItem(str("N/A")))
    tabela_paredes.setItem(rowPosition, 10, QtWidgets.QTableWidgetItem(str(angulo)))
    return tabela_paredes

def CriarInterfaceHorizontal(tabela_interface, interface, classe, vertices, cond_contorno, interface_andar, shapely, ambiente_contato_direto, paredes_default, andar_pertencente):
    rowPosition = tabela_interface.rowCount()
    cond_contorno_list = ["comum", "atmosfera", "atmosfera s/sol", "contato c/solo", "adibatica"]
    area = shapely.area 
    combobox_cond_contorno = QtWidgets.QComboBox()
    combobox_cond_contorno.addItems(cond_contorno_list)
    cor_list = parametros.cores_paredes_list
    combobox_cor = QtWidgets.QComboBox()
    combobox_cor.addItems(cor_list)
    cor = paredes_default["interfaces_horizontais"]["cor"]
    combobox_cor.setCurrentText(cor)
    tabela_interface.insertRow(rowPosition)
    tabela_interface.setItem(rowPosition, 0, QtWidgets.QTableWidgetItem(str(rowPosition)))
    tabela_interface.setItem(rowPosition, 1, QtWidgets.QTableWidgetItem(str(interface)))
    tabela_interface.setItem(rowPosition, 2, QtWidgets.QTableWidgetItem(str(classe)))
    tabela_interface.setItem(rowPosition, 3, QtWidgets.QTableWidgetItem(str(vertices[0])))
    tabela_interface.setCellWidget(rowPosition, 4, combobox_cond_contorno)
    tabela_interface.setItem(rowPosition, 5, QtWidgets.QTableWidgetItem(interface_andar))
    tabela_interface.setItem(rowPosition, 6, QtWidgets.QTableWidgetItem(str(area)))
    tabela_interface.setItem(rowPosition, 7, QtWidgets.QTableWidgetItem(str(vertices[1])))
    tabela_interface.setItem(rowPosition, 8, QtWidgets.QTableWidgetItem(ambiente_contato_direto))
    tabela_interface.setCellWidget(rowPosition, 9, combobox_cor)
    tabela_interface.setItem(rowPosition, 10, QtWidgets.QTableWidgetItem((andar_pertencente)))
    return tabela_interface    

def CriarInterfaceHorizontal_tipoB(tabela_interface, interface1, classe1, vertices1, cond_contorno1, interface_andar1, area1, buraco1, cor):
    rowPosition = tabela_interface.rowCount()
    cond_contorno_list = ["comum", "atmosfera", "atmosfera s/sol", "contato c/solo", "adibatica"]
    combobox_cond_contorno = QtWidgets.QComboBox()
    combobox_cond_contorno.addItems(cond_contorno_list)
    combobox_cond_contorno.setCurrentText(cond_contorno1) 


    cor_list = parametros.cores_paredes_list
    combobox_cor = QtWidgets.QComboBox()
    combobox_cor.addItems(cor_list)
    combobox_cor.setCurrentText(cor)
    tabela_interface.insertRow(rowPosition)
    tabela_interface.setItem(rowPosition, 0, QtWidgets.QTableWidgetItem(str(rowPosition)))
    tabela_interface.setItem(rowPosition, 1, QtWidgets.QTableWidgetItem(str(interface1)))
    tabela_interface.setItem(rowPosition, 2, QtWidgets.QTableWidgetItem(str(classe1)))
    tabela_interface.setItem(rowPosition, 3, QtWidgets.QTableWidgetItem(str(vertices1)))
    tabela_interface.setCellWidget(rowPosition, 4, combobox_cond_contorno)
    tabela_interface.setItem(rowPosition, 5, QtWidgets.QTableWidgetItem(interface_andar1))
    tabela_interface.setItem(rowPosition, 6, QtWidgets.QTableWidgetItem(str(area1)))
    tabela_interface.setItem(rowPosition, 7, QtWidgets.QTableWidgetItem(str(buraco1)))
    tabela_interface.setItem(rowPosition, 8, QtWidgets.QTableWidgetItem("N/A"))
    tabela_interface.setCellWidget(rowPosition, 9, combobox_cor)
    return tabela_interface    


def mudar_coordenadas_ambiente(tabela_ambientes, i, delta_x, delta_y):
    coordenadas_str = tabela_ambientes.item(i+1, 7).text()

    #'(1.4, 1.1), (2.6, 1.1), (2.6, 2.7), (1.4, 2.7)'
    coordenadas_str = coordenadas_str.replace(" ","")
    coordenadas_str_arr = coordenadas_str.split("),(")
    coordenadas_novas = []
    for tupla_str in coordenadas_str_arr:
        x = round(float(tupla_str.split(",")[0].replace("(","").replace(")","")) + delta_x , 4)
        y = round(float(tupla_str.split(",")[1].replace("(","").replace(")","")) + delta_y,  4)
        coordenadas_novas.append((x,y))
        
    coordenadas_novas_str = str(coordenadas_novas).replace("[","").replace("]","").replace(" ","")
    tabela_ambientes.setItem(i+1, 7, QtWidgets.QTableWidgetItem(coordenadas_novas_str))
    return tabela_ambientes

def _atualizar_tabela(poligono, cor, tipo, tabela_ : QtWidgets.QTableWidget,  escala, eventos_adicionais, andar, material, tabela_paredes, x_value, y_value, table_horizontal, pé_direito, indice_desejado):
    # Atualiza a tabela com as coordenadas e cores do retângulo desenhado

    tabela = tabela_


    nome_ambiente = gerar_nome_ambiente(tabela)
    rowPosition = tabela.rowCount()
    if(eventos_adicionais !="atualizar existente"):
        tabela.insertRow(rowPosition)
        item = QtWidgets.QTableWidgetItem(nome_ambiente)
        tabela.setItem(rowPosition, 0, item)

    topLeftX =  0
    topLeftY=0
    bottomRightX=0
    bottomRightY=0
    ocup_max = "N/A"
    
    if "retângulo" in tipo:
        topLeftX = poligono.topLeft().x() / escala
        topLeftY = poligono.topLeft().y() / escala
        bottomRightX = poligono.bottomRight().x() / escala
        bottomRightY = poligono.bottomRight().y() / escala
    
    if tipo == "linha":
        topLeftX = poligono.x1() / escala
        topLeftY = poligono.y1() / escala
        bottomRightX = poligono.x2() / escala
        bottomRightY = poligono.y2() / escala  

    vertices = ""
    vertices_lista = []

    if "retângulo" in tipo or tipo == "linha": 
        vertices = f"({topLeftX}, {topLeftY}), ({bottomRightX}, {topLeftY}), ({bottomRightX}, {bottomRightY}), ({topLeftX}, {bottomRightY})"
        
    if tipo == "poligono":
        vertices = ""
        for ponto in poligono:
            vertices+= "(" + str(ponto.x() / escala) + ", " + str(ponto.y() / escala) + "),"
            vertices_lista.append((ponto.x() / escala, ponto.y() / escala))
        vertices = vertices[:-1] #remove ultima vircula antes de fechar a string com o ")"
        vertices_lista.append(vertices_lista[0])
    area = matematica.Area_entrada_str(vertices)

    parametros_ventilação = parametros.parametros_refrigeração_ambientes().keys()
    combobox_tipos_ambientes = QtWidgets.QComboBox()
    combobox_tipos_ambientes.addItems(parametros_ventilação)
    if(eventos_adicionais== "atualizar existente"):
        rowPosition = indice_desejado
    tabela.setItem(rowPosition, 1, QtWidgets.QTableWidgetItem(str(topLeftX)))
    tabela.setItem(rowPosition, 2, QtWidgets.QTableWidgetItem(str(topLeftY)))
    tabela.setItem(rowPosition, 3, QtWidgets.QTableWidgetItem(str(bottomRightX)))
    tabela.setItem(rowPosition, 4, QtWidgets.QTableWidgetItem(str(bottomRightY)))
    tabela.setItem(rowPosition, 5, QtWidgets.QTableWidgetItem(str(cor.red()) + ', ' + str(cor.green()) + ', ' + str(cor.blue())))
    tabela.setItem(rowPosition, 6, QtWidgets.QTableWidgetItem(tipo))
    tabela.setItem(rowPosition, 7, QtWidgets.QTableWidgetItem(vertices))
    tabela.setItem(rowPosition, 8, QtWidgets.QTableWidgetItem(str(andar)))
    tabela.setItem(rowPosition, 9, QtWidgets.QTableWidgetItem(material))
    tabela.setItem(rowPosition, 10, QtWidgets.QTableWidgetItem(ocup_max))
    tabela.setItem(rowPosition, 11, QtWidgets.QTableWidgetItem(str(area)))
    tabela.setCellWidget(rowPosition, 12, combobox_tipos_ambientes)
    tabela.setItem(rowPosition, 13, QtWidgets.QTableWidgetItem(str("NA")))
    if(eventos_adicionais == "remover_linhas_90g_e_normais"):
        tabela = _atualizar_tabela_Remover_Retas90g_Poligono(tabela)

    if(tipo == "retângulo" or tipo == "poligono"):
        tabela_paredes = novasParedes(tabela_paredes, vertices, nome_ambiente, andar, pé_direito)

    if tipo == "poligono":
        tabela = gerenciamento_avançado_ambientes.subtrai_de_todos_poligonos(tabela, vertices_lista, andar, nome_ambiente)


    return tabela, tabela_paredes, table_horizontal, nome_ambiente





# ao criar um poligono remove as retas90g
def _atualizar_tabela_Remover_Retas90g_Poligono(tabela_):
    num_rows = tabela_.rowCount()
    row = 0
    while row < tabela_.rowCount():
        cell_value = tabela_.item(row, 6).text()
        if ("linha90g" in cell_value or "linha" in cell_value):
            tabela_.removeRow(row)
        else:
            row += 1

    return tabela_

#gera automaticamente um nome para cada ambiente novo
def gerar_nome_ambiente(tabela):
    # Gera um nome de ambiente único para cada retângulo
    nome_base = "Ambiente"
    numero_ambiente = 1
    while True:
        novo_nome = f"{nome_base} {numero_ambiente}"
        if not nome_ambiente_existe(novo_nome, tabela):
            return novo_nome
        numero_ambiente += 1

# Verifica se o nome do ambiente já existe na tabela
def nome_ambiente_existe(nome, tabela):
    for row in range(tabela.rowCount()):
        item = tabela.item(row, 0)
        if item and item.text() == nome:
            return True
    return False

def listar_ambientes(tabela):
    ambientes = {}
    andares = []
    for row in range(tabela.rowCount()):
        andar = tabela.item(row, 8).text()
        if(andar not in andares):
            andares.append(andar)
        ambiente = tabela.item(row, 0).text()
        if(andar  in ambientes.keys()):
            ambientes[andar].append(ambiente)
        else:
            ambientes[andar] = [ambiente]
    return ambientes, andares

#retorna uma array com os conteudos da tabela
def ConteudosTabela_STR(table):
    tabela_str = ""
    try:
        for row in range(table.rowCount()):
            linha = ""
            for col in range(table.columnCount()):
                item = table.item(row, col)
                if item:
                    tabela_str += f"{item.text()} " + "&"
                    linha += item.text() + ";"
                
                elif table.cellWidget(row, col):
                    combo = table.cellWidget(row, col)
                    combo_text = combo.currentText()
                    AllItems = "ITEMS/" + str([combo.itemText(i) for i in range(combo.count())]) +"/ITEMS"

                    
                    tabela_str += "COMBOITEM/" + "Escolhido/" + combo_text + "/Escolhido" + str(AllItems) + "/COMBOITEM"   + "&"
            tabela_str += "\n"
    except:
        print("Erro na leitura da tabela:\n" + str(table))
        None
    return tabela_str

def ConteudosTabela_ARR(table: QtWidgets.QTableWidget):
    tabela_arr = []
    for row in range(table.rowCount()):
        linha = []
        num_colunas = table.columnCount()
        for col in range(num_colunas):
            item = table.item(row, col)
            if item:
                linha.append(item.text())
            elif table.cellWidget(row, col):
                combo = table.cellWidget(row, col)
                combo_text = combo.currentText()
                linha.append(combo_text)
            else:
                linha.append(", ")
        tabela_arr.append(linha)
    return tabela_arr


def classificar_dados(dados, indice_coluna):
    # Função para classificar os dados (já explicada anteriormente)
    def comparar_linhas(a, b):
        return a[indice_coluna].lower() < b[indice_coluna].lower()
    return sorted(dados, key=comparar_linhas)

def ordenar_tabela_por_coluna(tabela, indice_coluna):
    # Função para ordenar a tabela (já explicada anteriormente)
    dados = ConteudosTabela_ARR(tabela)
    dados_classificados = classificar_dados(dados, indice_coluna)
    tabela = atualizar_tabela(tabela, dados_classificados)
    return tabela
def atualizar_tabela(tabela, dados_classificados):
    # Função para atualizar a tabela com os dados classificados (já explicada anteriormente)
    for i, linha in enumerate(dados_classificados):
        for j, valor in enumerate(linha):
            item = tabela.item(i, j)
            if item:
                item.setText(valor)
        
    return dados_classificados