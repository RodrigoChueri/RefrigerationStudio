from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMenuBar, QDialog
import eventosTabela
from PyQt5.QtCore import pyqtSignal
import simulacao
import threading
from threading import Thread
import progresso
from ast import literal_eval
import shutil
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QApplication, QMessageBox, QToolTip
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import Qt
import eventosTabela
from PyQt5.QtWidgets import QMenuBar, QDialog
import simulacao
from shapely.geometry import Polygon as shapelyPolygon
import matematica
import arquivo_climatico
import sys
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtGui import QTransform, QColor
import matplotlib.pyplot as plt
import random
import arredondamentos
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow
from shapely.geometry import Polygon, MultiPolygon
import eventosTabela
import contorno
import geometria
from PyQt5.QtWidgets import QMenuBar, QDialog, QMessageBox
from PyQt5.QtGui import QIcon
import tkinter as tk
from tkinter import filedialog
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QAction, QFileDialog, QWidget
import sys
from PyQt5.QtCore import Qt, QEvent
from elementos_e_materiais import ElementoEstrutural, elementos_predefinidos
import parede_gerenciamento
import simulacao
import Interfaces_Secundarias
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QTableWidget
import shapely
import numpy as np
from shapely.geometry import Polygon as shapelyPolygon
from shapely.geometry import Polygon
from shapely.ops import cascaded_union, nearest_points
import math
from PyQt5.QtGui import QPixmap
import ast
import teste_schedule
import os
import zipfile
import parametros
import qdarktheme
import json
print("Carregando interfaces secundárias...")

class TelaCargas(QDialog):
    valores_salvos = pyqtSignal(QtWidgets.QTableWidget)
    def __init__(self, table_cargas, tabela_ambientes, janela_principal, poligonos):
        # Inicializa a área de desenho
        super().__init__()
        self.setWindowTitle("Cargas Térmicas")
        #table_cargas.setSortingEnabled(True)
        #table_cargas.sortItems(0)
        self.table_cargas = table_cargas
        self.poligonos = poligonos
        #self.table_cargas.setMaximumHeight(500)
        #self.setFixedSize(900, 900)

        # Criando a ListBox
        self.listbox_andares = QtWidgets.QListWidget()
        self.listbox_andares.setMaximumHeight(200)
        # Populando a ListBox com a lista "ambientes" da janela principal
        self.ambientes, andares = eventosTabela.listar_ambientes(tabela_ambientes)
        
        self.listbox_andares.addItems(andares)

        # Conectando o sinal de clique do item da ListBox
        self.listbox_andares.itemClicked.connect(self.itemClicked)

        self.listbox_ambientes = QtWidgets.QListWidget()
        self.listbox_ambientes.setMaximumHeight(200)

        # Configurando o layout de grade
        layout = QtWidgets.QGridLayout()
        self.setLayout(layout)

        # Parte esquerda: texto "botões" e tabela para coordenadas
        upper_panel = QtWidgets.QGridLayout()
        
        layout.addLayout(upper_panel, 0, 0)
        # Adicionando a ListBox ao painel esquerdo
        upper_panel.addWidget(self.listbox_andares,0,0)
        upper_panel.addWidget(self.listbox_ambientes,0,1)

        header_colunas = ["Amb.", "Item", "Class", "Qntd.", "Andar",  "W. Dissipado", "De", "Até"]
        # Cria e configura a tabela para mostrar as coordenadas dos retângulos
        self.tabela_local = QtWidgets.QTableWidget()
        self.tabela_local = eventosTabela.ConstruirTabela(self.tabela_local, self.keyPressEventTable_Cargas, header_colunas)
        self.tabela_local.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)
        arr = eventosTabela.ConteudosTabela_ARR(self.table_cargas)
        for linha in arr:
            rowPosition = self.tabela_local.rowCount()
            self.tabela_local.insertRow(rowPosition)
            i=0
            for celula in linha:
                self.tabela_local.setItem(rowPosition, i, QtWidgets.QTableWidgetItem(celula))
                i+=1


        upper_panel.addWidget(self.tabela_local,1,0)

        # Construindo a tabela

        botao_Adicionar_Equipamento = QtWidgets.QPushButton("Adicionar Fonte de\n Calor", self)
        botao_Adicionar_Equipamento.clicked.connect(self.adicionar_equipamento)
        upper_panel.addWidget(botao_Adicionar_Equipamento,1,1)

        botao_Adicionar_ocupantes = QtWidgets.QPushButton("Adicionar Ocupantes\n e Atividades", self)
        botao_Adicionar_ocupantes.clicked.connect(self.adicionar_ocupantes)
        upper_panel.addWidget(botao_Adicionar_ocupantes,2,1)


    def keyPressEventTable_Cargas(self, event):
        # Verificar se a tecla pressionada é a tecla "Delete"
        if event.key() == QtCore.Qt.Key_Delete:
            # Obter a linha selecionada
            selected_row = self.tabela_local.currentRow()
            # Verificar se uma linha está selecionada
            if selected_row >= 0:
                # Remover a linha selecionada
                self.table_cargas.removeRow(selected_row)
                self.tabela_local.removeRow(selected_row)
                # Atualizar o desenho na área de desenho
        else:
            # Se a tecla pressionada não for "Delete", chamar o keyPressEvent original da tabela
            super().keyPressEvent(event)        

    def itemClicked(self, item):
        # Obtendo o índice do item clicado
        index = self.listbox_andares.currentIndex().row()

        # Obtendo o nome do item clicado
        self.andar = self.listbox_andares.item(index).text()
        lista_ambientes = self.ambientes[self.andar]
        self.listbox_ambientes.clear()
        self.listbox_ambientes.addItems(lista_ambientes)
        # Imprimindo o índice e o nome do item no console
        print(f"Índice: {index}, Nome: {self.andar}")




    def adicionar_equipamento(self):
        try:
            index = self.listbox_ambientes.currentIndex().row()
            ambiente = self.listbox_ambientes.item(index).text()
            self.nova_janela = TelaAdicionarEquipamento(self.table_cargas, self.tabela_local, ambiente, self.andar)
            self.nova_janela.valores_salvos.connect(self.atualizar_valores)
            self.nova_janela.show()
        except:
            print("ERRO EM -adicionar_equipamento-")

    def adicionar_ocupantes(self):
        try:
            index = self.listbox_ambientes.currentIndex().row()
            ambiente = self.listbox_ambientes.item(index).text()
            self.nova_janela = TelaAdicionarOcupantes(self.table_cargas, self.tabela_local, ambiente, self.andar)
            self.nova_janela.valores_salvos.connect(self.atualizar_valores2)
            self.nova_janela.show()
        except:
            print("ERRO EM -adicionar_ocupantes-")

    def atualizar_valores(self, table_cargas, tabela_local):
        self.table_cargas = table_cargas
        self.tabela_local = tabela_local
        tabela = eventosTabela.ConteudosTabela_ARR(self.table_cargas)

        #zera as anotações de cada ambiente
        i_andar = 0
        for andar in self.poligonos:
            i=0
            for poligono_, cor, nome_ambiente, dados_adicionais, buracos in self.poligonos[i_andar]:
                dados_adicionais["Ocupantes"] = 0
                dados_adicionais["Ocupantes_hora"] = []
                for i_ in range(25):
                    dados_adicionais["Ocupantes_hora"].append(0)
                self.poligonos[i_andar][i][3] = dados_adicionais 
                i+=1
            i_andar+=1

        for hora in range(25):


            for linha in tabela:
                ambiente = linha[0]
                classe = linha[2]
                quantidade = int(linha[3])
                inicio = int(linha[6])
                fim = int(linha[7])
                andar = int(linha[4])
                if(classe == "Ocupantes" and hora>= inicio and hora<= fim):
                    i = 0
                    for poligono_, cor, nome_ambiente, dados_adicionais, buracos in self.poligonos[andar]:
                        if(ambiente == nome_ambiente):
                            dados_adicionais["Ocupantes_hora"][hora] += quantidade
                            self.poligonos[andar][i][3] = dados_adicionais 
                        i+=1
        i=0
        for poligono_, cor, nome_ambiente, dados_adicionais, buracos in self.poligonos[andar]:
            dados_adicionais["Ocupantes"] = max(dados_adicionais["Ocupantes_hora"])
            self.poligonos[andar][i][3] = dados_adicionais 
            i+=1 
        

        self.valores_salvos.emit(self.table_cargas, )

    def atualizar_valores2(self, table_cargas, tabela_local):
        self.table_cargas = table_cargas
        self.tabela_local = tabela_local
        tabela = eventosTabela.ConteudosTabela_ARR(self.table_cargas)
        try:
            #zera as anotações de cada ambiente
            i_andar = 0
            for andar in self.poligonos:
                i=0
                for poligono_, cor, nome_ambiente, dados_adicionais in self.poligonos[i_andar]:
                    dados_adicionais["Ocupantes"] = 0
                    dados_adicionais["Ocupantes_hora"] = []
                    for i_ in range(25):
                        dados_adicionais["Ocupantes_hora"].append(0)
                    self.poligonos[i_andar][i][3] = dados_adicionais 
                    i+=1
                i_andar+=1

            for hora in range(25):


                for linha in tabela:
                    ambiente = linha[0]
                    classe = linha[2]
                    quantidade = int(linha[3])
                    inicio = int(linha[6])
                    fim = int(linha[7])
                    andar = int(linha[4])
                    if(classe == "Ocupantes" and hora>= inicio and hora<= fim):
                        i = 0
                        for poligono_, cor, nome_ambiente, dados_adicionais in self.poligonos[andar]:
                            if(ambiente == nome_ambiente):
                                dados_adicionais["Ocupantes_hora"][hora] += quantidade
                                self.poligonos[andar][i][3] = dados_adicionais 
                            i+=1
            i=0
            for poligono_, cor, nome_ambiente, dados_adicionais in self.poligonos[andar]:
                dados_adicionais["Ocupantes"] = max(dados_adicionais["Ocupantes_hora"])
                self.poligonos[andar][i][3] = dados_adicionais 
                i+=1 
            

            self.valores_salvos.emit(self.table_cargas, )
            
        except:
            None


class TelaAdicionarOcupantes(QDialog):
    valores_salvos = pyqtSignal(QtWidgets.QTableWidget, QtWidgets.QTableWidget)
    def __init__(self,table_cargas, tabela_local, ambiente, andar, parent=None):
        super().__init__(parent)
        self.andar = andar
        self.dicionario_atividades = {}
        with open("bibliotecas/cargas/atividades_ocupantes.txt", "r") as f:
            lines = f.readlines()
            for line in lines:
                if not line.startswith("@") and "=" in line:
                    # Processar a linha
                    self.dicionario_atividades[line.split("=")[0]] = float(line.split("=")[1].strip())
        classes_atividades = list(self.dicionario_atividades.keys())

        self.setWindowTitle("Adicionar Ocupantes")
        self.table_cargas = table_cargas
        self.tabela_local = tabela_local
        self.ambiente = ambiente

        # Layout
        layout = QtWidgets.QGridLayout()
        self.setLayout(layout)

        # Criando widgets
        self.label_atividades = QtWidgets.QLabel("Tipo Atividade:")
        self.combobox_atividades = QtWidgets.QComboBox()
        self.combobox_atividades.addItems(classes_atividades)
        self.label_qntd = QtWidgets.QLabel("N° Ocupantes:")
        self.textbox_qntd = QtWidgets.QLineEdit()
        self.botao_adicionar = QtWidgets.QPushButton("Adicionar")
        


        layout.addWidget(self.label_atividades)
        layout.addWidget(self.combobox_atividades)
        layout.addWidget(self.label_qntd)
        layout.addWidget(self.textbox_qntd)
        layout.addWidget(self.botao_adicionar)


        # Conectando sinais
        self.botao_adicionar.clicked.connect(self.adicionar_equipamento)



    def adicionar_equipamento(self):
        atividade = self.combobox_atividades.currentText()
        
        
        calor_dissipado = str(self.dicionario_atividades[atividade])

        rowPosition = self.table_cargas.rowCount()
        self.table_cargas.insertRow(rowPosition)
        classe_item = QtWidgets.QTableWidgetItem("Ocupantes")
        atividade_item = QtWidgets.QTableWidgetItem( "["+self.ambiente+"]"+atividade)
        calor_dissipado_item = QtWidgets.QTableWidgetItem(calor_dissipado)
        ambiente_item = QtWidgets.QTableWidgetItem(self.ambiente)
        qntd_item = QtWidgets.QTableWidgetItem(self.textbox_qntd.text())
        andar_item = QtWidgets.QTableWidgetItem(self.andar)
        self.table_cargas.setItem(rowPosition, 0, ambiente_item)
        self.table_cargas.setItem(rowPosition, 1, atividade_item)
        self.table_cargas.setItem(rowPosition, 2, classe_item)
        self.table_cargas.setItem(rowPosition, 3, qntd_item)
        self.table_cargas.setItem(rowPosition, 4, andar_item)
        self.table_cargas.setItem(rowPosition, 5, calor_dissipado_item)
        self.table_cargas.setItem(rowPosition, 6, QtWidgets.QTableWidgetItem("0"))
        self.table_cargas.setItem(rowPosition, 7, QtWidgets.QTableWidgetItem("24"))

        self.tabela_local.insertRow(rowPosition)
        classe_item = QtWidgets.QTableWidgetItem("Ocupantes")
        atividade_item = QtWidgets.QTableWidgetItem( "["+self.ambiente+"]"+atividade)
        calor_dissipado_item = QtWidgets.QTableWidgetItem(calor_dissipado)
        ambiente_item = QtWidgets.QTableWidgetItem(self.ambiente)
        qntd_item = QtWidgets.QTableWidgetItem(self.textbox_qntd.text())
        andar_item = QtWidgets.QTableWidgetItem(self.andar)    
        self.tabela_local.setItem(rowPosition, 0, ambiente_item)
        self.tabela_local.setItem(rowPosition, 1, atividade_item)
        self.tabela_local.setItem(rowPosition, 2, classe_item)
        self.tabela_local.setItem(rowPosition, 3, qntd_item)
        self.tabela_local.setItem(rowPosition, 4, andar_item)
        self.tabela_local.setItem(rowPosition, 5, calor_dissipado_item)
        self.tabela_local.setItem(rowPosition, 6, QtWidgets.QTableWidgetItem("0"))
        self.tabela_local.setItem(rowPosition, 7, QtWidgets.QTableWidgetItem("24"))

        self.valores_salvos.emit(self.table_cargas, self.tabela_local)
        # Fechando a janela
        self.close()

class TelaAdicionarEquipamento(QDialog):
    valores_salvos = pyqtSignal(QtWidgets.QTableWidget, QtWidgets.QTableWidget)
    def __init__(self,table_cargas, tabela_local, ambiente, andar, parent=None):
        super().__init__(parent)
        self.andar = andar
        classes_equipamentos = ["outros", "computador", "iluminação"]

        self.setWindowTitle("Adicionar Equipamento")
        self.table_cargas = table_cargas
        self.ambiente = ambiente
        self.tabela_local = tabela_local
        # Layout
        layout = QtWidgets.QGridLayout()
        self.setLayout(layout)




        materiais_dict = []
        with open("bibliotecas/cargas/cargas_termicas.txt", "r") as f:
            lines = f.readlines()
            for line in lines:
                if not line.startswith("@") and "=" in line:
                    # Processar a linha
                    materiais_dict.append(line.strip())
        # Criando a ListBox
        self.listbox_materiais = QtWidgets.QListWidget()
        # Populando a ListBox com a lista "ambientes" da janela principal
        self.listbox_materiais.addItems(materiais_dict)
        # Conectando o sinal de clique do item da ListBox
        self.listbox_materiais.itemClicked.connect(self.itemClicked)            

        # Criando widgets
        self.label_equipamentos_biblioteca = QtWidgets.QLabel("Biblioteca:")

        self.label_nome = QtWidgets.QLabel("Novo Equipamento:")
        self.textbox_nome = QtWidgets.QLineEdit()
        self.label_calor = QtWidgets.QLabel("Calor Dissipado [W]:")
        self.textbox_calor = QtWidgets.QLineEdit()
        self.label_classe = QtWidgets.QLabel("Classe de equipamento:")
        self.combobox_classes = QtWidgets.QComboBox()
        self.combobox_classes.addItems(classes_equipamentos)
        self.label_qntd = QtWidgets.QLabel("Qntd.:")
        self.textbox_qntd = QtWidgets.QLineEdit()
        self.botao_adicionar = QtWidgets.QPushButton("Adicionar")
        
        layout.addWidget(self.label_equipamentos_biblioteca,0,1)
        layout.addWidget(self.listbox_materiais,0,2,1,4)
        
        layout.addWidget(self.label_nome,1,0)
        layout.addWidget(self.textbox_nome,1,1)
        layout.addWidget(self.label_calor,1,2)
        layout.addWidget(self.textbox_calor,1,3)
        layout.addWidget(self.label_classe,2,0)
        layout.addWidget(self.combobox_classes,2,1)
        layout.addWidget(self.label_qntd,2,2)
        layout.addWidget(self.textbox_qntd,2,3)
        layout.addWidget(self.botao_adicionar,3,0)
        
        
        # Conectando sinais
        self.botao_adicionar.clicked.connect(self.adicionar_equipamento)


    def itemClicked(self, item):
        # Obtendo o índice do item clicado
        index = self.listbox_materiais.currentIndex().row()

        # Obtendo o nome do item clicado
        self.conteudo_str = self.listbox_materiais.item(index).text()
        
        itens = self.conteudo_str.split("=")[1].split(",")
        dicionario = {}
        key_value = self.conteudo_str.split("=")[1].split(",")
        nome = self.conteudo_str.split("=")[0]
        classe = key_value[1]
        calor = key_value[0]
        self.combobox_classes.setCurrentText(classe)       
        self.textbox_calor.setText(calor)
        self.textbox_nome.setText(nome)
    


    def adicionar_equipamento(self):
        # Obtendo o nome do equipamento
        nome_equipamento = self.textbox_nome.text()
        calor_dissipado = self.textbox_calor.text()
        




        if(nome_equipamento!= "" and str.isspace(nome_equipamento)==False):

            try:
                float(calor_dissipado),float(self.textbox_qntd.text())
                rowPosition = self.table_cargas.rowCount()
                self.table_cargas.insertRow(rowPosition)
                equipamento_item = QtWidgets.QTableWidgetItem("["+self.ambiente+"]"+ nome_equipamento)
                calor_dissipado_item = QtWidgets.QTableWidgetItem(calor_dissipado)
                ambiente_item = QtWidgets.QTableWidgetItem(self.ambiente)
                qntd_item = QtWidgets.QTableWidgetItem(self.textbox_qntd.text())
                andar_item = QtWidgets.QTableWidgetItem(self.andar)
                classe = self.combobox_classes.currentText()
                classe_item = QtWidgets.QTableWidgetItem(classe)   
                self.table_cargas.setItem(rowPosition, 0, ambiente_item)
                self.table_cargas.setItem(rowPosition, 1, equipamento_item)
                self.table_cargas.setItem(rowPosition, 2, classe_item)
                self.table_cargas.setItem(rowPosition, 3, qntd_item)
                self.table_cargas.setItem(rowPosition, 4, andar_item)
                self.table_cargas.setItem(rowPosition, 5, calor_dissipado_item)
                self.table_cargas.setItem(rowPosition, 6, QtWidgets.QTableWidgetItem("0"))
                self.table_cargas.setItem(rowPosition, 7, QtWidgets.QTableWidgetItem("24"))
                
                rowPosition = self.tabela_local.rowCount()
                self.tabela_local.insertRow(rowPosition)
                equipamento_item = QtWidgets.QTableWidgetItem("["+self.ambiente+"]"+ nome_equipamento)
                calor_dissipado_item = QtWidgets.QTableWidgetItem(calor_dissipado)
                ambiente_item = QtWidgets.QTableWidgetItem(self.ambiente)
                qntd_item = QtWidgets.QTableWidgetItem(self.textbox_qntd.text())
                andar_item = QtWidgets.QTableWidgetItem(self.andar)
                classe = self.combobox_classes.currentText()
                classe_item = QtWidgets.QTableWidgetItem(classe)
                self.tabela_local.setItem(rowPosition, 0, ambiente_item)
                self.tabela_local.setItem(rowPosition, 1, equipamento_item)
                self.tabela_local.setItem(rowPosition, 2, classe_item)
                self.tabela_local.setItem(rowPosition, 3, qntd_item)
                self.tabela_local.setItem(rowPosition, 4, andar_item)
                self.tabela_local.setItem(rowPosition, 5, calor_dissipado_item)
                self.tabela_local.setItem(rowPosition, 6, QtWidgets.QTableWidgetItem("0"))
                self.tabela_local.setItem(rowPosition, 7, QtWidgets.QTableWidgetItem("24"))
                self.valores_salvos.emit(self.table_cargas, self.tabela_local)
                # Fechando a janela
                self.close()
            except:
                QtWidgets.QMessageBox.information(self, "Erro", "Preencha corretamente os itens")
        
        else:
            QtWidgets.QMessageBox.information(self, "Erro", "Nomeie o equipamento")

class TelaConfigurarHVAC(QDialog):
    valores_salvos = pyqtSignal(float, str, str, float, float, float, int, int, int, int, float)  # Sinal personalizado
    def __init__(self, potencia_refrigeração, classe_compressor, janela_principal, unidade, COP, temperatura_desejada, ACH_troca_de_ar_h, horario_inicial_hora, horario_final_hora, horario_inicial_min, horario_final_min, temperatura_limite_inferior):
        super().__init__()
        idioma = parametros.linguagem()
        self.textos_json = {}
        self.escolhas_json_en = {}
        self.escolhas_json_pt = {}
        # Opening JSON file
        with open('data/interface.json', encoding='utf8') as json_file:
            data = json.load(json_file)
            self.textos_json = data[idioma+"_tela_hvac_config"]
        with open('data/equivalente.json', encoding='utf8') as json_file:
            data = json.load(json_file)
            self.escolhas_json_en = data["hvac"]["en"]
            self.escolhas_json_pt = data["hvac"]["pt"]

        classes_compressor = []
        self.classes_ambientes_dict = {}
        if(idioma == "pt"):
            classes_compressor = ["inverter (controle ideal)", "inverter (controle proporcional)", "normal split (on-off)"]
            self.classes_ambientes_dict = {"personalizado":0}
        if(idioma == "en"):
            classes_compressor = ["inverter (ideal control)", "inverter (proportional control)", "normal split (on-off)"]
            self.classes_ambientes_dict = {"custom":0}
        with open("bibliotecas/ach/ambientes.txt", "r") as f:
            lines = f.readlines()
            for line in lines:
                chave = line.split("=")[0]
                valor = line.split("=")[1]
                self.classes_ambientes_dict[chave] = valor
        self.classes_ambientes = list(self.classes_ambientes_dict)
        unidades = ["W","cal/h", "Btu/h"]
        self.setWindowTitle(self.textos_json["titulo"])
        self.unidade = unidade
        self.potencia_refrigeração = potencia_refrigeração
        self.classe_compressor = classe_compressor
        self.COP = COP
        self.temperatura_desejada = temperatura_desejada
        self.temperatura_limite_inferior = temperatura_limite_inferior
        self.ACH_troca_de_ar_h = ACH_troca_de_ar_h
        self.horario_inicial_hora = horario_inicial_hora
        self.horario_final_hora = horario_final_hora
        self.horario_inicial_min, self.horario_final_min = horario_inicial_min, horario_final_min
        # Layout
        layout = QtWidgets.QGridLayout()
        self.setLayout(layout)

        # Criando widgets
        self.label_potencia = QtWidgets.QLabel(self.textos_json["potencia refrigeração"])
        self.textbox_potencia = QtWidgets.QLineEdit()
        self.textbox_potencia.setText(str(potencia_refrigeração))
        self.combobox_unidade = QtWidgets.QComboBox()
        self.combobox_unidade.addItems(unidades)
        self.combobox_unidade.setCurrentText(unidade) 

        self.label_classe = QtWidgets.QLabel(self.textos_json["metodo controle"])
        self.combobox_classes = QtWidgets.QComboBox()
        self.combobox_classes.addItems(classes_compressor)
        self.combobox_classes.setCurrentText(classe_compressor) 
        self.combobox_classes.currentIndexChanged.connect(self.comboboxClasseChanged)

        self.label_COP = QtWidgets.QLabel(self.textos_json["cop medio"])
        self.textbox_COP = QtWidgets.QLineEdit()
        self.textbox_COP.setText(str(COP))        

        self.label_temperatura_desejada = QtWidgets.QLabel(self.textos_json["temperatura de setpoint"])
        self.textbox_temperatura_desejada = QtWidgets.QLineEdit()

        if(classe_compressor == "inverter (controle proporcional)" or classe_compressor =="inverter (controle ideal)" or classe_compressor =="inverter (ideal control)" or classe_compressor =="inverter (proportional control)"):
            self.textbox_temperatura_desejada.setText(str(temperatura_desejada)) 
        if(classe_compressor == "normal split (on-off)"):
            histerese = (temperatura_desejada-temperatura_limite_inferior)/2
            self.textbox_temperatura_desejada.setText(str(histerese)) 



        self.label_temperatura_inferior = QtWidgets.QLabel(self.textos_json["temperatura histerese"])
        self.textbox_temperatura_inferior = QtWidgets.QLineEdit()
        self.textbox_temperatura_inferior.setText(str(temperatura_limite_inferior)) 

        self.label_horario = QtWidgets.QLabel(self.textos_json["horario de op"])
        self.textbox_horario_inicial_hora = QtWidgets.QLineEdit()
        hora_inicial = str(self.horario_inicial_hora)
        if(len(hora_inicial) == 1):
            hora_inicial = "0"+hora_inicial
        min_inicial = str(self.horario_inicial_min)
        if(len(min_inicial) == 1):
            min_inicial = "0"+min_inicial
        self.textbox_horario_inicial_hora.setText(hora_inicial+":"+min_inicial) 
        self.textbox_horario_inicial_hora.setInputMask("HH:HH")

        self.textbox_horario_final_hora = QtWidgets.QLineEdit()
        hora_final = str(self.horario_final_hora)
        if(len(hora_final) == 1):
            hora_final = "0"+hora_final
        min_final = str(self.horario_final_min)
        if(len(min_final) == 1):
            min_final = "0"+min_final
        self.textbox_horario_final_hora.setText(hora_final+":"+min_final) 
        self.textbox_horario_final_hora.setInputMask("HH:HH")


        self.label_trocas_ar_h = QtWidgets.QLabel(self.textos_json["ACH"])
        self.dica_ach = QtWidgets.QLabel()
        self.dica_ach.setPixmap(QtGui.QPixmap("icons/question.png"))
        self.dica_ach.setToolTip(self.textos_json["tooltip"])
        self.textbox_troca_ar_h = QtWidgets.QLineEdit()
        self.textbox_troca_ar_h.setText(str(self.ACH_troca_de_ar_h)) 
        
        self.combobox_ACH = QtWidgets.QComboBox()
        self.combobox_ACH.addItems(self.classes_ambientes)
        self.combobox_ACH.setCurrentText(self.textos_json["personalizado"]) 
        self.combobox_ACH.currentIndexChanged.connect(self.comboboxACHChanged)


        self.botao_salvar = QtWidgets.QPushButton(self.textos_json["salvar"])

        layout.addWidget(self.label_potencia,0,0)
        layout.addWidget(self.textbox_potencia,0,1)
        layout.addWidget(self.combobox_unidade,0,2)
        layout.addWidget(self.label_classe,1,0)
        layout.addWidget(self.combobox_classes,1,1,1,2)
        layout.addWidget(self.label_COP,2,0)
        layout.addWidget(self.textbox_COP,2,1)
        layout.addWidget(self.label_temperatura_desejada,3,0)
        layout.addWidget(self.textbox_temperatura_desejada,3,1)
        layout.addWidget(self.label_temperatura_inferior,3,2)
        layout.addWidget(self.textbox_temperatura_inferior,3,3)    
        layout.addWidget(self.label_horario,4,0)
        layout.addWidget(self.textbox_horario_inicial_hora,4,1)

        layout.addWidget(self.textbox_horario_final_hora,4,2)


        layout.addWidget(self.label_trocas_ar_h,5,0)
        layout.addWidget(self.combobox_ACH, 5, 1)
        layout.addWidget(self.textbox_troca_ar_h,5,2)
        layout.addWidget(self.dica_ach,5,3)
        layout.addWidget(self.botao_salvar)

        self.comboboxClasseChanged()

        # Conectando sinais
        self.botao_salvar.clicked.connect(self.salvar)

    def comboboxClasseChanged(self):
            classe = self.combobox_classes.currentText()
            if(classe == "inverter (controle proporcional)" or classe == "inverter (proportional control)"):
                self.label_temperatura_inferior.setVisible(True)
                self.textbox_temperatura_inferior.setVisible(True)     
                self.label_temperatura_desejada.setText("Temperatura Limite Superior\n(controle proporcional):")
                self.label_temperatura_inferior.setText("Temperatura Limite Inferior\n(controle proporcional):")           
                self.textbox_temperatura_inferior.setText(str(self.temperatura_limite_inferior)) 
                self.textbox_temperatura_desejada.setText(str(self.temperatura_desejada))
            if(classe == "inverter (controle ideal)") or classe == "inverter (ideal control)":
                self.label_temperatura_inferior.setVisible(False)
                self.textbox_temperatura_inferior.setVisible(False)
                self.label_temperatura_desejada.setText(self.textos_json["temperatura de setpoint"])
                self.textbox_temperatura_inferior.setText(str(self.temperatura_limite_inferior)) 
                self.textbox_temperatura_desejada.setText(str(self.temperatura_desejada))
            if(classe == "normal split (on-off)"):
                self.label_temperatura_inferior.setVisible(True)
                self.textbox_temperatura_inferior.setVisible(True)     
                self.label_temperatura_desejada.setText(self.textos_json["temperatura de setpoint"])
                self.label_temperatura_inferior.setText(self.textos_json["temperatura histerese 2"])
                histerese = (self.temperatura_desejada-self.temperatura_limite_inferior)/2
                self.textbox_temperatura_desejada.setText(str(self.temperatura_desejada-histerese)) 
                self.textbox_temperatura_inferior.setText(str(histerese)) 

    def comboboxACHChanged(self):
            classe = self.combobox_ACH.currentText()
            valor = self.classes_ambientes_dict[classe]
            self.textbox_troca_ar_h.setText(str(valor))


    def salvar(self):
        try:
            self.potencia_refrigeração = float(self.textbox_potencia.text())
            self.classe_compressor = self.combobox_classes.currentText()
            if(self.classe_compressor == "inverter (proportional control)"):
                self.classe_compressor = "inverter (controle proporcional)"
            if(self.classe_compressor == "inverter (controle ideal)"):
                self.classe_compressor = "inverter (controle ideal)"

            self.unidade = self.combobox_unidade.currentText()
            self.COP = float(self.textbox_COP.text())
            if(self.classe_compressor == "inverter (controle proporcional)"):
                self.temperatura_desejada = float(self.textbox_temperatura_desejada.text())
                self.temperatura_limite_inferior = float(self.textbox_temperatura_inferior.text())
            if(self.classe_compressor == "inverter (controle ideal)"):
                self.temperatura_desejada = float(self.textbox_temperatura_desejada.text())
            if(self.classe_compressor == "normal split (on-off)"):
                self.temperatura_desejada = float(self.textbox_temperatura_desejada.text()) + float(self.textbox_temperatura_inferior.text()) #histerese suprior
                self.temperatura_limite_inferior = float(self.textbox_temperatura_desejada.text()) - float(self.textbox_temperatura_inferior.text()) #histerese inferior
            self.ACH_troca_de_ar_h = float(self.textbox_troca_ar_h.text())
            try:
                self.horario_inicial_hora = int(self.textbox_horario_inicial_hora.text().split(":")[0])
                self.horario_final_hora = int(self.textbox_horario_final_hora.text().split(":")[0])
                self.horario_inicial_min = int(self.textbox_horario_inicial_hora.text().split(":")[1])
                self.horario_final_min = int(self.textbox_horario_final_hora.text().split(":")[1])

                salvar = True
                if(self.horario_inicial_hora+self.horario_inicial_min/60 > self.horario_final_hora + self.horario_final_min/60):
                    #QtWidgets.QMessageBox.information(self, "Aviso", "Horário inicial maior que horário final")
                    salvar = True
                if(self.horario_inicial_hora >24 or self.horario_final_hora>24):
                    QtWidgets.QMessageBox.information(self, self.textos_json["erro"], "Horário maior que o limite de 24h diário")
                    salvar = False                
                if(self.horario_inicial_min >60 or self.horario_final_min>60):
                    QtWidgets.QMessageBox.information(self, self.textos_json["erro"], "Minutos ultrapassando ou igual a 60")
                    salvar = False
                if(self.horario_final_hora == 24 and self.horario_final_min !=0):
                    QtWidgets.QMessageBox.information(self, self.textos_json["erro"], "Horário maior que o limite de 24h diário")
                    salvar = False           
                if (salvar==True):
                    # Emitir sinal com os valores atualizados
                    self.valores_salvos.emit(self.potencia_refrigeração, self.classe_compressor, self.unidade, self.COP, self.temperatura_desejada, self.ACH_troca_de_ar_h, self.horario_inicial_hora, self.horario_final_hora, self.horario_inicial_min, self.horario_final_min, self.temperatura_limite_inferior)
                    # Fechando a janela
                    self.close()
            except:
                QtWidgets.QMessageBox.information(self, self.textos_json["erro"], "Horário no formato errado! O formato correto deve ser HH:MM")
        except:
            QtWidgets.QMessageBox.information(self, self.textos_json["erro"], "Insira somente números nos campos de Potência, COP, temperatura e ACH")




class TelaSimulação(QDialog):
    def __init__(self,  altura, tables_dicionario, potencia_refrigeração, latitude_graus, unidade_potencia, COP, paredes_default, temperatura_desejada, ACH_troca_de_ar_h, horario_hvac, andar_terreo, angulo_N_geral, compressão_convensional_ou_inverter, temperatura_limite_inferior, metodo_calculo_temp_solo, temp_solo_cte):
        super().__init__()
        self.metodo_calculo_temp_solo, self.temp_solo_cte = metodo_calculo_temp_solo, temp_solo_cte
        self.compressão_convensional_ou_inverter = compressão_convensional_ou_inverter
        self.Relatorio_window = None
        self.tables_dicionario = tables_dicionario
        self.altura = altura
        self.potencia_refrigeração = potencia_refrigeração
        self.latitude_graus = latitude_graus
        self.unidade_potencia = unidade_potencia
        self.COP = COP
        self.paredes_default = paredes_default
        self.temperatura_desejada = temperatura_desejada
        self.temperatura_limite_inferior = temperatura_limite_inferior
        self.setWindowTitle("Simulação")
        self.taxa_kwh_reais = 1.20
        self.ACH_troca_de_ar_h = ACH_troca_de_ar_h
        self.horario_hvac = horario_hvac
        self.andar_terreo = andar_terreo
        self.angulo_N_geral = angulo_N_geral
        self.refrigeração_ideal = False
        self.somente_iterar = False
        # Layout
        layout = QtWidgets.QGridLayout()
        self.setLayout(layout)

        # Criando widgets
        self.label_taxa = QtWidgets.QLabel("Taxa [$/kwh]:")
        self.textbox_taxa = QtWidgets.QLineEdit()
        self.textbox_taxa.setText(str(self.taxa_kwh_reais))
        self.label_data = QtWidgets.QLabel("Dia do ano para simular:")
        self.textbox_dia = QtWidgets.QLineEdit()
        self.textbox_dia.setText("21")
        self.label_data_separador = QtWidgets.QLabel("/")        
        self.textbox_mes = QtWidgets.QLineEdit()
        self.textbox_mes.setText("3")
        self.botao_simular_dia = QtWidgets.QPushButton("Simular Dia")
        self.botao_simular_dia_mais_quente = QtWidgets.QPushButton("Simular Dia Mais Quente")
        self.botao_simular_refrigerador_idealDia = QtWidgets.QPushButton("Refrigeração Ideal (dia)")
        self.botao_simular_idealDia_mais_quente = QtWidgets.QPushButton("Refrigeração Ideal \nDia Mais Quente")
        self.label_separador = QtWidgets.QLabel("______________________________________________________________________________")
        self.botao_simular_ano = QtWidgets.QPushButton("Simular Ano")
        self.botao_simular_refrigerador_idealAno = QtWidgets.QPushButton("Refrigeração Ideal (ano)")
        self.botao_simular_dia.clicked.connect(self.SimularDia)
        self.botao_simular_dia_mais_quente.clicked.connect(self.SimularDiaMaisQuente)
        self.botao_simular_idealDia_mais_quente.clicked.connect(self.ProcurarRefrigeradorIdealDia_MaisQuente)
        self.botao_simular_ano.clicked.connect(self.SimularAno)
        self.botao_simular_refrigerador_idealDia.clicked.connect(self.ProcurarRefrigeradorIdealDia)
        self.botao_simular_refrigerador_idealAno.clicked.connect(self.ProcurarRefrigeradorIdealAno)
        self.label_qualidade_simulação = QtWidgets.QLabel("Resolução simulação anual: ")  
        qualidades_simulacao_list = ["muito baixa ΔT =240s", "baixa ΔT =120s", "padrão ΔT =60s", "alta  ΔT =30s"]
        self.combobox_qualidade_simulacao = QtWidgets.QComboBox()
        self.combobox_qualidade_simulacao.addItems(qualidades_simulacao_list)
        self.combobox_qualidade_simulacao.setCurrentText("muito baixa ΔT =240s") 
        layout.addWidget(self.label_taxa, 0,0)
        layout.addWidget(self.textbox_taxa, 0,1)
        layout.addWidget(self.label_data, 1,0)
        layout.addWidget(self.textbox_dia, 1, 1)
        layout.addWidget(self.label_data_separador, 1, 2)
        layout.addWidget(self.textbox_mes, 1, 3)
        layout.addWidget(self.botao_simular_dia,2,0)
        layout.addWidget(self.botao_simular_refrigerador_idealDia,2,1)
        layout.addWidget(self.botao_simular_dia_mais_quente,2,2)
        layout.addWidget(self.botao_simular_idealDia_mais_quente,2,3)
        layout.addWidget(self.label_separador,3,0,1,4)
        layout.addWidget(self.label_qualidade_simulação,4,0)
        layout.addWidget(self.combobox_qualidade_simulacao,4,1)
        layout.addWidget(self.botao_simular_ano,4,2)
        layout.addWidget(self.botao_simular_refrigerador_idealAno,4,3)


    def ProcurarRefrigeradorIdealDia(self):
        self.potencia_refrigeração = 1111111111111111111
        self.compressão_convensional_ou_inverter = "inverter (controle ideal)"
        QtWidgets.QMessageBox.information(self, "Info", "Pra este modo de simulação usado método de controle " + self.compressão_convensional_ou_inverter + ".")
        self.refrigeração_ideal= True
        self.SimularDia()

    def ProcurarRefrigeradorIdealAno(self):
        self.potencia_refrigeração = 1111111111111111111
        self.compressão_convensional_ou_inverter = "inverter (controle ideal)"
        QtWidgets.QMessageBox.information(self, "Info", "Pra este modo de simulação usado método de controle " + self.compressão_convensional_ou_inverter + ".")
        self.refrigeração_ideal= True
        self.SimularAno()        

    def SimularDiaMaisQuente(self):
        Arquivo_climatico = arquivo_climatico.Historico()
        ano = Arquivo_climatico.ano
        temperatura, mes, dia = Arquivo_climatico.Temperatura_maxima(ano)
        self.textbox_dia.setText(str(dia))
        self.textbox_mes.setText(str(mes))
        QtWidgets.QMessageBox.information(self, "Info", "Será simulada a data " + str(dia) + "/" + str(mes))
        self.SimularDia()

    def ProcurarRefrigeradorIdealDia_MaisQuente(self):
        self.potencia_refrigeração = 1111111111111111111
        self.refrigeração_ideal= True
        Arquivo_climatico = arquivo_climatico.Historico()
        ano = Arquivo_climatico.ano
        temperatura, mes, dia = Arquivo_climatico.Temperatura_maxima(ano)
        self.textbox_dia.setText(str(dia))
        self.textbox_mes.setText(str(mes))
        QtWidgets.QMessageBox.information(self, "Info", "Será simulada a data " + str(dia) + "/" + str(mes))
        self.SimularDia()


    def SimularAno(self):

        # thread_simulação = threading.Thread(target=lambda: simulacao.Laterais(self.table_paredes, self.table, self.table_horizontal, self.table_cargas, 2.1, self.potencia_refrigeração, "Ano", 0,0,""))
        # thread_simulação.start()
        thread_progresso = threading.Thread(target=progresso.Progresso)
        thread_progresso.start()
        
        qualidade_simulacao_text = self.combobox_qualidade_simulacao.currentText()
        self.taxa_kwh_reais = float(self.textbox_taxa.text())
        Relatorio_simulacao = simulacao.Laterais()
        
        self.Relatorio_window = Relatorio_simulacao.Iniciar(self.tables_dicionario, self.altura, self.potencia_refrigeração, "Ano", 0,0,"", qualidade_simulacao_text, self.latitude_graus, self.unidade_potencia, self.COP, self.paredes_default, self.temperatura_desejada, self.taxa_kwh_reais, self.ACH_troca_de_ar_h, self.horario_hvac, self.andar_terreo, self.angulo_N_geral, self.compressão_convensional_ou_inverter, self.temperatura_limite_inferior, self.refrigeração_ideal,self.somente_iterar, self.metodo_calculo_temp_solo, self.temp_solo_cte)
        self.Relatorio_window.show()
        # Fechando a janela
        self.close()


    def SimularDia(self):
        stop_threads = False
        thread_progresso = threading.Thread(target=progresso.ProgressoDia, args=(id, lambda: stop_threads))
        thread_progresso.start()
        dia = 0
        mes = 0
        self.taxa_kwh_reais = float(self.textbox_taxa.text())
        prosseguir = True
        try:
            dia = int(self.textbox_dia.text())
            mes = int(self.textbox_mes.text())
        except:
            print("Data no formato errado")
            prosseguir = False
        if(prosseguir == True):
            Relatorio_simulacao = simulacao.Laterais()

            self.Relatorio_window = Relatorio_simulacao.Iniciar(self.tables_dicionario, self.altura, self.potencia_refrigeração, "Dia", dia, mes,"", "", self.latitude_graus, self.unidade_potencia, self.COP, self.paredes_default, self.temperatura_desejada, self.taxa_kwh_reais, self.ACH_troca_de_ar_h, self.horario_hvac, self.andar_terreo, self.angulo_N_geral, self.compressão_convensional_ou_inverter, self.temperatura_limite_inferior, self.refrigeração_ideal, self.somente_iterar, self.metodo_calculo_temp_solo, self.temp_solo_cte)
            self.Relatorio_window.show()
            with open("temp/progresso2.txt", "a+") as arquivo:
                valor = "FimSimulação"
                arquivo.write(valor)
            arquivo.close()
            # Fechando a janela
            self.close()



class TelaConfigurarClimaGeo(QDialog):

    valores_salvos = pyqtSignal(float, float, str, float)  # Sinal personalizado

    def __init__(self, latitude, angulo_N, metodo_calculo_temp_solo, temp_solo_cte):
        super().__init__()
        idioma = parametros.linguagem() + "_clima_geo"
        self.textos_json = {}
        # Opening JSON file
        with open('data/interface.json', encoding='utf8') as json_file:
            data = json.load(json_file)
            self.textos_json = data[idioma]
        self.setWindowTitle(self.textos_json["janela"])
        self.temp_solo_cte = temp_solo_cte
        self.latitude_graus = latitude
        self.angulo_N = angulo_N
        # Layout
        layout = QtWidgets.QGridLayout()
        self.setLayout(layout)

        # Criando widgets
        self.label_latitude = QtWidgets.QLabel(self.textos_json["Latitude"])
        self.textbox_latitude = QtWidgets.QLineEdit()
        self.textbox_latitude.setText(str(latitude))
        self.label_angulo_N = QtWidgets.QLabel(self.textos_json["Angulo N"])
        self.textbox_angulo_N = QtWidgets.QLineEdit()
        self.textbox_angulo_N.setText(str(self.angulo_N))
        self.dica_angulo_N = QtWidgets.QLabel()
        self.dica_angulo_N.setPixmap(QtGui.QPixmap("icons/question.png"))
        self.dica_angulo_N.setToolTip(self.textos_json["angulo N tooltip"])

        self.label_método_solo = QtWidgets.QLabel(self.textos_json["metodo solo temp"])
        self.tipos_temp_solo_list = ["Constante", "senoidal (comb.lin. solução dia + ano)"] 
        self.combobox_tipos_temp_solo = QtWidgets.QComboBox()
        self.combobox_tipos_temp_solo.addItems(self.tipos_temp_solo_list)
        self.combobox_tipos_temp_solo.setCurrentText(metodo_calculo_temp_solo)  
        self.combobox_tipos_temp_solo.currentIndexChanged.connect(self.comboboxSoloChanged) 
        self.label_temp_solo  = QtWidgets.QLabel(self.textos_json["temperatura solo"])
        self.textbox_temp_solo = QtWidgets.QLineEdit()
        self.label_temp_solo.setVisible(False)
        self.textbox_temp_solo.setVisible(False)
        self.textbox_temp_solo.setText(str(self.temp_solo_cte))
        self.botao_salvar = QtWidgets.QPushButton(self.textos_json["salvar"])
        self.botao_carregar_arquivo = QtWidgets.QPushButton(self.textos_json["carregar arquivo climatico"])

        # Adicionando widgets ao layout
        layout.addWidget(self.label_latitude, 0, 0)
        layout.addWidget(self.textbox_latitude, 0, 1)
        layout.addWidget(self.label_angulo_N, 1, 0)
        layout.addWidget(self.textbox_angulo_N, 1, 1)
        layout.addWidget(self.dica_angulo_N, 1, 2)
        layout.addWidget(self.label_método_solo, 2, 0)
        layout.addWidget(self.combobox_tipos_temp_solo, 2, 1)
        layout.addWidget(self.label_temp_solo, 2, 2)
        layout.addWidget(self.textbox_temp_solo, 2, 3)        
        layout.addWidget(self.botao_salvar, 3, 0)
        layout.addWidget(self.botao_carregar_arquivo, 4, 0)

        # Conectando sinais
        self.botao_salvar.clicked.connect(self.salvar)
        self.botao_carregar_arquivo.clicked.connect(self.carregar_arquivo_climatico)
        self.comboboxSoloChanged()
    def comboboxSoloChanged(self):
            classe = self.combobox_tipos_temp_solo.currentText()
            if classe == "Constante":
                self.textbox_temp_solo.setText(str(self.temp_solo_cte))
                self.label_temp_solo.setVisible(True)
                self.textbox_temp_solo.setVisible(True)
            if classe == "periódico (senoidal)":
                self.label_temp_solo.setVisible(False)
                self.textbox_temp_solo.setVisible(False)

    def salvar(self):
        try:
            textão = self.textbox_latitude.text()
            self.latitude_graus = float(self.textbox_latitude.text())
            self.angulo_N = float(self.textbox_angulo_N.text())
            self.metodo = self.combobox_tipos_temp_solo.currentText()
            self.temp_solo_cte = float(self.textbox_temp_solo.text())
            # Emitir sinal com os valores atualizados
            self.valores_salvos.emit(self.latitude_graus, self.angulo_N, self.metodo, self.temp_solo_cte)
            # Fechando a janela
            self.close()
        except:
            QtWidgets.QMessageBox.information(self, "Erro", "Latitude ou ângulo ao norte no formato incorreto.")

            

    def carregar_arquivo_climatico(self):
        # Abrir diálogo de seleção de arquivo
        caminho_arquivo, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Selecionar Arquivo Climático", "", "Arquivos Climáticos (*.epw)"
        )
        print(str(caminho_arquivo))
        # Verificar se o arquivo foi selecionado
        if not caminho_arquivo:
            return

        # Copiar o arquivo para a pasta "arquivo climatico"
        shutil.copy(caminho_arquivo, "temp/arquivos_climaticos")

        with open("temp/arquivos_climaticos/config.txt", "a+") as arquivo:
            valor = ""
            arquivo.write(valor)
            
        arquivo.close()
        with open("temp/arquivos_climaticos/config.txt", "w") as arquivo:
            valor = "path="+caminho_arquivo.split("/")[-1]
            arquivo.write(valor)

            arquivo.close()
        # Exibir mensagem de sucesso
        QtWidgets.QMessageBox.information(self, "Sucesso", "Arquivo climático carregado com sucesso!")
        latitude = self.leitura_arquivo_climatico()
        self.textbox_latitude.setText(str(latitude))
        self.latitude_graus = latitude
        
        try:

            self.valores_salvos.emit(float(self.textbox_latitude.text()), float(self.textbox_angulo_N.text()), self.combobox_tipos_temp_solo.currentText(), float(self.textbox_temp_solo.text()))
        except:
            QtWidgets.QMessageBox.information(self, "Erro", "Latitude no formato incorreto.")

    #encontra a latitude do arquivo
    def leitura_arquivo_climatico(self):
        # Abra o arquivo em modo de leitura ('r')
        nome_arquivo = None
        with open("temp/arquivos_climaticos/config.txt", "r") as f:
            lines = f.readlines()
            for line in lines:
                if("path=" in line):
                    nome_arquivo = line.split("=")[1].strip()

        caminho = "temp/arquivos_climaticos/"+nome_arquivo
        try:
            with open(caminho, 'r') as f:
                lines = f.readlines()
                latitude = lines[0].split(",")[6]
                return latitude
                        
        except FileNotFoundError:
            print(f'O arquivo "{nome_arquivo}" não foi encontrado.')
            return None
        
        

class TelaCriarJanelaPorta(QDialog):
    valores_salvos = pyqtSignal(str, str, str, str, str, str, str, str)  # Sinal personalizado
    def __init__(self, SHGC, largura, altura, tipoItem, espessura, k, U, UouSHGC):
        idioma = parametros.linguagem() + "_janelas_portas"
        self.textos_json = {}
        # Opening JSON file
        with open('data/interface.json', encoding='utf8') as json_file:
            data = json.load(json_file)
            self.textos_json = data[idioma]
        self.tipoItem = tipoItem
        self.SHGC = SHGC
        self.largura = largura
        self.altura = altura
        self.espessura = espessura
        self.k = k
        self.U = U
        self.UouSHGC = UouSHGC
        super().__init__()

        self.setWindowTitle(self.textos_json["titulo"])

        # Layout
        self.layout = QtWidgets.QGridLayout()
        self.setLayout(self.layout)
        self.layout.setColumnMinimumWidth(5, 750)
        # Criando widgets
        self.b1 = QtWidgets.QRadioButton(self.textos_json["janela"])
        self.layout.addWidget(self.b1,0,0)
        self.b2 = QtWidgets.QRadioButton(self.textos_json["porta"])
        self.layout.addWidget(self.b2,0,1)

        self.label_largura = QtWidgets.QLabel(self.textos_json["largura"])
        self.textbox_label_largura = QtWidgets.QLineEdit()
        self.textbox_label_largura.setText(str(largura))
        self.label_altura = QtWidgets.QLabel(self.textos_json["altura"])
        self.textbox_label_altura = QtWidgets.QLineEdit()
        self.textbox_label_altura.setText(str(altura))
        self.label_espessura = QtWidgets.QLabel(self.textos_json["espessura"])
        self.textbox_label_espessura = QtWidgets.QLineEdit()
        self.textbox_label_espessura.setText(str(espessura))

        self.label_SHGC = QtWidgets.QLabel(self.textos_json["shgc"])
        self.textbox_label_SHGC = QtWidgets.QLineEdit()
        self.textbox_label_SHGC.setText(str(SHGC))
        self.textbox_label_SHGC.textChanged.connect(self.textbox_label_SHGC_changed)
        self.label_k = QtWidgets.QLabel("k [W/(m·K)]:")
        self.textbox_label_k = QtWidgets.QLineEdit()
        self.textbox_label_k.setText(str(k))
        if(self.tipoItem == "janela"):
            self.textbox_label_k.setEnabled(False) # a parcela de U devido a condução interna é despresivel para a espessura da janela que é muito fina
        self.textbox_label_k.textChanged.connect(self.textbox_label_SHGC_changed)


        self.label_U = QtWidgets.QLabel("U [W/(m²·K)]:")
        self.textbox_label_U = QtWidgets.QLineEdit()
        self.textbox_label_U.setText(str(U))
        self.textbox_label_U.textChanged.connect(self.textbox_label_U_changed)


        cor_paredes_list = parametros.cores_paredes_list
        self.combobox_cor = QtWidgets.QComboBox()
        self.combobox_cor.addItems(cor_paredes_list)
                

        

        self.layout.addWidget(self.label_largura,1,0)
        self.layout.addWidget(self.textbox_label_largura,1,1)
        self.layout.addWidget(self.label_altura,2,0)
        self.layout.addWidget(self.textbox_label_altura,2,1)
        self.layout.addWidget(self.label_espessura,3,0)
        self.layout.addWidget(self.textbox_label_espessura,3,1)
                
        self.layout.addWidget(self.label_SHGC,4,0)
        self.layout.addWidget(self.textbox_label_SHGC,4,1)
        self.layout.addWidget(self.combobox_cor,4,1)
     
        self.combobox_cor.setVisible(False)

        self.layout.addWidget(self.label_k,4,2)
        self.layout.addWidget(self.textbox_label_k,4,3)
        self.layout.addWidget(self.label_U,5,0)
        self.layout.addWidget(self.textbox_label_U,5,1)


        self.botao_salvar = QtWidgets.QPushButton(self.textos_json["salvar"])
        self.layout.addWidget(self.botao_salvar,7,0)
        # Conectando sinais
        self.botao_salvar.clicked.connect(self.salvar)

        self.b1.toggled.connect(lambda:self.btnstate(self.b1))
        self.b2.toggled.connect(lambda:self.btnstate(self.b2))
        if(self.tipoItem == "janela"):
            self.b1.setChecked(True)
        if(self.tipoItem == "porta"):
            self.b2.setChecked(True)

        self.configurar_tabela_materiais()

    def textbox_label_SHGC_changed(self):
        if(self.tipoItem == "porta"):
            if(  (self.textbox_label_SHGC.text()!= "" and self.textbox_label_SHGC.text()!= " ") or  (self.textbox_label_k.text()!= "" and self.textbox_label_k.text()!= " ")   ):
                self.textbox_label_U.setText("")
                self.UouSHGC = "SHGC"

    def textbox_label_U_changed(self):
        if(self.tipoItem == "porta"):
            if(self.textbox_label_U.text()!=""):
                self.textbox_label_k.setText("")
                self.textbox_label_SHGC.setText("")
                self.UouSHGC = "U"


    def configurar_tabela_materiais(self):
        materiais_dict = []
        with open("bibliotecas/portas e janelas/materiais.txt", "r") as f:
            lines = f.readlines()
            for line in lines:
                if not line.startswith("#") and "=" in line:
                    # Processar a linha
                    materiais_dict.append(line.strip())

        # Criando a ListBox
        self.listbox_materiais = QtWidgets.QListWidget()

        # Populando a ListBox com a lista "ambientes" da janela principal
        self.listbox_materiais.addItems(materiais_dict)

        # Conectando o sinal de clique do item da ListBox
        self.listbox_materiais.itemClicked.connect(self.itemClicked)



        # Parte esquerda: texto "botões" e tabela para coordenadas
        left_panel = QtWidgets.QVBoxLayout()
    
        self.layout.addLayout(left_panel, 0, 5, 8,1)

        # Adicionando a ListBox ao painel esquerdo
        left_panel.addWidget(self.listbox_materiais)


    def itemClicked(self, item):
        # Obtendo o índice do item clicado
        index = self.listbox_materiais.currentIndex().row()

        # Obtendo o nome do item clicado
        self.conteudo_str = self.listbox_materiais.item(index).text()
        
        itens = self.conteudo_str.split("=")[1].split(",")
        dicionario = {}
        key_value = self.conteudo_str.split("=")[1].split(",")
        for v in key_value:
            aux = v.split(":")
            try:
                dicionario[aux[0].strip()] = aux[1].strip()
            except:
                None
        if("tipo" in dicionario):
            self.tipoItem = dicionario["tipo"]
            if(self.tipoItem == "J"):
                self.b1.setChecked(True)
                self.tipoItem = "janela"
                self.SHGC = dicionario["SHGC"]
                self.U = dicionario["U"]
                self.largura = dicionario["largura"]
                self.altura = dicionario["altura"]
                self.textbox_label_k.setEnabled(False)
                self.textbox_label_k.setText("0")
                self.textbox_label_U.setText(str(self.U))
                self.textbox_label_U.setEnabled(True)

                self.textbox_label_SHGC.setText(str(self.SHGC))
                self.textbox_label_largura.setText(str(self.largura))
                self.textbox_label_altura.setText(str(self.altura))
                
            if(self.tipoItem == "P"):
                self.tipoItem = "porta"
                self.b2.setChecked(True)
                self.SHGC = dicionario["cor"]
                self.largura = dicionario["largura"]
                self.altura = dicionario["altura"]
                self.textbox_label_k.setEnabled(True)
                self.textbox_label_SHGC.setText(str(self.SHGC))
                self.textbox_label_U.setEnabled(False)
                self.textbox_label_U.setText("")
                self.textbox_label_largura.setText(str(self.largura))
                self.textbox_label_altura.setText(str(self.altura))   
                        
        if("k" in dicionario):
            self.k = dicionario["k"]
            self.textbox_label_k.setText(self.k)
        if("espessura" in dicionario):
            self.espessura = dicionario["espessura"]
            self.textbox_label_espessura.setText(self.espessura)
            

        print(dicionario)


        #lista_ambientes = self.ambientes[self.andar]
        #self.listbox_ambientes.clear()
        #self.listbox_ambientes.addItems(lista_ambientes)
        # Imprimindo o índice e o nome do item no console
        #print(f"Índice: {index}, Nome: {self.andar}")


    def btnstate(self,b):
	
      if b.text() == self.textos_json["janela"]:
        if b.isChecked() == True:
            self.tipoItem = "janela"
            self.label_SHGC.setEnabled(True)
            self.textbox_label_k.setText("")
            self.textbox_label_k.setEnabled(False)
            self.textbox_label_k.setVisible(False)
            self.label_k.setVisible(False)
            self.textbox_label_SHGC.setText(str(self.SHGC))
            self.textbox_label_SHGC.setEnabled(True)
            self.label_SHGC.setText("SHGC:")
            self.textbox_label_U.setEnabled(True)
            self.label_U.setVisible(True)
            self.textbox_label_U.setVisible(True)
            try:
                self.textbox_label_SHGC.setVisible(True)
                self.combobox_cor.setVisible(False)
            except:
                None
            
      if b.text() == self.textos_json["porta"]:
        if b.isChecked() == True:
            self.tipoItem = "porta"
            self.label_SHGC.setEnabled(True)

            self.textbox_label_k.setEnabled(True)
            self.textbox_label_k.setVisible(True)
            self.textbox_label_k.setText(str(self.k))
            self.label_k.setVisible(True)
            self.textbox_label_SHGC.setText("")
            self.textbox_label_SHGC.setEnabled(True)
            self.label_SHGC.setText(self.textos_json["cor"])
            self.textbox_label_U.setEnabled(False)
            self.textbox_label_U.setText("")
            self.label_U.setVisible(False)
            self.textbox_label_U.setVisible(False)
            try:
                self.textbox_label_SHGC.setVisible(False)
                self.combobox_cor.setVisible(True)
            except:
                None
        

        
    def salvar(self):
        if (self.tipoItem == "janela"):
            self.SHGC = self.textbox_label_SHGC.text()
        if (self.tipoItem == "porta"):
            self.SHGC = self.combobox_cor.currentText()
        
        try:
            self.largura = self.textbox_label_largura.text()
            self.altura = self.textbox_label_altura.text()
            self.espessura = self.textbox_label_espessura.text()
            self.k = self.textbox_label_k.text()
            self.U = self.textbox_label_U.text()
            if (self.tipoItem == "janela"):
                float(self.textbox_label_SHGC.text())
                float(self.U)
            if (self.tipoItem == "porta"):
                self.U = "0"
                float(self.k)
            float(self.largura)
            float(self.altura)
            float(self.espessura)
            
            verificar_entradas = None
            if(self.tipoItem=="janela"):
                verificar_entradas = matematica.verificar_entradas_numeros_e_vazias([str(self.SHGC), str(self.largura), str(self.altura), str(self.espessura), str(self.k), str(self.U)])
            if(self.tipoItem=="porta"):
                
                verificar_entradas = matematica.verificar_entradas_numeros_e_vazias([str(self.largura), str(self.altura), str(self.espessura), str(self.k), str(self.U)])
            if(verificar_entradas==True):
                # Emitir sinal com os valores atualizados
                self.valores_salvos.emit(str(self.SHGC), str(self.largura), str(self.altura), str(self.tipoItem), str(self.espessura), str(self.k), str(self.U), str(self.UouSHGC))
                # Fechando a janela
                self.close()
            else:
                msg_box = QMessageBox()
                msg_box.setIcon(QMessageBox.Information)
                msg_box.setText("Esta é uma mensagem de aviso.")
                msg_box.setWindowTitle("Aviso")
                msg_box.setStandardButtons(QMessageBox.Ok)
                msg_box.exec_()
        except:
            QtWidgets.QMessageBox.information(self, self.textos_json["erro"], self.textos_json["erro1"])


class TelaConfigurarSchedule(QDialog):
    valores_salvos = pyqtSignal(QtWidgets.QTableWidget)  # Sinal personalizado

    def __init__(self, table_cargas: QtWidgets.QTableWidget):
        # Inicializa a área de desenho
        super().__init__()
        self.setWindowTitle("Cargas Térmicas")
        self.table_cargas = table_cargas
        self.setFixedSize(900, 900)

        # Configurando o layout de grade
        layout = QtWidgets.QGridLayout()
        self.setLayout(layout)

        # Parte esquerda: texto "botões" e tabela para coordenadas
        left_panel = QtWidgets.QVBoxLayout()
        layout.addLayout(left_panel, 0, 0)

        # Adicionando a ListBox ao painel esquerdo
        left_panel.addWidget(self.table_cargas)

        # Criando a região em branco com horas
        self.horarios = Horarios(self)
        layout.addWidget(self.horarios, 0, 1)


        # Construindo a tabela
        botao_Adicionar_Equipamento = QtWidgets.QPushButton("Adicionar ao Schedule", self)
        botao_Adicionar_Equipamento.clicked.connect(self.adicionar_equipamento)
        left_panel.addWidget(botao_Adicionar_Equipamento)







    def adicionar_equipamento(self):
        try:
            selected_row = self.table_cargas.currentRow()
            ambiente = self.table_cargas.item(selected_row, 6).text()
            self.table_paredes.setItem(selected_row,6,QtWidgets.QTableWidgetItem(str(6)))
            self.nova_janela = TelaAdicionarEquipamento(self.table_cargas, ambiente, self.andar)
            self.nova_janela.show()
        except:
            print("ERRO EM -adicionar_equipamento-")


class Horarios(QtWidgets.QWidget):
    def __init__(self, parent):
        # Inicializa a área de desenho
        super().__init__(parent)

    def paintEvent(self, event):
        """
        Cria uma região em branco com as horas do dia.

        Retorna:
            QtWidgets.QWidget: Região em branco com horas.
        """
        qp = QtGui.QPainter(self)

        qp.setBrush(QtCore.Qt.white)  # Define a cor de fundo branca
        qp.drawRect(self.rect())

  

        


        #desenha a grade
        #define os offset das linhas da grade        
        self.pen_grade = QtGui.QPen()
        self.pen_grade.setWidth(1)
        qp.setPen(self.pen_grade)

        #linhas horizontais
        altura_linha = int(self.height()/26)
        for y in range(25):
            qp.drawLine(0, y*altura_linha , self.width(), y*altura_linha )
            qp.drawText(5, y*altura_linha  , str(y))



class TelaConfigurarParedes_e_Andares(QDialog):
    valores_salvos = pyqtSignal(dict, float, int)  # Sinal personalizado

    def __init__(self,  paredes_dados, paredes_default, pé_direito, andar_terreo):
        super().__init__()

        self.andar_terreo = int(andar_terreo)

        self.setWindowTitle("Configurações da edificação")
        self.paredes_dados = paredes_dados
        self.paredes_default = paredes_default
        self.pé_direito = pé_direito
        self.paredes_internas = self.paredes_default["paredes_internas"]
        self.paredes_externas = self.paredes_default["paredes_externas"]
        self.divisórias = self.paredes_default["divisorias"]
        self.interaces_horizontais = self.paredes_default["interfaces_horizontais"]

        self.classes = ["paredes_externas", "paredes_internas", "interfaces_horizontais"]   



        # Layout
        layout = QtWidgets.QGridLayout()
        self.setLayout(layout)

        self.label_material = QtWidgets.QLabel("Material")
        self.label_espessura = QtWidgets.QLabel("Espessura[m]")
        self.label_cor = QtWidgets.QLabel("Cor")
        self.label_k = QtWidgets.QLabel("k [W/m.k]")
        self.label_pé_direito = QtWidgets.QLabel("Pé esquerdo [m] (Soma do\n pé direito com espessura da lage e teto):")


        self.textbox_pé_direito = QtWidgets.QLineEdit()
        self.textbox_pé_direito.setText(str(self.pé_direito))
        self.label_terreo = QtWidgets.QLabel("Térreo: ")
        self.andarSpinBox = QtWidgets.QSpinBox()
        self.andarSpinBox.setValue(self.andar_terreo)
        self.andarSpinBox.valueChanged.connect(self.andarSpinBoxEvent)
        # Adicionando widgets ao layout
        layout.addWidget(self.label_pé_direito, 0, 0)
        layout.addWidget(self.textbox_pé_direito, 0, 1)
        layout.addWidget(self.label_terreo, 0, 2)
        layout.addWidget(self.andarSpinBox, 0, 3)
        layout.addWidget(self.label_material, 1, 1)
        layout.addWidget(self.label_espessura, 1, 2)
        layout.addWidget(self.label_cor, 1, 3)
        layout.addWidget(self.label_k, 1, 4)
        self.itens = []
        i = 2
        for classe in self.classes:
            # Criando widgets
            label_parede_externa = QtWidgets.QLabel(classe)
            combobox_material_externa = QtWidgets.QComboBox()
            lista_paredes_externas = list(paredes_dados[classe].keys())
            lista_paredes_externas.append("personalizado")
            combobox_material_externa.addItems(lista_paredes_externas)
            combobox_material_externa.setCurrentText(paredes_default[classe]["nome"]) 
            textbox_parede_externa_espessura = QtWidgets.QLineEdit()
            textbox_parede_externa_espessura.setText(str(paredes_default[classe]["espessura"]))
            combobox_parede_externa_cor = QtWidgets.QComboBox()
            combobox_parede_externa_cor.addItems(parametros.cores_paredes_list)
            combobox_parede_externa_cor.setCurrentText(str(paredes_default[classe]["cor"]))        
            textbox_parede_externa_k = QtWidgets.QLineEdit()
            textbox_parede_externa_k.setText(str(paredes_default[classe]["k"]))  
            layout.addWidget(label_parede_externa, i, 0)
            layout.addWidget(combobox_material_externa, i, 1)
            layout.addWidget(textbox_parede_externa_espessura, i, 2)
            layout.addWidget(combobox_parede_externa_cor, i, 3)
            layout.addWidget(textbox_parede_externa_k, i, 4)
            combobox_material_externa.currentIndexChanged.connect(lambda: self.comboboxChanged(str(classe)))
            item = [label_parede_externa, combobox_material_externa, textbox_parede_externa_espessura, combobox_parede_externa_cor, textbox_parede_externa_k]
            self.itens.append(item)
            i+=1


        self.botao_salvar = QtWidgets.QPushButton("Salvar")






        # Conectando sinais
        self.botao_salvar.clicked.connect(self.salvar)
        layout.addWidget(self.botao_salvar)

    def andarSpinBoxEvent(self):
        self.andar_terreo = int(self.andarSpinBox.value())
        

    def comboboxChanged(self, arg):
        string = self.itens[0][1].currentText()
        if(string!="personalizado"):
            self.itens[0][2].setText(str(self.paredes_dados["paredes_externas"][string]["espessura"]))
            self.itens[0][3].setCurrentText(str(self.paredes_dados["paredes_externas"][string]["cor"]))   
            self.itens[0][4].setText(str(self.paredes_dados["paredes_externas"][string]["k"]))   
    

        string = self.itens[1][1].currentText()
        if(string!="personalizado"):
            self.itens[1][2].setText(str(self.paredes_dados["paredes_internas"][string]["espessura"]))
            self.itens[1][3].setCurrentText(str(self.paredes_dados["paredes_internas"][string]["cor"]))   
            self.itens[1][4].setText(str(self.paredes_dados["paredes_internas"][string]["k"]))    

        string = self.itens[2][1].currentText()
        if(string!="personalizado"):
            self.itens[2][2].setText(str(self.paredes_dados["interfaces_horizontais"][string]["espessura"]))
            self.itens[2][4].setText(str(self.paredes_dados["interfaces_horizontais"][string]["k"]))    

    def salvar(self):
        for item in self.itens:
            classe = item[0].text()
            nome = item[1].currentText()
            espessura = item[2].text()
            cor = item[3].currentText()
            k = item[4].text()
            self.paredes_default[classe]["nome"] = nome
            self.paredes_default[classe]["espessura"] =  float(espessura)
            self.paredes_default[classe]["cor"] =  cor
            self.paredes_default[classe]["k"] = float(k)
            self.pé_direito = float(self.textbox_pé_direito.text())


        # Emitir sinal com os valores atualizados
        self.valores_salvos.emit(self.paredes_default, self.pé_direito, self.andar_terreo)

        # Fechando a janela
        self.close()


class TelaConfiguração(QDialog):
    def __init__(self):
        super().__init__()
        self.lang = None
        with open("config/interface.txt", "r") as f:
            lines = f.readlines()
            for line in lines:
                if("lang=" in line):
                    self.lang = line.split("=")[1].strip()
            
        layout = QtWidgets.QGridLayout()
        self.setLayout(layout)
        self.label_linguagem = QtWidgets.QLabel("linguagem: ")
        linguagens = ["en","pt"]
        self.combobox_linguagem = QtWidgets.QComboBox()
        self.combobox_linguagem.addItems(linguagens)
        self.combobox_linguagem.setCurrentText(self.lang) 
        layout.addWidget(self.label_linguagem,0,0)
        layout.addWidget(self.combobox_linguagem,0,1)
        self.combobox_linguagem.currentIndexChanged.connect(self.comboboxChanged)

    def comboboxChanged(self):
        nova_lang = self.combobox_linguagem.currentText()
        if(nova_lang != self.lang):
            data = None
            with open('config/interface.txt', 'r') as file:
                data = file.readlines()
            i = 0
            for string in data:
                if("lang=" in string):
                    data[i] = "lang=" + nova_lang +"\n"
                i+=1

            with open("config/interface.txt", "w") as file:
                file.writelines( data )

            self.lang = nova_lang
            if(nova_lang == "pt"):
                QtWidgets.QMessageBox.information(self, "Aviso", "Reinicie o programa para aplicar a mudança de linguagem.")
            if(nova_lang == "en"):
                QtWidgets.QMessageBox.information(self, "Info", "Restart the program to update the program language.")



