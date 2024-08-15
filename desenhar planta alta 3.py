# encoding: utf-8
# encoding: iso-8859-1
# encoding: win-1252
print("Iniciando RefrigerationStudio.")

import sys
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtGui import QTransform, QColor
print("Bibliotecas gráficas carregadas.")
import matplotlib.pyplot as plt
print("Matplotlib carregado.")
import random
import arredondamentos
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow
from shapely.geometry import Polygon, MultiPolygon
print("Módulo de operações geometricas carregado.")
import eventosTabela
import contorno
import geometria
from PyQt5.QtWidgets import QMenuBar, QDialog, QMessageBox
from PyQt5.QtGui import QIcon
import tkinter as tk
from tkinter import filedialog
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QAction, QFileDialog, QWidget, QToolBar, QPushButton
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
import leitor_log

texto_interface_dict = {}
idioma = parametros.linguagem()
# Opening JSON file
with open('data/interface.json', encoding='utf8') as json_file:
    data = json.load(json_file)
    texto_interface_dict = data[idioma]

def texto_interface (chave):
    string =  texto_interface_dict[chave]
    return string
     

debug = False
plotar_discretização_ambientes = False

#liga e desliga o modo de arrastar as figuras
arrastar_ligado = False

converter_retangulo_p_polygono = True

# Inicializa os valores de x, y e zoom
velocidade_scroll_seta = 5 #px
x_value = 0
y_value = 0
zoom = 1
scroll_zoom = 0
escala_original = 100  # px/metro
escala = int(escala_original)  # px/metro
resolução_arredondamento_ = 0.1
resolução_arredondamento = escala_original * zoom * resolução_arredondamento_
modo_escolhido = "retângulo"  # Modo inicial
numero_colunas = 9
#guarda as coordenadas da linha90g até virar um poligono, depois são apagadas
coordenadas_linha90g = []
andar_atual = "0"
andar_max = 0



cores_interface_desenho = []

class Transformações():
    #offset_value pode ser o x_value ou y_value
    def AjusteCoordenada(numero_original, offset_value):
        global zoom, escala
        numero_transformado = int(zoom * (int(float(numero_original) * escala) - offset_value))
        return numero_transformado
    
    def Offsets_X_Y():
        global y_value, x_value, zoom
        offsetLinhaVertical = x_value * zoom
        offsetLinhaHorizontal = y_value * zoom
        return (offsetLinhaVertical, offsetLinhaHorizontal)

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        global debug, cores_interface_desenho
        self.limpar_temp() #limpa tudo que for temporário
        #configura os temas
        #qdarktheme.setup_theme() # dark
        qdarktheme.setup_theme() #claro
        tema_pasta = "config/interface.txt"
        if tema_pasta:
            with open(tema_pasta, 'r') as file:
                text = file.read()
                linhas = text.split("\n")
                for linha in linhas:
                    if("darktheme" in linha):
                        if "True" in linha:
                            qdarktheme.setup_theme()
                            cores_interface_desenho = [QtGui.QColor("darkGray"), QtGui.QColor("green")]
                        else:
                            qdarktheme.setup_theme("light")
                    if("debug" in linha and "True" in linha):
                        debug = True
        self.CriarInterfaces()       


    def CriarInterfaces(self):
        # Crie um widget central
        self.central_widget = MyWidget()
        # Defina o widget central da janela principal
        self.setCentralWidget(self.central_widget)
        self._createActions()
        self._createMenuBar()
        self._createToolBars()




    #posso criar botões usando isso
    def _createToolBars(self):
        global debug
        # File toolbar
        fileToolBar = self.addToolBar("Arquivos")
        fileToolBar.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        self.importar_autocad_action = QtWidgets.QAction(QIcon('icons/import_CAD.png'),"Importar", self)
        self.importar_autocad_action.triggered.connect(lambda: self.ImportarAutocad())
        fileToolBar.addAction(self.importar_autocad_action)
        fileToolBar.addAction(self.novo_arquivoAction)
        fileToolBar.addAction(self.carregar_arquivoAction)
        fileToolBar.addAction(self.salvar_arquivoAction)
        self.novo_arquivoAction.triggered.connect(self.novo_arquivo)
        self.salvar_arquivoAction.triggered.connect(self.salvar_arquivo)
        self.carregar_arquivoAction.triggered.connect(self.carregar_arquivo)

        #toolbar de comandos de desenho
        desenhoToolBar = self.addToolBar("Ferramentas de Desenho")
        desenhoToolBar.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)        

        #titulo da linha da barra para simulação
        self.desenho_label = QtWidgets.QLabel(texto_interface("desenho"))
        self.desenho_label.setStyleSheet("background-color: white") 
        # Adiciona o rótulo à barra de ferramentas de operações
        desenhoToolBar.addWidget(self.desenho_label)

        # selecionar 
        self.selecionarAction = QtWidgets.QAction(QIcon('icons/selecionar3.png'),texto_interface("selecionar"), self)
        self.selecionarAction.triggered.connect(lambda: self.central_widget.atualizar_modo("selecionar"))
        desenhoToolBar.addAction(self.selecionarAction)

        # arrastar
        self.arrastarAction = QtWidgets.QAction(QIcon('icons/selecionar2.png'),texto_interface("arrastar"), self)
        self.arrastarAction.triggered.connect(lambda: self.central_widget.atualizar_modo("arrastar"))
        desenhoToolBar.addAction(self.arrastarAction)

        # alterar poligono
        if(debug==True):
            self.alterar_poligonoAction = QtWidgets.QAction(QIcon('icons/alterar.png'),texto_interface("alterar_poligono"), self)
            self.alterar_poligonoAction.triggered.connect(lambda: self.central_widget.atualizar_modo("alterar"))
            desenhoToolBar.addAction(self.alterar_poligonoAction)

        # linhas
        self.criar_linhasAction = QtWidgets.QAction(QIcon('icons/linha.png'),texto_interface("linha"), self)
        self.criar_linhasAction.triggered.connect(lambda: self.central_widget.atualizar_modo("linha"))
        desenhoToolBar.addAction(self.criar_linhasAction)

        # Botão "Modo Retângulo"
        self.retanguloAction = QtWidgets.QAction(QIcon('icons/retangulo.png'), texto_interface("retangulo"), self)
        self.retanguloAction.triggered.connect(lambda: self.central_widget.atualizar_modo("retângulo"))
        desenhoToolBar.addAction(self.retanguloAction)

        # Botão "Modo Unir"
        self.unirAction = QtWidgets.QAction(QIcon('icons/union1.png'), texto_interface("união"), self)
        self.unirAction.triggered.connect(lambda: self.central_widget.atualizar_modo("unir"))
        desenhoToolBar.addAction(self.unirAction)

        # Botão "Modo Unir"
        self.reguaAction = QtWidgets.QAction(QIcon('icons/regua.png'), texto_interface("régua"), self)
        self.reguaAction.triggered.connect(lambda: self.central_widget.atualizar_modo("régua"))
        desenhoToolBar.addAction(self.reguaAction)

        # Botão "Modo Arrastar"
        if(debug==True):
            self.arrastarCheckbox = QtWidgets.QCheckBox("Arrastar Polígonos", self)
            self.arrastarCheckbox.clicked.connect(lambda: self.central_widget.modo_arrastar_atualizar())
            desenhoToolBar.addWidget(self.arrastarCheckbox)
        
        #ANDAR
        self.andarLabel = QtWidgets.QLabel("Andar:")
        desenhoToolBar.addWidget(self.andarLabel)
        self.andarSpinBox = QtWidgets.QSpinBox()
        self.andarSpinBox.setFocusPolicy(Qt.NoFocus)
        self.andarSpinBox.valueChanged.connect(self.andarSpinBoxEvent)
        desenhoToolBar.addWidget(self.andarSpinBox)

        #cria uma nova linha
        #self.addToolBarBreak()
        #toolbar de operações
        elementosToolBar = self.addToolBar("Elementos Construtivos")
        #titulo da linha da barra para elementos
        self.elementos_label = QtWidgets.QLabel(texto_interface("construção"))
        self.elementos_label.setStyleSheet("background-color: white") 
        # Adiciona o rótulo à barra de ferramentas de elementos
        elementosToolBar.addWidget(self.elementos_label)
        elementosToolBar.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)

        # botão de Janela
        self.janelaAction = QtWidgets.QAction(QIcon('icons/janela_porta.png'),texto_interface("janela_porta"), self)
        self.janelaAction.triggered.connect(self.central_widget.janelaButton)
        elementosToolBar.addAction(self.janelaAction)

        # botão de configurações de andar
        self.configurarAndaresAction = QtWidgets.QAction(QIcon('icons/parede_andar.png'),texto_interface("parede_andar"), self)
        self.configurarAndaresAction.triggered.connect(self.central_widget.ConfigurarParedes_e_Andares)
        self.configurarAndaresAction.setIconText("Parede/Andar")
        elementosToolBar.addAction(self.configurarAndaresAction)

        #cria uma nova linha
        self.addToolBarBreak()
        cargasToolBar = self.addToolBar(texto_interface("cargas"))
        cargasToolBar.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        #titulo da linha da barra para simulação
        self.cargasToolBar_label = QtWidgets.QLabel("CARGAS")
        self.cargasToolBar_label.setStyleSheet("background-color: white") 
        cargasToolBar.addWidget(self.cargasToolBar_label)
        # botão de cargas térmicas
        self.cargasTermicasAction = QtWidgets.QAction(QIcon('icons/carga_termica.png'), texto_interface("cargas"), self)
        self.cargasTermicasAction.triggered.connect(self.central_widget.GerenciarCargasTermicas)
        cargasToolBar.addAction(self.cargasTermicasAction)

        # botão de Schedule
        self.configurarScheduleTestection = QtWidgets.QAction(QIcon('icons/schedule.png'),texto_interface("schedule"), self)
        self.configurarScheduleTestection.triggered.connect(self.central_widget.ScheduleTeste)
        cargasToolBar.addAction(self.configurarScheduleTestection)

        # botão de condições climaticas e geograficas
        self.configurarClimaGeoAction = QtWidgets.QAction(QIcon('icons/map.png'), texto_interface("clima_cond_geográficas"), self)
        self.configurarClimaGeoAction.triggered.connect(self.central_widget.configurarClimaGeo)
        cargasToolBar.addAction(self.configurarClimaGeoAction)

        # botão de HVAC
        self.configurarHVACAction = QtWidgets.QAction(QIcon('icons/hvac.png'), texto_interface("config_hvac"), self)
        self.configurarHVACAction.triggered.connect(self.central_widget.configurarHVAC)
        cargasToolBar.addAction(self.configurarHVACAction)

        #toolbar de operações
        simulaçãoToolBar = self.addToolBar(texto_interface("simulação"))
        simulaçãoToolBar.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        #titulo da linha da barra para simulação
        self.simulação_label = QtWidgets.QLabel(texto_interface("simulação"))
        self.simulação_label.setStyleSheet("background-color: white")  #background-color: lightgreen
        # Adiciona o rótulo à barra de ferramentas de operações
        simulaçãoToolBar.addWidget(self.simulação_label)

        # botão de gerar paredes versão 2
        self.autoGerenciarParedes2 = QtWidgets.QAction(QIcon('icons/contorno.png'), texto_interface("gerar_c_de_contorno"), self)
        self.autoGerenciarParedes2.triggered.connect(self.central_widget.AutoRecriarParedes2)
        simulaçãoToolBar.addAction(self.autoGerenciarParedes2)

        # botão de simular
        self.simularAction = QtWidgets.QAction(QIcon('icons/graph.png'), texto_interface("simular"), self)
        self.simularAction.triggered.connect(self.central_widget.Simular)
        simulaçãoToolBar.addAction(self.simularAction)

        if(debug == True):
                # botão de discretizar
            self.discretizarAction = QtWidgets.QAction("Discretizar (debug)", self)
            self.discretizarAction.triggered.connect(self.central_widget.discretizar)
            simulaçãoToolBar.addAction(self.discretizarAction)
        
        #toolbar de Configurações
        configuraçõesToolBar = self.addToolBar("Configurações")
        configuraçõesToolBar.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        #titulo da linha da barra para simulação
        self.configuraçõesToolBar = QtWidgets.QLabel(texto_interface("configurar"))
        self.configuraçõesToolBar.setStyleSheet("background-color: white")  #background-color: lightgreen
        # botão de configurações
        self.configurarAction = QtWidgets.QAction(QIcon('icons/config.png'), texto_interface("configurar"), self)
        self.configurarAction.triggered.connect(self.central_widget.Configurar)
        configuraçõesToolBar.addAction(self.configurarAction)

    def _createActions(self):
        # Creating action using the first constructor
        self.newAction = QtWidgets.QAction(self)
        self.newAction.setText("New")
        # Creating actions using the second constructor
        self.novo_arquivoAction = QtWidgets.QAction(QIcon('icons/new.png'), texto_interface("novo"), self)
        self.salvar_arquivoAction = QtWidgets.QAction(QIcon('icons/save.png'), texto_interface("salvar"), self)
        self.carregar_arquivoAction = QtWidgets.QAction(QIcon('icons/load.png'), texto_interface("carregar"), self)
        self.helpContentAction = QtWidgets.QAction("Help Content", self)
        self.aboutAction = QtWidgets.QAction("About", self)

    def _createMenuBar(self):
        menuBar = self.menuBar()
        # File menu
        fileMenu = QtWidgets.QMenu("File", self)
        menuBar.addMenu(fileMenu)
        fileMenu.addAction(self.novo_arquivoAction)
        fileMenu.addAction(self.carregar_arquivoAction)
        fileMenu.addAction(self.salvar_arquivoAction)
        # fileMenu.addAction(self.exitAction)
        # Edit menu
        editMenu = menuBar.addMenu("&Edit")
        # Help menu
        helpMenu = menuBar.addMenu(QIcon(":help-content.svg"), "&Help")
        helpMenu.addAction(self.helpContentAction)
        helpMenu.addAction(self.aboutAction)

    def andarSpinBoxEvent(self):
        global andar_atual, andar_max
        andar_atual = str(self.andarSpinBox.value())
        andar_max = max([int(andar_atual),andar_max])
        self.central_widget.ajustar_tamanho_listas()

    def ImportarAutocad(self):
        global escala
        self.novo_arquivo()
        importar_cad = leitor_log.ImportCad()
        fileName_txt, _ = QFileDialog.getOpenFileName(self, "importar", "", "Arquivos de log Autocad (*.log)")
        poligonos_não_processados, andares = importar_cad.main(fileName_txt)
        x_min,y_min = 1,1
        x_max,y_max = 500,500
        for poligono_com_andar in poligonos_não_processados:
            poligono = poligono_com_andar[0]
            print(str(poligono))
            poligono.insert(0, poligono[0])
            Z = poligono_com_andar[1]
            andar = andares[Z]
            cor = self.central_widget.gerar_cor()
            self.central_widget.drawing_area.QPoligono(poligono, cor, andar)
            for coord in poligono:
                if(coord[0]>x_max):
                    x_max = coord[0]
                if(coord[1]>y_max):
                    y_max = coord[1]
        continuar_afastar = True
        x_tela = 500
        y_tela = 500
        while(continuar_afastar == True):
            escala = escala / 2
            x_tela = x_tela*2
            y_tela = y_tela*2
            self.central_widget.update_labels()
            self.central_widget.atualizar()
            if(x_tela>x_max and y_tela>y_max):
                continuar_afastar = False

    def novo_arquivo(self):
        global x_value, y_value, zoom, escala
        x_value = 0
        y_value = 0
        zoom = 1
        escala = 100
        resposta = QMessageBox.question(
            None, "Confirmar Salvamento", "Deseja salvar estado atual?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if resposta == QMessageBox.Yes:
            self.central_widget.SalvarArquivo()
        self.central_widget.drawing_area.primeiro_ponto_poligono = []
        self.central_widget.drawing_area.begin = QtCore.QPoint()
        self.central_widget.drawing_area.begin =QtCore.QPoint()
        self.central_widget.drawing_area.begin_linha = QtCore.QPoint()
        self.central_widget.drawing_area.begin_sem_zoom = QtCore.QPoint()
        self.central_widget.drawing_area.end = QtCore.QPoint()            
        self.central_widget.limpar()
        self.central_widget.zerar_tabela()
        self.central_widget.COP = 3.5
        self.central_widget.classe_compressor ="inverter (controle proporcional)"
        self.central_widget.unidade = "W"
        self.central_widget.temperatura_desejada = 25
        self.central_widget.potencia_refrigeração = 0
        self.central_widget.horario_inicial_hora = 0
        self.central_widget.horario_inicial_min = 0
        self.central_widget.horario_final_hora = 24
        self.central_widget.horario_final_min = 0
        self.central_widget.latitude_graus = 0
        self.central_widget.ACH_troca_de_ar_h = 2.0
        [self.central_widget.paredes_dados, self.central_widget.paredes_default] = parametros.parametros_paredes()
        #começa a limpar o temp
        self.limpar_temp

    def limpar_temp(self):
        f = open('temp/arquivos_climaticos/config.txt', 'w')
        f.write(str("path=False"))
        f.close()
        
    def salvar_arquivo(self):
        self.central_widget.SalvarArquivo()
        pass

    def carregar_arquivo(self):
        self.central_widget.CarregarArquivo()
        pass

class MyWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Refrigeração")
        self.resize(800, 900)
        # Configurando o layout de grade
        layout = QtWidgets.QGridLayout()
        layout.setColumnMinimumWidth(0, 200) #largura mínima da primeira coluna em 200
        self.setLayout(layout)
        # Parte esquerda: texto "botões" e tabela para coordenadas
        left_panel = QtWidgets.QVBoxLayout()
        layout.addLayout(left_panel, 1, 0)
        label = QtWidgets.QLabel("Ambientes")
        label.setAlignment(QtCore.Qt.AlignCenter)
        left_panel.addWidget(label)
        # constroi a tabela
        self.ConstruirTabela()
        left_panel.addWidget(self.table)
        labelContorno = QtWidgets.QLabel("Condições de Contorno")
        labelContorno.setAlignment(QtCore.Qt.AlignCenter)
        left_panel.addWidget(labelContorno)
        #constroi a tabela de paredes
        self.ConstruirTabelaParedes()
        left_panel.addWidget(self.table_paredes)
        #constroi a tabela de limites horizontais
        self.ConstruirTabelaHorizontal()
        left_panel.addWidget(self.table_horizontal)

        #constroi a tabela de reguas
        self.ConstruirTabelaRegua()
        if(debug==True):
            left_panel.addWidget(self.table_reguas)

        #construir a tabela de envelopamento
        self.ConstruirTabelaJanelasPortas()
        left_panel.addWidget(self.table_janelas_portas)

        #constroi a tabela de cargas geradas porem não adiciona
        self.ConstruirTabelaCargasTermicas()





        # Parte direita: área de desenho de poligonos
        self.drawing_area = DrawingArea(self)
        layout.setColumnMinimumWidth(1, 600)  # Define a largura mínima da segunda coluna como 1000 pixels
        # Criar a toolbar
        toolbar_vistas = QToolBar()
        # seletor de vistas
        self.vista_ambiente_button = QtWidgets.QToolButton() 
        self.vista_ambiente_button.setToolTip("ambientes diferenciados")
        self.vista_ambiente_button.setIcon(QtGui.QIcon('icons/vista_ambientes.png'))
        self.vista_ambiente_button.setCheckable(True)
        self.vista_ambiente_button.click()
        self.vista_ambiente_button.toggled.connect(self.drawing_area.Vistas_ambientes)
        toolbar_vistas.addWidget(self.vista_ambiente_button) 
    
        self.vista_contornos_button = QtWidgets.QToolButton()
        self.vista_contornos_button.setToolTip("condições de contorno")
        self.vista_contornos_button.setIcon(QtGui.QIcon('icons/vista_contorno.png'))
        self.vista_contornos_button.setCheckable(True)
        self.vista_contornos_button.toggled.connect(self.drawing_area.Vistas_contonos)
        toolbar_vistas.addWidget(self.vista_contornos_button) 

        self.centralizar_vista_button = QtWidgets.QToolButton()
        self.centralizar_vista_button.setToolTip("centralizar")
        self.centralizar_vista_button.setIcon(QtGui.QIcon('icons/centralizar.png'))
        self.centralizar_vista_button.clicked.connect(self.drawing_area.Centralizar_Vista)
        toolbar_vistas.addWidget(self.centralizar_vista_button) 

        toolbar_vistas.setMaximumWidth(120)
        layout_drawing = QtWidgets.QGridLayout()
        layout_drawing.addWidget(toolbar_vistas,0,1)
        layout_drawing.addWidget(self.drawing_area,0,0,2,3)
        layout.addLayout(layout_drawing, 1,1)


        # Adicionando uma região de 30 pixels abaixo da área de desenho
        text_area = QtWidgets.QWidget()
        text_layout = QtWidgets.QHBoxLayout()
        text_area.setLayout(text_layout)
        layout.addWidget(text_area, 2, 1)

        # Adicionando o texto "x:y:"
        self.x_label = QtWidgets.QLabel("x:")
        text_layout.addWidget(self.x_label)

        self.y_label = QtWidgets.QLabel("y:")
        text_layout.addWidget(self.y_label)

        self.zoom_label = QtWidgets.QLabel("zoom:")
        text_layout.addWidget(self.zoom_label)

        self.escala_label = QtWidgets.QLabel("escala:")
        text_layout.addWidget(self.escala_label)

        self.medição_continua_checkbox = QtWidgets.QCheckBox("medição continua")
        self.medição_continua_checkbox.stateChanged.connect(self.medicao_continua_checkbox_changed)
        text_layout.addWidget(self.medição_continua_checkbox)
        
        self.snap_pontos_checkbox = QtWidgets.QCheckBox("snap")
        self.snap_pontos_checkbox.setChecked(True)
        self.snap_pontos_checkbox.stateChanged.connect(self.snap_checkbox_changed)
        text_layout.addWidget(self.snap_pontos_checkbox)


        self.update_labels()  # Atualiza os valores iniciais de x, y e zoom nos rótulos

        self.setGeometry(30, 30, 1200, 430)  # Ajusta a largura total para acomodar a tabela e a área de desenho

        self.potencia_refrigeração = 0
        self.classe_compressor ="inverter (controle ideal)"
        self.unidade = "W"
        self.COP = 3.5
        self.temperatura_desejada = 25 #funciona como limite superior
        self.temperatura_limite_inferior = 24 #devido a histerese 
        self.ACH_troca_de_ar_h = 2.0
        self.latitude_graus = 0
        self.metodo_calculo_temp_solo = "senoidal (comb.lin. solução dia + ano)"
        self.temp_solo_cte = 18
        self.angulo_N_geral = 0
        self.necessario_novas_CContorno = True
        self.horario_inicial_hora = 0
        self.horario_inicial_min = 0
        self.horario_final_hora = 24
        self.horario_final_min = 0
        [self.paredes_dados, self.paredes_default] = parametros.parametros_paredes()
        self.pé_direito = 2.7
        self.andar_terreo = 0
        self.tabs = QtWidgets.QTabWidget()

        self.show()

    def medicao_continua_checkbox_changed(self, int):
        if(self.medição_continua_checkbox.isChecked() == True):
            self.drawing_area.medição_continua = True

        else:
            self.drawing_area.medição_continua = False
            self.drawing_area.begin =QtCore.QPoint()
            self.drawing_area.begin_sem_zoom = QtCore.QPoint()
            self.drawing_area.end = QtCore.QPoint()
            self.drawing_area.primeiro_ponto_poligono = []

    def snap_checkbox_changed(self, int):
        if(self.snap_pontos_checkbox.isChecked() == True):
            self.drawing_area.snap = True

        else:
            self.drawing_area.snap = False



    def SalvarArquivo(self):
        nome_arquivo_climatico=None
        with open("temp/arquivos_climaticos/config.txt", "r") as f:
            lines = f.readlines()
            for line in lines:
                if("path=" in line):
                    nome_arquivo_climatico = line.split("=")[1].strip()
        if(nome_arquivo_climatico != "False"):
            conteudo_str = "@arquivo_epw@\n"
            conteudo_str += nome_arquivo_climatico + "\n"
            conteudo_str += "@fim@\n"
        else:
            conteudo_str = ""
        conteudo_str += "@ambientes@\n"
        conteudo_str += eventosTabela.ConteudosTabela_STR(self.table)
        conteudo_str += "@fim@\n"

        conteudo_str += "@paredes@\n"
        conteudo_str += eventosTabela.ConteudosTabela_STR(self.table_paredes)
        conteudo_str += "@fim@\n"

        conteudo_str += "@limites_horizontais@\n"
        conteudo_str += eventosTabela.ConteudosTabela_STR(self.table_horizontal)
        conteudo_str += "@fim@\n"

        conteudo_str += "@cargas@\n"
        conteudo_str += eventosTabela.ConteudosTabela_STR(self.table_cargas)
        conteudo_str += "@fim@\n"

        conteudo_str+= "@configuração HVAC@\n"
        conteudo_str+= "potencia_refrigeração=" + str(self.potencia_refrigeração) + "\n"
        conteudo_str+= "unidade=" + str(self.unidade) + "\n"
        conteudo_str+= "classe_compressor=" + self.classe_compressor + "\n"
        conteudo_str+= "COP=" + str(self.COP) + "\n"
        conteudo_str+= "Temp_alvo=" + str(self.temperatura_desejada) + "\n"
        conteudo_str+= "temperatura_limite_inferior=" + str (self.temperatura_limite_inferior) +"\n"
        conteudo_str+= "ACH=" + str(self.ACH_troca_de_ar_h) + "\n"
        conteudo_str+= "horario_inicial_hora=" + str(self.horario_inicial_hora) + "\n"
        conteudo_str+= "horario_inicial_min=" + str(self.horario_inicial_min) + "\n"
        conteudo_str+= "horario_final_hora=" + str(self.horario_final_hora) + "\n"
        conteudo_str+= "horario_final_min=" + str(self.horario_final_min) + "\n"


        conteudo_str += "@fim@\n"

        conteudo_str+= "@elementos@\n"
        conteudo_str+= eventosTabela.ConteudosTabela_STR(self.table_janelas_portas)
        conteudo_str += "@fim@\n"

        conteudo_str+= "@clima e geografia@\n"
        conteudo_str+= "latitude=" + str(self.latitude_graus) + "\n"
        conteudo_str+= "angulo_geral_norte=" + str(self.angulo_N_geral) + "\n"
        conteudo_str+= "metodo_calculo_temp_solo=" +str(self.metodo_calculo_temp_solo) + "\n"
        conteudo_str+= "temp_solo_cte=" + str(self.temp_solo_cte) + "\n"
        conteudo_str += "@fim@\n"

        conteudo_str+= "@paredes_default@\n"
        conteudo_str+= str(self.paredes_default) + "\n"
        conteudo_str += "@fim@\n"

        conteudo_str+= "@pe_direito@\n"
        conteudo_str+= str(self.pé_direito) + "\n"
        conteudo_str += "@fim@\n"

        conteudo_str+= "@necessario_novas_CContorno@\n"
        conteudo_str+= str(self.necessario_novas_CContorno) + "\n"
        conteudo_str += "@fim@\n"

        fileName_txt, _ = QFileDialog.getSaveFileName(self, "Salvar Arquivo", "", "Projeto de Refrig. (*.chu)")
        if(fileName_txt!=''):
            if fileName_txt:
                with open(fileName_txt, 'w') as file:
    
                    file.write(conteudo_str)
                file.close()
            nome_zip = fileName_txt

            caminho_novo = os.path.join(os.path.dirname(fileName_txt), "temp.chu")
            if os.path.exists(caminho_novo):
                os.remove(caminho_novo)

            os.rename(fileName_txt, caminho_novo)
            fileName_txt = caminho_novo

            caminho_arquivos = [fileName_txt,
                        "temp/arquivos_climaticos/" + nome_arquivo_climatico]
            if(nome_arquivo_climatico == "False"):
                caminho_arquivos = [fileName_txt]
            pasta_origem = os.path.dirname(caminho_arquivos[0])
            nome_arquivo_saida = os.path.join(pasta_origem, "temp/arquivos_compactados.chu")
            with zipfile.ZipFile(nome_zip, 'w') as zipf:
                for arquivo in caminho_arquivos:
                    zipf.write(arquivo, os.path.basename(arquivo))
            #apaga o resto do processo
            os.remove(fileName_txt)



    #transforma string para os dados das tables
    def Save_para_Table(self, linha, tabela_atualizada: QTableWidget):
        rowPosition = tabela_atualizada.rowCount()
        tabela_atualizada.insertRow(rowPosition)
        celulas = linha.split("&")
        i_cel = 0
        for celula in celulas:
            if("COMBOITEM/" in celula):
                conteudo = celula.split("COMBOITEM/")[1].split("/COMBOITEM")[0]
                escolhido_text = conteudo.split("Escolhido/")[1].split("/Escolhido")[0].strip()
                lista = ast.literal_eval(conteudo.split("ITEMS/")[1].split("/ITEMS")[0])
                lista_ = lista.copy()
                for item in lista:
                    lista_.append(item.strip())
                lista = lista_.copy()
                combobox = QtWidgets.QComboBox()
                combobox.addItems(lista)
                combobox.setCurrentText(escolhido_text)     
                tabela_atualizada.setCellWidget(rowPosition, i_cel, combobox)
            else:
                item = QtWidgets.QTableWidgetItem(celula.strip())
                tabela_atualizada.setItem(rowPosition, i_cel, item)
            i_cel+=1
        return tabela_atualizada

    def CarregarArquivo(self):
        global  x_value, y_value, andar_max
        fileName, _ = QFileDialog.getOpenFileName(self, "Abrir Arquivo", "", "Projeto de Refrig. (*.chu)")
        if(fileName!=''):
            self.parent().novo_arquivo()
            self.limpar()
            pasta_destino = os.path.join(os.getcwd(), "temp")

            with zipfile.ZipFile(fileName, 'r') as zip_ref:
                zip_ref.extractall(pasta_destino)

            txt_temp_pasta = pasta_destino.replace("\\","/") + "/" + "temp.chu"
    #"D:/OneDrive/TCC/scripts/CAD V01/temp/temp.txt
            if txt_temp_pasta:
                with open(txt_temp_pasta, 'r') as file:
                    text = file.read()
                    linhas = text.split("\n")
                    estado_atual = ""
                    for linha in linhas:
                        if("@arquivo_epw@" in estado_atual and "@fim@" not in linha):
                            # Copiar o arquivo para a pasta "arquivo climatico"
                            import shutil
                            shutil.copy("temp/" + linha, "arquivos_climaticos")
                            with open("temp/arquivos_climaticos/config.txt", "a+") as arquivo:
                                valor = ""
                                arquivo.write(valor)
                                
                            arquivo.close()
                            with open("temp/arquivos_climaticos/config.txt", "w") as arquivo:
                                valor = "path="+linha.split("/")[-1]
                                arquivo.write(valor)
                                arquivo.close()
                            nome_arquivo = None


                            caminho = "temp/arquivos_climaticos/"+linha
                            with open(caminho, 'r') as f:
                                lines = f.readlines()
                                latitude = lines[0].split(",")[6]
                                self.latitude_graus = latitude

                        if("@ambientes@" in estado_atual and "@fim@" not in linha):
                            self.table = self.Save_para_Table(linha, self.table)

                        if("@paredes@" in estado_atual and "@fim@" not in linha):
                            self.table_paredes = self.Save_para_Table(linha, self.table_paredes)


                        if("@limites_horizontais@" in estado_atual and "@fim@" not in linha):
                            self.table_horizontal = self.Save_para_Table(linha, self.table_horizontal)


                        if("@cargas@" in estado_atual and "@fim@" not in linha and (linha!= "" and linha!= "\n" and linha != " ")):
                            self.table_cargas = self.Save_para_Table(linha, self.table_cargas)

                        if("@elementos@" in estado_atual and "@fim@" not in linha):
                            self.table_janelas_portas = self.Save_para_Table(linha, self.table_janelas_portas)

                        if("@paredes_default@" in estado_atual and "@fim@" not in linha):
                            self.paredes_default = ast.literal_eval(linha)

                        if("@pe_direito@" in estado_atual and "@fim@" not in linha):
                            self.pé = float(linha)

                        if("@necessario_novas_CContorno@"  in estado_atual and "@fim@" not in linha):
                            if(linha == "False"):
                                self.necessario_novas_CContorno = False
                            if(linha == "True"):
                                self.necessario_novas_CContorno = True

                        if("@configuração HVAC@" in estado_atual and "@fim@" not in linha):
                            if("potencia_refrigeração=" in linha):
                                self.potencia_refrigeração = float(linha.split("=")[1])
                            if("classe_compressor=" in linha):
                                self.classe_compressor = linha.split("=")[1]
                            if("unidade=" in linha):
                                self.unidade = linha.split("=")[1]
                            if("COP=" in linha):
                                self.COP = float(linha.split("=")[1])
                            if("Temp_alvo=" in linha):
                                self.temperatura_desejada = float(linha.split("=")[1])
                            if("temperatura_limite_inferior=" in linha):
                                self.temperatura_limite_inferior = float(linha.split("=")[1])
                            if("ACH=" in linha):
                                self.ACH_troca_de_ar_h = float(linha.split("=")[1])

                            if("horario_inicial_hora=" in linha):
                                if(len(linha.split("=")[1]) == 1):
                                    self.horario_inicial_hora = "0" + str(linha.split("=")[1])
                                else:
                                    self.horario_inicial_hora = str(linha.split("=")[1])
                            if("horario_inicial_min=" in linha):
                                if(len(linha.split("=")[1]) == 1):
                                    self.horario_inicial_min = "0" + str(linha.split("=")[1])
                                else:
                                    self.horario_inicial_min = str(linha.split("=")[1])
                         
                            if("horario_final_hora=" in linha):
                                if(len(linha.split("=")[1]) == 1):
                                    self.horario_final_hora = "0" + str(linha.split("=")[1])
                                else:
                                    self.horario_final_hora = str(linha.split("=")[1])
                            if("horario_final_min=" in linha):
                                if(len(linha.split("=")[1]) == 1):
                                    self.horario_final_min = "0" + str(linha.split("=")[1])
                                else:
                                    self.horario_final_min = str(linha.split("=")[1])
                                
                        if("@clima e geografia@" in estado_atual and "@fim@" not in linha):
                            if("angulo_geral_norte=" in linha):
                                self.angulo_N_geral = float(linha.split("=")[1])
                            if("latitude=" in linha):
                                self.latitude = float(linha.split("=")[1])
                            if("metodo_calculo_temp_solo=" in linha):
                                self.metodo_calculo_temp_solo = linha.split("=")[1]
                            if("temp_solo_cte="  in linha):
                                self.temp_solo_cte = float(linha.split("=")[1])
                                                        

                        if("@" in linha): #mantem o estado atualizado
                            estado_atual = linha
                        
            self.atualizar()
        
        tabela = eventosTabela.ConteudosTabela_ARR(self.table_cargas)
  
        #zera as anotações de cada ambiente
        i_andar = 0
        for andar in self.drawing_area.poligonos:
            i=0
            for poligono_, cor, nome_ambiente, dados_adicionais, buracos in self.drawing_area.poligonos[i_andar]:
                dados_adicionais["Ocupantes"] = 0
                dados_adicionais["Ocupantes_hora"] = []
                for i_ in range(25):
                    dados_adicionais["Ocupantes_hora"].append(0)
                self.drawing_area.poligonos[i_andar][i][3] = dados_adicionais 
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
                    for poligono_, cor, nome_ambiente, dados_adicionais, buracos in self.drawing_area.poligonos[andar]:
                        if(ambiente == nome_ambiente):
                            dados_adicionais["Ocupantes_hora"][hora] += quantidade
                            self.drawing_area.poligonos[andar][i][3] = dados_adicionais 
                        i+=1
        i=0
        try:
            for andar in range(andar_max):
                for poligono_, cor, nome_ambiente, dados_adicionais, buracos in self.drawing_area.poligonos[andar]:
                    dados_adicionais["Ocupantes"] = max(dados_adicionais["Ocupantes_hora"])
                    self.drawing_area.poligonos[andar][i][3] = dados_adicionais 
                    i+=1 
        except:
            None   




   
    #funções relativas a tabela
    def ConstruirTabela(self):
        header_colunas = ["Ambiente", "X1", "Y1", "X2", "Y2", "Cor", "Classe", "Vértices", "Andar", "Material", "ocupação máxima", "Área", "Tipo ambiente", "Hole"]
        # Cria e configura a tabela para mostrar as coordenadas dos retângulos
        self.table = QtWidgets.QTableWidget()
        self.table = eventosTabela.ConstruirTabela(self.table, self.keyPressEventTable, header_colunas)
        #esconde colunas
        if(debug == False):
            self.table.setColumnHidden(1, True)
            self.table.setColumnHidden(2, True)
            self.table.setColumnHidden(3, True)
            self.table.setColumnHidden(4, True)

        self.table.cellChanged.connect(self.on_cell_changed)

    def ConstruirTabelaParedes(self):
        header_colunas = ["Indice", "Interface", "Material", "Vértices", "C. de Contorno", "Andar", "Area", "orientação", "cor", "iluminação solar", "angulo H."]
        # Cria e configura a tabela para mostrar as coordenadas dos retângulos
        self.table_paredes = QtWidgets.QTableWidget()
        self.table_paredes = eventosTabela.ConstruirTabela(self.table_paredes, self.keyPressEventTable, header_colunas)
        #esconde colunas
        #self.table_paredes.setColumnHidden(1, True)
        self.table_paredes.cellChanged.connect(self.on_cell_changed)

    def ConstruirTabelaHorizontal(self):
        header_colunas = ["Indice", "Interface", "Classe", "Vértices", "C. de Contorno", "Interface Andar", "Área", "Hole", "Contato Superficial Direto", "cor", "andar pertecente"]
        # Cria e configura a tabela para mostrar as coordenadas dos retângulos
        self.table_horizontal = QtWidgets.QTableWidget()
        self.table_horizontal = eventosTabela.ConstruirTabela(self.table_horizontal, self.keyPressEventTable, header_colunas)
        #esconde colunas
        if(debug == False):
            self.table_horizontal.setColumnHidden(0, True)
            self.table_horizontal.setColumnHidden(3, True)
            self.table_horizontal.setColumnHidden(7, True)
            self.table_horizontal.setColumnHidden(8, True)
        self.table_horizontal.cellChanged.connect(self.on_cell_changed)

    def ConstruirTabelaCargasTermicas(self):
        header_colunas = ["Amb.", "Item", "Class", "Qntd.", "Andar",  "W. Dissipado", "De", "Até"]
        # Cria e configura a tabela para mostrar as coordenadas dos retângulos
        self.table_cargas = QtWidgets.QTableWidget()
        self.table_cargas = eventosTabela.ConstruirTabela(self.table_cargas, self.keyPressEventTable_Cargas, header_colunas)
    
    def ConstruirTabelaRegua(self):
        header_colunas = ["andar", "x1","y1","x2","y2"]
        # Cria e configura a tabela para mostrar as coordenadas dos retângulos
        self.table_reguas = QtWidgets.QTableWidget()
        self.table_reguas = eventosTabela.ConstruirTabela(self.table_reguas, self.keyPressEventTable, header_colunas)        
        #esconde colunas
        if(debug == False):
            self.table_reguas.setColumnHidden(1, True)
            self.table_reguas.setColumnHidden(2, True)
            self.table_reguas.setColumnHidden(3, True)
            self.table_reguas.setColumnHidden(4, True)



    def ConstruirTabelaJanelasPortas(self):
        header_colunas = ["andar", "x1","y1","x2","y2", "SHGC", "largura", "altura", "tipo", "angulo_rad", "interface", "material", "area", "angulo_Norte", "angulo_horizontal", "interno/ext", "U", "espessura(cm)", "k", "U ou SHGC"]
        # Cria e configura a tabela para mostrar as coordenadas dos retângulos
        #esconde colunas

        self.table_janelas_portas = QtWidgets.QTableWidget()
        self.table_janelas_portas = eventosTabela.ConstruirTabela(self.table_janelas_portas, self.keyPressEventTable_Elementos, header_colunas)
        self.table_janelas_portas.cellChanged.connect(self.on_cell_changed) 

        if(debug == False):
            self.table_janelas_portas.setColumnHidden(1, True)
            self.table_janelas_portas.setColumnHidden(2, True)
            self.table_janelas_portas.setColumnHidden(3, True)
            self.table_janelas_portas.setColumnHidden(4, True)
            self.table_janelas_portas.setColumnHidden(6, True)
            self.table_janelas_portas.setColumnHidden(7, True)
            self.table_janelas_portas.setColumnHidden(9, True)
            self.table_janelas_portas.setColumnHidden(13, True)
            self.table_janelas_portas.setColumnHidden(14, True)
            self.table_janelas_portas.setColumnHidden(15, True)

    def on_cell_changed(self, row, column):
        #print(f"Célula alterada: ({row}, {column})")
        self.necessario_novas_CContorno = True

    def zerar_tabela(self):
        self.table = eventosTabela.apagar_todas_linhas(self.table)
        self.table_paredes = eventosTabela.apagar_todas_linhas(self.table_paredes)
        self.table_horizontal = eventosTabela.apagar_todas_linhas(self.table_horizontal)
        self.table_cargas = eventosTabela.apagar_todas_linhas(self.table_cargas)
        self.table_janelas_portas = eventosTabela.apagar_todas_linhas(self.table_janelas_portas)
        self.table_reguas = eventosTabela.apagar_todas_linhas(self.table_reguas)

    def atualizar_tabela(self, poligono, cor, tipo, eventos_adicionais, andar, indice_desejado):
        # Atualiza a tabela com as coordenadas e cores do retângulo desenhado
        global escala, x_value, y_value
        self.table, self.table_paredes, self.table_horizontal, nome_novo_poligono = eventosTabela._atualizar_tabela(poligono, cor, tipo, self.table, escala, eventos_adicionais, andar, "automatico_parede", self.table_paredes,x_value ,y_value, self.table_horizontal, self.pé_direito, indice_desejado)
        return nome_novo_poligono

#ponto_central, angulo_rad, self.SHGC, self.largura, self.altura, tipo, espessura, k
    def atualizar_tabela_janelas_portas(self, ponto_central, angulo_rad, SHGC, largura, altura, tipo, espessura, k, U, UouSHGC):
#header_colunas = ["andar", "x1","y1","x2","y2", "SHGC", "largura", "altura", "tipo", "angulo_rad", "interface", "material", "area", "angulo_Norte", "angulo_horizontal", "interno/ext", "U", "espessura", "k", UouSHGC]
        global andar_atual
        global escala, x_value, y_value
        x = (ponto_central.x())/zoom/escala + x_value/escala
        y = (ponto_central.y())/zoom/escala + y_value/escala
        rowPosition = self.table_janelas_portas.rowCount()
        self.table_janelas_portas.insertRow(rowPosition)
        self.table_janelas_portas.setItem(rowPosition, 0, QtWidgets.QTableWidgetItem(str(andar_atual))) 
        self.table_janelas_portas.setItem(rowPosition, 1, QtWidgets.QTableWidgetItem(str(x))) 
        self.table_janelas_portas.setItem(rowPosition, 2, QtWidgets.QTableWidgetItem(str(y))) 
        self.table_janelas_portas.setItem(rowPosition, 3, QtWidgets.QTableWidgetItem(str(x))) 
        self.table_janelas_portas.setItem(rowPosition, 4, QtWidgets.QTableWidgetItem(str(y))) 
        self.table_janelas_portas.setItem(rowPosition, 5, QtWidgets.QTableWidgetItem(str(SHGC))) 
        self.table_janelas_portas.setItem(rowPosition, 6, QtWidgets.QTableWidgetItem(str(largura)))
        self.table_janelas_portas.setItem(rowPosition, 7, QtWidgets.QTableWidgetItem(str(altura)))        
        self.table_janelas_portas.setItem(rowPosition, 8, QtWidgets.QTableWidgetItem(str(tipo)))     
        self.table_janelas_portas.setItem(rowPosition, 9, QtWidgets.QTableWidgetItem(str(angulo_rad)))
        self.table_janelas_portas.setItem(rowPosition, 10, QtWidgets.QTableWidgetItem(str("N/A")))
        self.table_janelas_portas.setItem(rowPosition, 11, QtWidgets.QTableWidgetItem(str("N/A")))
        self.table_janelas_portas.setItem(rowPosition, 12, QtWidgets.QTableWidgetItem(str("N/A")))
        self.table_janelas_portas.setItem(rowPosition, 13, QtWidgets.QTableWidgetItem(str("N/A")))
        self.table_janelas_portas.setItem(rowPosition, 14, QtWidgets.QTableWidgetItem(str("N/A")))
        self.table_janelas_portas.setItem(rowPosition, 15, QtWidgets.QTableWidgetItem(str("N/A")))
        self.table_janelas_portas.setItem(rowPosition, 16, QtWidgets.QTableWidgetItem(str(U)))
        self.table_janelas_portas.setItem(rowPosition, 17, QtWidgets.QTableWidgetItem(str(espessura)))
        self.table_janelas_portas.setItem(rowPosition, 18, QtWidgets.QTableWidgetItem(str(k)))
        self.table_janelas_portas.setItem(rowPosition, 19, QtWidgets.QTableWidgetItem(str(UouSHGC)))




    def mudar_coordenadas_ambiente(self, i_ambiente, delta_x, delta_y, delta_x_pixels, delta_y_pixels, andar):
        None
        self.table = eventosTabela.mudar_coordenadas_ambiente(self.table, i_ambiente, delta_x, delta_y)

        
        #retangulo = QtCore.QRect(x1, y1, w, h)
        
        
        

    def update_labels(self):
        # Atualiza os rótulos com os valores atuais de x, y e zoom
        global x_value, y_value, zoom, escala
        self.x_label.setText(f"x: {x_value}")
        self.y_label.setText(f"y: {y_value}")
        self.zoom_label.setText(f"zoom: {zoom * 100}%")
        self.escala_label.setText(f"escala: {escala}")



    def redesenhar_quadro(self):
        # Função para redesenhar o quadro, não implementada
        QtWidgets.QMessageBox.information(self, 'Redesenhado', 'O quadro foi redesenhado')



    def atualizar(self):
        # Atualiza os retângulos na tela com base nos valores da tabela
        global escala
        tabela_arr = eventosTabela.ConteudosTabela_ARR(self.table)


        #zera todas arrays
        self.limpar()

        #atualiza a array com os poligonos
        # lê cada linha da tabela e reconstroi
        for coordenadas in tabela_arr:
            tipo = coordenadas[6]
            x1 = Transformações.AjusteCoordenada(coordenadas[1], x_value)
            y1 = Transformações.AjusteCoordenada(coordenadas[2], y_value)
            x2 = Transformações.AjusteCoordenada(coordenadas[3], x_value)
            y2 = Transformações.AjusteCoordenada(coordenadas[4], y_value)
            poligono_str = coordenadas[7]
            andar = coordenadas[8]
            cor_str = coordenadas[5].split(',')
            cor = QtGui.QColor(int(cor_str[0]), int(cor_str[1]), int(cor_str[2]))
            dados_adicionais = {"Ocupantes":0}
            buracos = coordenadas[13]
            self.adiciona_elemento(tipo, x1, y1, x2, y2, cor, poligono_str, coordenadas[0], andar, dados_adicionais, buracos)
            self.update()

        #atualiza a array com as réguas
        tabela_arr_reguas = eventosTabela.ConteudosTabela_ARR(self.table_reguas)
        for coordenadas in tabela_arr_reguas:
            x1 = Transformações.AjusteCoordenada(coordenadas[1], x_value)
            y1 = Transformações.AjusteCoordenada(coordenadas[2], y_value)
            x2 = Transformações.AjusteCoordenada(coordenadas[3], x_value)
            y2 = Transformações.AjusteCoordenada(coordenadas[4], y_value)
            andar = coordenadas[0]
            self.adiciona_regua(x1, y1, x2, y2, andar)
            self.update()

        tabela_arr_janelas_portas = eventosTabela.ConteudosTabela_ARR(self.table_janelas_portas)
        for coordenadas in tabela_arr_janelas_portas:
            andar = coordenadas[0]
            x_central = Transformações.AjusteCoordenada(coordenadas[1], x_value)
            y_central = Transformações.AjusteCoordenada(coordenadas[2], y_value)
            SHGC = coordenadas[5]
            largura = coordenadas[6]
            tipo = coordenadas[8]
            angulo_rad = coordenadas[9]
            self.adiciona_janela_porta(x_central, y_central, tipo, andar, angulo_rad, SHGC, largura)

        #adiciona a uma lista de render as condições de contorno horizontais
        tabela_horizontal = eventosTabela.ConteudosTabela_ARR(self.table_horizontal)
        #["Indice", "Interface", "Classe", "Vértices", "C. de Contorno", "Interface Andar", "Área", "Hole", "Contato Superficial Direto", "cor", "andar pertecente"]
        for linha in tabela_horizontal:
            vertices = linha[3].replace(" ","").replace("[","").replace("]","")
            coordenadas_str_arr = vertices.split("),(")
            coordenadas_novas = []   
            interface_andar = linha[5]
            poligono = []         
            for tupla_str in coordenadas_str_arr:
                x_str,y_str =  tupla_str.split(",")[0], tupla_str.split(",")[1]
                x_str, y_str = x_str.replace("(", ""), y_str.replace(")", "")
                x,y = float(x_str),float(y_str)
                x = Transformações.AjusteCoordenada(x, x_value)
                y = Transformações.AjusteCoordenada(y, y_value)
                ponto = QtCore.QPoint (x,y)
                poligono.append(ponto)

            buracos = []
            vertices_buracos = linha[7]
            vertices_buracos = vertices_buracos.replace(" ","").replace("],[", "|").replace("[","").replace("]","")
            buracos_str = vertices_buracos.split("|")
            for vertices_ in buracos_str:
                coordenadas_str_arr = vertices_.split("),(")
                coordenadas_buraco = []
                for tupla_str in coordenadas_str_arr:
                    try:
                        x_str,y_str =  tupla_str.split(",")[0], tupla_str.split(",")[1]
                        x_str, y_str = x_str.replace("(", ""), y_str.replace(")", "")
                        x,y = float(x_str),float(y_str)
                        x = Transformações.AjusteCoordenada(x, x_value)
                        y = Transformações.AjusteCoordenada(y, y_value)
                        ponto = QtCore.QPoint (x,y)
                        coordenadas_buraco.append(ponto)
                    except:
                        None
                
                buracos.append(coordenadas_buraco)

            dados_adicionais = []
            andares = interface_andar.split("<->")
            try:
                andar1 = int(andares[0])            

                self.drawing_area.condições_de_contorno[andar1].append([poligono, buracos, dados_adicionais])

            except: None
            try:
                andar2 = int(andares[1])
                
                self.drawing_area.condições_de_contorno[andar2].append([poligono, buracos, dados_adicionais])
 
            except: None
        None
        self.update_labels()

    # adiciona um por um cada poligono na tela
    def adiciona_regua(self, x1, y1, x2, y2, andar):
        w = int(x2-x1)
        h = int(y2-y1)
        global andar_atual


        linha = [(x1, y1), (x2, y2)]
        self.drawing_area.lista_reguas[int(andar)].append(linha)



 
    # é invocado toda vez que for chamado o "atualizar"
    # adiciona um por um cada poligono na tela
    def adiciona_elemento(self, tipo, x1, y1, x2, y2, cor, poligono_str, nome_ambiente, andar, dados_adicionais, buracos):
        w = int(x2-x1)
        h = int(y2-y1)
        global andar_atual

        #renderiza como retangulo
        if("retângulo" in tipo):
            retangulo = QtCore.QRect(x1, y1, w, h)
            print("tamanho lista: " + str(len(self.drawing_area.rectangles)) +  " andar: " + andar)
            self.drawing_area.rectangles[int(andar)].append((retangulo, cor, nome_ambiente))
        #renderiza como linha
        if(tipo == "linha"):
            #\

            linha = [(x1, y1), (x2, y2)]
            self.drawing_area.linhas[int(andar)].append((linha, cor))

        if(tipo == "poligono"):
            pontos_poligono_str = poligono_str.split("),(")
            pontos_poligono = []

            poligono = QtGui.QPolygon()
            for ponto_str in pontos_poligono_str:
                ponto_str_divido = ponto_str.replace("(", "").replace(")", "").split(",")
                x_float = float(ponto_str_divido[0])
                y_float = float(ponto_str_divido[1])

                x = int(Transformações.AjusteCoordenada(x_float, x_value))
                y = int(Transformações.AjusteCoordenada(y_float, y_value))
                ponto_poligono = QtCore.QPoint(x, y)
                pontos_poligono.append(ponto_poligono)
            

            poligono = QtGui.QPolygon(pontos_poligono)
            try:
       
                self.drawing_area.poligonos[int(andar)].append([poligono, cor, nome_ambiente, dados_adicionais, buracos])
            except:
                None



    def adiciona_janela_porta (self, x_central, y_central, tipo, andar, angulo_rad, SHGC, largura):
        if (tipo == "janela" or tipo == "porta"):
            x = x_central
            y = y_central

            ponto_central = QtCore.QPoint(x, y)
            if(tipo == "janela"):
                self.drawing_area.janelas[int(andar)].append([ponto_central, angulo_rad, SHGC, largura])
            if(tipo == "porta"):
                self.drawing_area.portas[int(andar)].append([ponto_central, angulo_rad, SHGC, largura])
            None

    def limpar(self):
        # Limpa todos os retângulos da tela
        self.drawing_area.rectangles = [[]]        
        self.drawing_area.linhas = [[]]
        self.drawing_area.poligonos = [[]]
        self.drawing_area.lista_reguas = [[]]
        self.drawing_area.portas = [[]]
        self.drawing_area.janelas = [[]]
        self.drawing_area.condições_de_contorno = [[]]


        # recria as listas com o tamanho correto
        self.ajustar_tamanho_listas()
        self.drawing_area.update() 
        for i in range(1000):
            self.drawing_area.rectangles.append([])        
            self.drawing_area.linhas.append([])   
            self.drawing_area.poligonos.append([])   
            self.drawing_area.lista_reguas.append([])   
            self.drawing_area.portas.append([])   
            self.drawing_area.janelas.append([])  
            self.drawing_area.condições_de_contorno.append([])            


    #ajusta o tamanho das listas de figuras de acordo com o numero de andares
    def ajustar_tamanho_listas(self):
        # Limpa todos os retângulos da tela
        global andar_max
        andar_int = int(andar_max)



        while(len(self.drawing_area.rectangles)<andar_int+1):
            self.drawing_area.rectangles.append([])
            self.drawing_area.linhas.append([])
            self.drawing_area.poligonos.append([])
            self.drawing_area.lista_reguas.append([])
            self.drawing_area.portas.append([])
            self.drawing_area.janelas.append([])
            self.drawing_area.pontos_existentes.append([])
            self.drawing_area.condições_de_contorno.append([])
        # self.drawing_area.poligonos = []
        

    def gerar_cor(self):
        # Gera uma cor aleatória
        return QtGui.QColor(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

    def keyPressEvent(self, event):
        # Manipula os eventos de teclado para mover a visualização
        global x_value, y_value
        if event.key() == QtCore.Qt.Key_Right:
            x_value += velocidade_scroll_seta
            self.atualizar()
        elif event.key() == QtCore.Qt.Key_Left:
            x_value -= velocidade_scroll_seta
            self.atualizar()
        elif event.key() == QtCore.Qt.Key_Up:
            y_value -= velocidade_scroll_seta
            self.atualizar()
        elif event.key() == QtCore.Qt.Key_Down:
            y_value += velocidade_scroll_seta
            self.atualizar()
        elif event.key() == QtCore.Qt.Key_Escape:
            self.drawing_area.begin =QtCore.QPoint()
            self.drawing_area.begin_sem_zoom = QtCore.QPoint()
            self.drawing_area.end = QtCore.QPoint()
            self.drawing_area.primeiro_ponto_poligono = []

        elif event.key()==(Qt.Key_Control and Qt.Key_E):
            global andar_max
            andar_int = int(andar_max)
            self.drawing_area.begin =QtCore.QPoint()
            self.drawing_area.begin_sem_zoom = QtCore.QPoint()
            self.drawing_area.end = QtCore.QPoint()
            self.drawing_area.primeiro_ponto_poligono = []
            i = 0
            while(i<andar_int+1):
                self.drawing_area.lista_reguas[i] = []
                self.table_reguas.removeRow(i)
                i+=1
            while (self.table_reguas.rowCount()!=0):
                self.table_reguas.removeRow(0)

        self.update_labels()
        event.accept()

    def wheelEvent(self, event):
        # Manipula o evento de roda do mouse para zoom in/out
        global scroll_zoom, zoom, escala
        if event.angleDelta().y() > 0:
            if(escala != escala_original):
                escala = escala * 2 
            else:
                scroll_zoom += 1
        else:
            scroll_zoom -= 1
        if scroll_zoom < 0:
            #mecho só na escala sem mexer no zoom, pois zoom menor que 100% mostrou dar problemas
            scroll_zoom = 0
            escala = escala / 2

        zoom = pow(2, scroll_zoom)
        if(scroll_zoom == 3):
            zoom = 10
        if(scroll_zoom >= 4):
            zoom = 10
            scroll_zoom = 3
        if(scroll_zoom >= 5):
            zoom = 20
            scroll_zoom = 4
        if(scroll_zoom >= 6):
            zoom = 50
            scroll_zoom = 5
        self.update_labels()
        event.accept()
        self.atualizar()

    #para os ambientes
    def keyPressEventTable(self, event):
        # Verificar se a tecla pressionada é a tecla "Delete"
        if event.key() == QtCore.Qt.Key_Delete:
            # Obter a linha selecionada
            andar_pertencente = None
            selected_row = self.table.currentRow()
            # Verificar se uma linha está selecionada
            if selected_row >= 0:
                #captura que ambiente era
                ambiente =self.table.item(selected_row, 0).text()
                andar_pertencente = int(self.table.item(selected_row, 8).text())
                # Remover a linha selecionada
                self.table.removeRow(selected_row)

                #remove as paredes atreladas a esse ambiente apagado
                deletado_count = 0
                for row in range(self.table_paredes.rowCount()+1):
                    try:

                        ambientes_parede = self.table_paredes.item(row-deletado_count, 1).text().replace("[","").replace("]","").replace("'","")
                        ambientes_arr = ambientes_parede.split(",")
                        ambiente_cout = 0
                        #tira a primeira barra de espaço dos nomes dos ambientes
                        for ambiente_str in ambientes_arr:
                            if(ambiente_str.startswith(" ")):
                                ambientes_arr[ambiente_cout] = ambiente_str[1:]
                            ambiente_cout+=1
                        # caso o ambiente esteja disponivel na parede remove o ambiente ou a parede toda 
                        if (ambiente in ambientes_arr):
                            if(len(ambientes_arr) == 1):
                                self.table_paredes.removeRow(row-deletado_count)
                            else:
                                ambientes_arr.remove(ambiente)
                                self.table_paredes.setItem(row-deletado_count,1,QtWidgets.QTableWidgetItem(str(ambientes_arr)))

                            deletado_count+=1
                    except:
                        print("Possivel Erro: paredes deletadas")

                #remove os pontos para snap
                pontos = self.drawing_area.pontos_existentes[andar_pertencente]
                novos_pontos_andar = []
                for ponto, ambiente_ponto in pontos:
                    if(ambiente_ponto != ambiente):
                        novos_pontos_andar.append((ponto, ambiente_ponto))
                self.drawing_area.pontos_existentes[andar_pertencente] = novos_pontos_andar
                # Atualizar o desenho na área de desenho
                self.atualizar()
        else:
            # Se a tecla pressionada não for "Delete", chamar o keyPressEvent original da tabela
            super().keyPressEvent(event)


    def keyPressEventTable_Cargas(self, event):
        # Verificar se a tecla pressionada é a tecla "Delete"
        if event.key() == QtCore.Qt.Key_Delete:
            # Obter a linha selecionada
            selected_row = self.table_cargas.currentRow()
            # Verificar se uma linha está selecionada
            if selected_row >= 0:
                # Remover a linha selecionada
                self.table_cargas.removeRow(selected_row)

                # Atualizar o desenho na área de desenho
                self.atualizar()
        else:
            # Se a tecla pressionada não for "Delete", chamar o keyPressEvent original da tabela
            super().keyPressEvent(event)        

    def keyPressEventTable_Elementos(self, event):
        # Verificar se a tecla pressionada é a tecla "Delete"
        if event.key() == QtCore.Qt.Key_Delete:
            # Obter a linha selecionada
            selected_row = self.table_janelas_portas.currentRow()
            # Verificar se uma linha está selecionada
            if selected_row >= 0:
                #captura que ambiente era
                ambiente =self.table_janelas_portas.item(selected_row, 0).text()
                # Remover a linha selecionada
                self.table_janelas_portas.removeRow(selected_row)

                # Atualizar o desenho na área de desenho
                self.atualizar()
        else:
            # Se a tecla pressionada não for "Delete", chamar o keyPressEvent original da tabela
            super().keyPressEvent(event)


    # controla o modo do clique entre
    #"rastrear" "linha" "linha90g" "retângulo"
    def atualizar_modo(self, modo):
        global modo_escolhido
        modo_escolhido = modo
        if(modo_escolhido == "linha"):
            self.drawing_area.begin =QtCore.QPoint()
            self.drawing_area.begin_sem_zoom = QtCore.QPoint()
            self.drawing_area.end = QtCore.QPoint()
            self.drawing_area.primeiro_ponto_poligono = []
            
        if(modo_escolhido == "unir"):
            self.drawing_area.lista_indices_poligonos_união =  []
            self.drawing_area.lista_poligonos_união = [] #zera as duas listas pra evitar poligono acumulado na memória
            self.drawing_area.lista_nome_ambiente_união = []
        if(modo_escolhido == "selecionar"):
            self.drawing_area.setCursor(Qt.ArrowCursor) # configura o cursor em formato de seta
        if(modo_escolhido == "arrastar"):
            self.drawing_area.setCursor(Qt.ArrowCursor) # configura o cursor em formato de seta
            self.drawing_area.resizing = True
        if(modo_escolhido == "alterar poligono"):
            self.drawing_area.setCursor(Qt.WhatsThisCursor) # configura o cursor em formato de cruz        
        if(modo_escolhido == "retângulo" or modo_escolhido == "linha"):
            self.drawing_area.setCursor(Qt.CrossCursor)
        if(modo_escolhido == "régua"):
            self.drawing_area.begin =QtCore.QPoint()
            self.drawing_area.begin_sem_zoom = QtCore.QPoint()
            self.drawing_area.end = QtCore.QPoint()
            self.drawing_area.primeiro_ponto_poligono = []
            #CURSOR_NEW = QtGui.QCursor(QtGui.QPixmap('cursor/regua.png'))
            #self.drawing_area.setCursor(CURSOR_NEW) # muda o cursor
            self.drawing_area.setCursor(Qt.ArrowCursor) # configura o cursor em formato de seta do mouse
            

    def modo_arrastar_atualizar(self):
        global arrastar_ligado
        if(self.parent().arrastarCheckbox.isChecked()):
            arrastar_ligado = True
        else:
            arrastar_ligado = False
        print(str(arrastar_ligado))
    #verifica como devem ser as paredes realmente verificando onde elas estão em intercessão e dividindo elas
    def AutoRecriarParedes2(self):
        global escala, andar_max

        self.table_paredes, self.table_horizontal, self.table_janelas_portas = parede_gerenciamento.AutoCriação_Paredes3(self.table_paredes, andar_max+1, self.table_horizontal, self.table, self.table_janelas_portas, self.andar_terreo, self.paredes_default, self.pé_direito)
        self.necessario_novas_CContorno = False
        tb = eventosTabela.ConteudosTabela_ARR(self.table_cargas)
        
        
        self.atualizar()





    def janelaButton(self):
        CURSOR_NEW = QtGui.QCursor(QtGui.QPixmap('cursor/door.png'))
        self.drawing_area.setCursor(CURSOR_NEW) # muda o cursor
        self.dialog = Interfaces_Secundarias.TelaCriarJanelaPorta(self.drawing_area.SHGC, self.drawing_area.largura, self.drawing_area.altura, self.drawing_area.tipoItem, self.drawing_area.espessura_janela_porta, self.drawing_area.k_janela_k, self.drawing_area.U, self.drawing_area.UouSHGC)
        self.dialog.valores_salvos.connect(self.atualizar_valores_Janela_Porta)
        self.dialog.show()
        global modo_escolhido
        modo_escolhido = self.drawing_area.tipoItem

    
    def atualizar_valores_Janela_Porta(self, SHGC, largura, altura, tipoItem, espessura, k, U, UouSHGC):
        global modo_escolhido
        if(tipoItem == "janela"):
            self.drawing_area.SHGC = SHGC
        if(tipoItem == "porta"):
            self.drawing_area.SHGC = SHGC
        self.drawing_area.largura = largura
        self.drawing_area.altura = altura
        self.drawing_area.tipoItem = tipoItem
        modo_escolhido = tipoItem
        self.drawing_area.espessura_janela_porta = espessura
        self.drawing_area.k_janela_k = k
        self.drawing_area.U = U
        self.drawing_area.UouSHGC = UouSHGC

    def Configurar(self):
        self.dialog = Interfaces_Secundarias.TelaConfiguração()
        self.dialog.show()

    def Simular(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setText("É altamente recomendado que salve o arquivo antes de iniciar a simulação!\nAtualmente o programa se encontra em estado de teste e \napresenta muitos erros e bugs que encerraram o programa.")
        msg.setInformativeText("Aviso")
        msg.setWindowTitle("Confirmação")
        msg.setDetailedText("Os detalhes são os a seguir:")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        resposta = msg.exec_()

        if resposta == QMessageBox.Yes:
            continuar = True
            self.SalvarArquivo()
        else:
            continuar = False
        

        print("Cargas: " + str(self.table_cargas))
        continuar = True
        nome_arquivo_climatico = None
        with open("temp/arquivos_climaticos/config.txt", "r") as f:
            lines = f.readlines()
            for line in lines:
                if("path=" in line):
                    nome_arquivo_climatico = line.split("=")[1].strip()
        if(nome_arquivo_climatico == "False"):
            continuar = False
            QtWidgets.QMessageBox.information(self, "Aviso", "Não foi carregado nenhum arquivo climático (.epw).")          
        elif(self.necessario_novas_CContorno == False):
            None
        elif(continuar == True):
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText("Foram alteradas condições de projeto sem atualizar \nas condições de contorno, deseja prosseguir?")
            msg.setInformativeText("Não recomendado continuar.")
            msg.setWindowTitle("Confirmação")
            msg.setDetailedText("Os detalhes são os a seguir:")
            msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            resposta = msg.exec_()

            if resposta == QMessageBox.Yes:
                continuar = True
            else:
                continuar = False

        if(continuar == True):
            horario_hvac = {"hora_inicial": int(self.horario_inicial_hora), "minuto_inicial": int(self.horario_inicial_min), "hora_final": int(self.horario_final_hora), "minuto_final": int(self.horario_final_min)}
            dicionario_tabelas = {"Qtabela_paredes": self.table_paredes, "Qtabela_ambientes": self.table,"Qtable_horizontal": self.table_horizontal, "Qtable_equipamentos": self.table_cargas, "Qtabela_janelas_portas": self.table_janelas_portas}  
            self.simulação = Interfaces_Secundarias.TelaSimulação(self.pé_direito, dicionario_tabelas, self.potencia_refrigeração, self.latitude_graus, self.unidade, self.COP, self.paredes_default, self.temperatura_desejada, self.ACH_troca_de_ar_h, horario_hvac, self.andar_terreo, self.angulo_N_geral, self.classe_compressor, self.temperatura_limite_inferior, self.metodo_calculo_temp_solo, self.temp_solo_cte)
            self.simulação.show()

        #simulacao.Laterais(self.table_paredes, self.table, self.table_horizontal, self.table_cargas, 2.1, self.potencia_refrigeração, "Ano")


    def GerenciarCargasTermicas(self):
        self.dialog = Interfaces_Secundarias.TelaCargas(self.table_cargas,self.table, self, self.drawing_area.poligonos)
        self.dialog.valores_salvos.connect(self.atualizar_table_cargas)
        self.dialog.show()
    
    def configurarHVAC(self):
        self.dialog = Interfaces_Secundarias.TelaConfigurarHVAC(self.potencia_refrigeração, self.classe_compressor, self, self.unidade, self.COP, self.temperatura_desejada, self.ACH_troca_de_ar_h, self.horario_inicial_hora, self.horario_final_hora, self.horario_inicial_min, self.horario_final_min, self.temperatura_limite_inferior)
        self.dialog.valores_salvos.connect(self.atualizar_valores_HVAC)
        self.dialog.show()

    def atualizar_valores_HVAC(self, nova_potencia, nova_classe, nova_unidade, COP, temperatura_desejada, ACH_troca_de_ar_h, horario_inicial_hora, horario_final_hora, horario_inicial_min, horario_final_min, temperatura_limite_inferior):
        self.potencia_refrigeração = nova_potencia
        self.classe_compressor = nova_classe
        self.unidade = nova_unidade
        self.COP = COP
        self.temperatura_desejada = temperatura_desejada
        self.ACH_troca_de_ar_h = ACH_troca_de_ar_h
        self.horario_inicial_hora = horario_inicial_hora
        self.horario_final_hora = horario_final_hora
        self.horario_inicial_min, self.horario_final_min = horario_inicial_min, horario_final_min
        self.temperatura_limite_inferior = temperatura_limite_inferior


    def ScheduleTeste(self):
        try:
            tabela_arr = eventosTabela.ConteudosTabela_ARR(self.table_cargas)
            atividades = {}
            for item in tabela_arr:
                nome = item[1]
                de = int(item[6])
                até = int(item[7])
                atividades[nome] = {"inicio": de , "fim": até}
            
            dialog = teste_schedule.Cronograma(atividades, self.table_cargas, self.drawing_area.poligonos)
            dialog.mainloop()
            print("Schedule fechado")

        except:
            print("erro ao carregar tela Schedule")



    def atualizar_table_cargas(self, table_cargas):


        self.table_cargas = table_cargas
        ta = eventosTabela.ConteudosTabela_ARR(table_cargas)
        tb = eventosTabela.ConteudosTabela_ARR(self.table_cargas)
        None

    def atualizar_valores_Schedule(self, table_cargas):
        self.table_cargas = table_cargas

    def configurarClimaGeo(self):
        #latitude, angulo_N, metodo_calculo_temp_solo, temp_solo_cte
        self.dialog = Interfaces_Secundarias.TelaConfigurarClimaGeo(self.latitude_graus, self.angulo_N_geral, self.metodo_calculo_temp_solo, self.temp_solo_cte)
        self.dialog.valores_salvos.connect(self.atualizar_valores_ClimaGeo)
        self.dialog.show()    


    def ConfigurarParedes_e_Andares(self):
        self.dialog = Interfaces_Secundarias.TelaConfigurarParedes_e_Andares(self.paredes_dados, self.paredes_default, self.pé_direito, self.andar_terreo)
        self.dialog.valores_salvos.connect(self.atualizar_andaresConfiguracoes)
        self.dialog.show()          

    def atualizar_andaresConfiguracoes(self, paredes_default, pé_direito, andar_terreo):
        self.paredes_default = paredes_default
        self.pé_direito = pé_direito
        self.andar_terreo = andar_terreo
        None

    def atualizar_valores_ClimaGeo(self, latitude, angulo_N_geral, metodo_calculo_temp_solo, temp_solo_cte):
        self.latitude_graus = latitude
        self.angulo_N_geral = angulo_N_geral
        self.metodo_calculo_temp_solo = metodo_calculo_temp_solo
        self.temp_solo_cte = temp_solo_cte

    def discretizar(self):
        tabela_arr = eventosTabela.ConteudosTabela_ARR(self.table)
        #cria uma lista que vai acomodar todos os poligonos que serão analisados separando por andar
        total_andares = len(self.drawing_area.rectangles)
        poligonos = []
        for i in range(total_andares):
            poligonos.append([])

        for coordenadas in tabela_arr:
            tipo = coordenadas[6]
            ambiente = coordenadas[0]
            x1 = Transformações.AjusteCoordenada(coordenadas[1], 0)
            y1 = Transformações.AjusteCoordenada(coordenadas[2], 0)
            x2 = Transformações.AjusteCoordenada(coordenadas[3], 0)
            y2 = Transformações.AjusteCoordenada(coordenadas[4], 0)
            andar = int(coordenadas[8])
            w = int(x2-x1)
            h = int(y2-y1)
            cor_str = coordenadas[5].split(',')
            #renderiza como retangulo
            if("retângulo" in tipo):
                ponto1 = (x1,y1)
                ponto2 = (x1,y2)
                ponto3 = (x2,y2)
                ponto4 = (x2,y1)
                cor = self.gerar_cor()
                poligono = ([ponto1,ponto2,ponto3,ponto4],cor,ambiente)
                poligonos[andar].append(poligono)
            #renderiza como linha
            if(tipo == "linha"):
                None

            if(tipo == "poligono"):
                pontos_str = coordenadas[7].split("),(")
                poligono = []
                for ponto_str in pontos_str:
                    x_str,y_str =  ponto_str.split(",")[0], ponto_str.split(",")[1]
                    x_str, y_str = x_str.replace("(", ""), y_str.replace(")", "")
                    x,y = float(x_str),float(y_str)
                    x = Transformações.AjusteCoordenada(x, 0)
                    y = Transformações.AjusteCoordenada(y, 0)
                    poligono.append((x,y))


                cor = self.gerar_cor()
                dados_adicionais = {"ocupantes":0}
                buracos = "NA"
                poligonos[andar].append([poligono, cor, ambiente, dados_adicionais, buracos])
        

        valor_min_x, valor_max_x ,  valor_min_y,  valor_max_y, pontos_discretizados_andar = contorno.discretização_interna(poligonos,resolucao=1, camadas_contorno=1)
        
        andar_count = 0
        plots = []


        #mostra como ficou a discretização do ambiente
        if(plotar_discretização_ambientes == True):
            for andar in range(len(self.drawing_area.rectangles)):
                pontos_discretizados = pontos_discretizados_andar[andar_count]
                fig, ax = plt.subplots()
                # Define a proporção dos eixos como 1:1
                ax.set_aspect('equal')
                # Inverte a ordem dos valores no eixo Y
                ax.invert_yaxis()
                plt.title("Pontos Internos e de Contorno - Andar " + str(andar_count), fontweight="bold", fontsize=14, color="black")
                for nome_ambiente, ambiente_valor  in pontos_discretizados.items():
                    plt.plot(*zip(*ambiente_valor["pontos internos"]),"o", markersize=1, color="cyan")
                    plt.plot(*zip(*ambiente_valor["pontos contorno"]),"o", markersize=2, color="gray")
                andar_count+=1
                plots.append(fig)

            for plot in plots:
                plot.show()
        
        return valor_min_x, valor_max_x ,  valor_min_y,  valor_max_y, pontos_discretizados_andar

        


class DrawingArea(QtWidgets.QWidget):
    def __init__(self, parent):
        # Inicializa a área de desenho
        super().__init__(parent)

        self.setCursor(Qt.CrossCursor) # configura o cursor em formato de cruz

        self.begin = QtCore.QPoint()
        self.begin_linha = QtCore.QPoint()
        self.begin_sem_zoom = QtCore.QPoint()
        self.end = QtCore.QPoint()
        self.rectangles = [[],[],[]]
        self.linhas = [[],[],[]]
        self.poligonos = [[],[],[]]
        self.lista_reguas = [[],[],[]]
        self.janelas = [[],[],[]]
        self.portas = [[],[],[]]
        self.avisos_tela = "\n"
        self.pontos_existentes = [[],[],[]]
        self.primeiro_ponto_poligono = []
        self.selected_rectangle_index = -1
        self.offset = QtCore.QPoint()
        self.resizing = False

        self.lista_poligonos_união = [] # acumula até dois itens antes de unir
        self.lista_indices_poligonos_união = []
        self.lista_nome_ambiente_união = []
        #cria as canetas usadas nas linhas individualmente
        self.pen_linha = QtGui.QPen()
        self.pen_linha.setColor(QColor("purple"))
        self.pen_linha.setWidth(2)
        self.pen_poligono = QtGui.QPen()
        self.pen_poligono.setColor(QColor("black"))
        self.pen_poligono.setWidth(2)
        self.pen_grade = QtGui.QPen()
        self.pen_grade.setWidth(1)
        self.pen_ambiente_selecionado = QtGui.QPen(QtCore.Qt.red, 4, QtCore.Qt.DashLine)
        self.pen_cond_contorno = QtGui.QPen(QtCore.Qt.red, 1, QtCore.Qt.DashLine)
        self.pen_nome_ambiente = QtGui.QPen()
        self.cor_nome_ambiente = QColor("black")
        self.pen_nome_ambiente.setColor(QColor("black"))
        # configurações de janela e portas
        self.SHGC, self.largura, self.altura, self.tipoItem, self.espessura_janela_porta, self.k_janela_k = 0, 0, 0, "janela", 0, 0
        self.U = 0
        self.UouSHGC = "SHGC"
        self.medição_continua = False
        self.snap = True

        #usado para mover a tela
        self.setMouseTracking(True)
        self.ultimo_ponto_x = None
        self.ultimo_ponto_y = None
        self.ultimo_x_value = None
        self.ultimo_y_value = None
        self.inicio_x_arrastar_tela = None 
        self.inicio_y_arrastar_tela = None

        #tipos de vista
        self.vista_contorno = False
        self.vista_ambientes = True
        self.condições_de_contorno = [[],[],[]]

    def Vistas_ambientes(self):
        if(self.vista_ambientes == True):
            self.vista_ambientes = False
            self.parent().vista_ambiente_button.setChecked(False)
        elif(self.vista_ambientes == False):
            self.vista_ambientes = True
            self.parent().vista_ambiente_button.setChecked(True)
    def Vistas_contonos(self):
        if(self.vista_contorno == True):
            self.vista_contorno = False
            self.parent().vista_contornos_button.setChecked(False)
        elif(self.vista_contorno == False):
            self.vista_contorno = True
            self.parent().vista_contornos_button.setChecked(True)

    def Centralizar_Vista(self):
        global x_value, y_value, zoom,escala
        andar = int(andar_atual)
        x_min = 99999999
        y_min = 99999999 
        x_max = -99999999
        y_max = -99999999 
        escala = 100
        zoom = 1

        tabela_arr = eventosTabela.ConteudosTabela_ARR(self.parent().table)
        for ambiente in tabela_arr:
            ambiente_nome  = ambiente[0]
            if(int(ambiente[8]) == andar):
                vertices_str_arr = ambiente[7].replace(" ","").split("),(")
                for vertice_str in vertices_str_arr:

                    p1 = int(float(vertice_str.split(",")[0].replace("(",""))*escala)
                    p2 = int(float(vertice_str.split(",")[1].replace(")",""))*escala)
                    if(p1<x_min):
                        x_min = p1
                    if(p1>x_max):
                        x_max = p1                    
                    if(p2<y_min):
                        y_min = p2
                    if(p2>y_max):
                        y_max = p2                        
        largura_necessaria = x_max-x_min
        altura_necessaria = y_max-y_min
        largura_tela = self.width()
        
        altura_tela = self.height()

        zoom_x = largura_tela/largura_necessaria
        zoom_y = altura_tela/altura_necessaria
        #ajusta o zoom para acomodar tudo
        zoom = int(max([min([zoom_x,zoom_y]),1]))
        #se o zoom for "negativo", ou seja, zoom out, é afastado a câmera através da alteração da escala
        if(min([zoom_x,zoom_y])<1):
            escala_list = [100, 50, 25, 10, 5, 2, 1]
            escala_temp = int(min([zoom_x,zoom_y])*100)
            i_escala = 0
            while(escala>escala_temp and i_escala <= 6):
                escala = escala_list[i_escala]
                i_escala+=1
        else:
            zoom_temp = zoom
            zoom = 1
            zoom_list = [1,2,5,10,20,50,100]
            i_zoom = 0
            while(zoom<zoom_temp):
                zoom = zoom_list[i_zoom]
                i_zoom +=1
            if(zoom>zoom_list[0]):
                zoom = zoom_list[i_zoom-1]
                i_zoom -=1
            if(zoom>zoom_list[0]):
                zoom = zoom_list[i_zoom-1]
        if(tabela_arr!=[]):
            x_value = x_min -int(100/zoom*escala/100)-100
            y_value = y_min - int(100/zoom*escala/100)-100
        if(tabela_arr==[]):
            x_value=0
            y_value=0
            zoom=1
            escala=100
        self.parent().atualizar()

    # desenha as figuras na tela a cada atualização
    def paintEvent(self, event):
        # Desenha os retângulos na área de desenho
        global zoom, x_value, y_value, andar_atual
        qp = QtGui.QPainter(self)
        andar = int(andar_atual)
        # desenha o fundo branco
        qp.setBrush(QtCore.Qt.white)  # Define a cor de fundo branca
        qp.drawRect(self.rect())

        


        #desenha a grade
        #define os offset das linhas da grade
        qp.setPen(self.pen_grade)
        (offsetLinhaVertical,offsetLinhaHorizontal) = Transformações.Offsets_X_Y()
        #linhas horizontais
        inicial_horizontal =  int(offsetLinhaHorizontal/100)*100
        for y in range(0, self.height(), 100):
            qp.drawLine(0, y - offsetLinhaHorizontal+inicial_horizontal, self.width(), y - offsetLinhaHorizontal+inicial_horizontal)
            qp.drawText(5, y + 15 - offsetLinhaHorizontal+inicial_horizontal, str((y+inicial_horizontal) / zoom / escala))
        #linhas verticais
        inicial_vertical =  int(offsetLinhaVertical/100)*100
        for x in range(0, self.width(), 100):
            qp.drawLine(x - offsetLinhaVertical + inicial_vertical, 0, x - offsetLinhaVertical+inicial_vertical, self.height())
            qp.drawText(x + 5 - offsetLinhaVertical+inicial_vertical, 15, str((x+inicial_vertical) / zoom / escala))
        


        #desenha retangulos
        for i, (retangulo, cor, nome_ambiente) in enumerate(self.rectangles[andar]):
            brush = QtGui.QBrush(cor) # a cor de cada retangulo é individual e settada usando o brush
            qp.setBrush(brush)
            #caso seja linha90g muda a cor para roxo, caso contrario fica a preta
            if (retangulo.width() == 0 or retangulo.height() == 0):
                qp.setPen(self.pen_linha)
            else:
                qp.setPen(self.pen_poligono)
            #desenha o retangulo
            qp.drawRect(retangulo)


            # usado para aparecer pontilhado vermelho em volta ao mover os retangulos
            if i == self.selected_rectangle_index:
                qp.setPen(QtGui.QPen(QtCore.Qt.red, 2, QtCore.Qt.DashLine))
                qp.drawRect(retangulo.adjusted(0, 0, -1, -1))
            
            # anotações que aparecem nas figuras geometricas
            # cuida do texto das retas90g (tipo retangulo)
            if(retangulo.width() == 0 or retangulo.height()==0):
                qp.drawText(retangulo.topLeft() + QtCore.QPoint(30, 30),
                            "Parede")
                            
                
            # cuida do texto dos retangulos
            else:
                qp.drawText(retangulo.center() + QtCore.QPoint(5, 30),
                            f"Δx: {retangulo.width() / zoom/escala}m" + f" Δy: {retangulo.height() / zoom/escala}m")
                nome_ambiente = nome_ambiente
                qp.drawText(retangulo.center() + QtCore.QPoint(-len(nome_ambiente) * 2 - 3, 5), nome_ambiente)


        selected_row = self.parent().table.currentRow()             #item selecionado pelo user na tabela
        ambiente_selecionado = None
        try:
            if(self.parent().table.hasFocus()==True):
                ambiente_selecionado =self.parent().table.item(selected_row, 0).text()
        except:
            ambiente_selecionado = None

        #desenha poligonos
        for poligono_, cor, nome_ambiente, dados_adicionais, buracos in self.poligonos[andar]:
            num_vertices = poligono_.size()
            poligono = []
            poligono_temp = []
            i=0
            for i in range(num_vertices):
                ponto = poligono_[i]
                poligono_temp.append( QtCore.QPoint (ponto.x(),ponto.y()) )
                poligono = poligono_temp.copy()
            if(ambiente_selecionado == nome_ambiente): #caso seja um item selecionado fica tracejado com dasheds
                qp.setPen(self.pen_ambiente_selecionado)

            if(self.vista_ambientes==True):
                brush = QtGui.QBrush(cor)
            else:
                brush = QtGui.QBrush(QColor("white"))
            qp.setPen(self.pen_poligono)
            qp.setBrush(brush)
            qp.drawPolygon(poligono)

            # cuida do texto dos poligonos
            vertices =  []
            try:
                for j in range(10000):
                    vertices.append( (poligono[j].x(),poligono[j].y() ) ) #usado para achar o centroide posteriormente
            except: 
                None
            #caso a média seja acima de 128 sabemos que é uma cor "clara", logo usamos  a cor "preta"
            vermelho = cor.red()
            verde = cor.green()
            azul = cor.blue()
            media = (vermelho+verde+azul)/3
            if(media>128 or self.vista_ambientes == False):
                self.cor_nome_ambiente = QColor("black")
            else:
                self.cor_nome_ambiente = QColor("white")
            self.pen_nome_ambiente = QtGui.QPen(self.cor_nome_ambiente)
            qp.setPen(self.pen_nome_ambiente)
            try:
                centroide = shapelyPolygon(vertices).centroid
            except:
                #tabela = eventosTabela.ConteudosTabela_ARR(self.parent().table)
                None
            QCentroide = QtCore.QPoint(int(centroide.x), int(centroide.y))
            nome_ambiente = nome_ambiente 
            qp.drawText(QCentroide + QtCore.QPoint(-len(nome_ambiente) * 2 - 6, 5), nome_ambiente)
            texto = "Ocupantes: " + str(dados_adicionais["Ocupantes"])
            qp.drawText(QCentroide + QtCore.QPoint(-len(texto) * 2 - 6, 15), texto)


            #desenha o "buraco" como um espaço branco
            if(buracos!="NA" and buracos!= ['']):
                buracos = buracos.replace(" ","").replace("],[", "|").replace("[","").replace("]","")
                buracos = buracos.split("|")
                for vertices_ in buracos:
                    coordenadas_str_arr = vertices_.split("),(")
                    coordenadas_buraco = []
                    for tupla_str in coordenadas_str_arr:
                        try:
                            tupla_str.replace("(","").replace(")","")
                            x = float(tupla_str.split(",")[0].replace("(","").replace(")",""))
                            y = float(tupla_str.split(",")[1].replace("(","").replace(")","")) 
                            x = int((x+inicial_vertical) * zoom * escala) - offsetLinhaVertical
                            y = int((y+inicial_horizontal) * zoom * escala) - offsetLinhaHorizontal
                            ponto = QtCore.QPoint (x,y)
                            coordenadas_buraco.append(ponto)
                        except:
                            None
                    qp.setBrush(Qt.white)  # Defina a cor do pincel para a cor de fundo (para "apagar" o buraco)
                    qp.drawPolygon(coordenadas_buraco)


        # mostra todas condições de contorno na tela
        if(self.vista_contorno == True):
            qp.setPen(self.pen_cond_contorno)
            
            #desenha somente as linhas sem preenchimento
            for verices_externos, buracos, dados_adicionais in self.condições_de_contorno[andar]:
                ponto1 = None
                ponto2 = None  
                for ponto_ in verices_externos:          
                    try:
                        ponto1 = ponto_
                        if ponto2 != None:
                            qp.drawLine(QtCore.QPoint(ponto1), QtCore.QPoint(ponto2))
                        ponto2 = ponto_
                    except:
                        None  
                for vertices_ in buracos:
                    ponto2 = None
                    for ponto_ in vertices_:          
                        try:
                            ponto1 = ponto_
                            if ponto2 != None:
                                qp.drawLine(QtCore.QPoint(ponto1), QtCore.QPoint(ponto2))

                            ponto2 = ponto_
                        except:
                            None  



        
        self.update()
                

        # Desenha as linhas
        # POSSO COLOCAR O AJUSTE DE COORDENADS NESSES PONTO1 E PONTO2
        pen = QtGui.QPen(QtCore.Qt.black)
        pen.setWidth(2)
        pen.setColor(QColor("purple"))
        qp.setPen(pen)
        for linha in self.linhas[andar]:
            ponto1, ponto2 = linha

            if(type(ponto2) == tuple):
                qp.drawLine(QtCore.QPoint(*ponto1), QtCore.QPoint(*ponto2))
            else:
                ponto1_ = ponto1[0]
                ponto2_ = ponto1[1]
                qp.drawLine(QtCore.QPoint(*ponto1_), QtCore.QPoint(*ponto2_))


        # Desenha as réguas
        pen = QtGui.QPen(QtCore.Qt.black, QtCore.Qt.DashLine)
        pen.setStyle(QtCore.Qt.DashLine)
        pen.setColor(QColor("purple"))
        qp.setPen(pen)
        for regua in self.lista_reguas[andar]:
            ponto1, ponto2 = regua

            if(type(ponto2) == tuple):
                qp.drawLine(QtCore.QPoint(*ponto1), QtCore.QPoint(*ponto2))
            else:
                ponto1_ = ponto1[0]
                ponto2_ = ponto1[1]
                qp.drawLine(QtCore.QPoint(*ponto1_), QtCore.QPoint(*ponto2_))
            
            dX = (ponto2[0]-ponto1[0])/100
            dY = (ponto2[1]-ponto1[1])/100

            qp.drawText( QtCore.QPoint(int((ponto1[0]+ponto2[0])/2), int((ponto2[1]+ponto2[1])/2)), "Δx: " + str(dX)  +  "m Δy: " + str(dY) + "m") 

        # desenha janelas e portas
        # JANELA
        pen = QtGui.QPen(QtCore.Qt.black)
        pen.setWidth(6)
        pen.setColor(QColor("cyan"))
        qp.setPen(pen)
        brush = QtGui.QBrush(QColor("blue"))
        qp.setBrush(brush)

        for janela in self.janelas[andar]:
            #[ponto_central, angulo_rad, SHGC, largura]
            ponto_central = janela[0]
            angulo_rad = float(janela[1])
            largura = float(janela[3])
            ponto_central_tupla = (ponto_central.x(), ponto_central.y())
            ponto1 = (int(ponto_central_tupla[0] + largura/2 * math.cos(angulo_rad)*zoom*escala/100), int(ponto_central_tupla[1] + largura/2 * math.sin(angulo_rad)*zoom*escala/100))
            ponto2 = (int(ponto_central_tupla[0] - largura/2 * math.cos(angulo_rad)*zoom*escala/100), int(ponto_central_tupla[1] - largura/2 * math.sin(angulo_rad)*zoom*escala/100))
            qp.drawLine(QtCore.QPoint(*ponto1), QtCore.QPoint(*ponto2))
            #qp.drawEllipse(ponto_central.x()-5, ponto_central.y()-5, 10, 10)
        # PORTA
        pen.setColor(QColor("brown"))
        qp.setPen(pen)
        brush = QtGui.QBrush(QColor("purple"))
        qp.setBrush(brush)            
        for porta in self.portas[andar]:
            #[ponto_central, angulo_rad, SHGC, largura]
            ponto_central = porta[0]
            angulo_rad = float(porta[1])
            largura = float(porta[3])
            ponto_central_tupla = (ponto_central.x(), ponto_central.y())
            ponto1 = (int(ponto_central_tupla[0] + largura/2 * math.cos(angulo_rad)*zoom*escala/100), int(ponto_central_tupla[1] + largura/2 * math.sin(angulo_rad)*zoom*escala/100))
            ponto2 = (int(ponto_central_tupla[0] - largura/2 * math.cos(angulo_rad)*zoom*escala/100), int(ponto_central_tupla[1] - largura/2 * math.sin(angulo_rad)*zoom*escala/100))
            qp.drawLine(QtCore.QPoint(*ponto1), QtCore.QPoint(*ponto2))
            #qp.drawEllipse(ponto_central.x()-5, ponto_central.y()-5, 10, 10)
        pen.setWidth(1)            
 
        #destaca paredes
        selected_row_parede = self.parent().table_paredes.currentRow()             #item selecionado pelo user na tabela
        parede_selecionada = None
        coordenadas_novas = [(0,0),(0,0)]
        try:
            if(self.parent().table_paredes.hasFocus()==True):
                
                parede_selecionada =self.parent().table_paredes.item(selected_row_parede, 0).text()
                vertices = self.parent().table_paredes.item(selected_row_parede, 3).text()
                andar= int(self.parent().table_paredes.item(selected_row_parede, 5).text())
                self.parent().parent().andarSpinBox.setValue(andar)
                vertices = vertices.replace(" ","")
                coordenadas_str_arr = vertices.split("),(")
                coordenadas_novas = []
                parede_temp = []
                for tupla_str in coordenadas_str_arr:

                    x = float(tupla_str.split(",")[0].replace("(","").replace(")",""))
                    y = float(tupla_str.split(",")[1].replace("(","").replace(")","")) 
                    x = int((x+inicial_vertical) * zoom * escala) - offsetLinhaVertical
                    y = int((y+inicial_horizontal) * zoom * escala) - offsetLinhaHorizontal
                    coordenadas_novas.append((x,y))
                qp.setPen(self.pen_ambiente_selecionado)
                qp.drawLine(coordenadas_novas[0][0],coordenadas_novas[0][1],coordenadas_novas[1][0],coordenadas_novas[1][1])
                qp.setPen(self.pen_poligono)
        except:
            parede_selecionada = None  

        #destaca limites horizontais
        selected_row_interface = self.parent().table_horizontal.currentRow()             #item selecionado pelo user na tabela
        interface_selecionada = None
        coordenadas_novas = [(0,0),(0,0)]
        try:
            if(self.parent().table_horizontal.hasFocus()==True):
                interface_selecionada =self.parent().table_horizontal.item(selected_row_interface, 0).text()
                #desenha parte externa do poligono
                vertices = self.parent().table_horizontal.item(selected_row_interface, 3).text()
                interface_andares = self.parent().table_horizontal.item(selected_row_interface, 5).text()
                classe = self.parent().table_horizontal.item(selected_row_interface, 2).text()
                if(classe == "teto"):
                    if(interface_andares.split("<->")[0]!="Exterior"):
                        andar = int(interface_andares.split("<->")[0])
                    else:
                        andar = int(interface_andares.split("<->")[1])
                if(classe == "piso"):
                    if(interface_andares.split("<->")[1]!="Exterior"):
                        andar = int(interface_andares.split("<->")[1])
                    else:
                        andar = int(interface_andares.split("<->")[0])
                if(classe == "conjunto"):
                    if(andar_atual == interface_andares.split("<->")[0]):
                        andar = int(interface_andares.split("<->")[0])
                    elif(andar_atual == interface_andares.split("<->")[1]):
                        andar = int(interface_andares.split("<->")[1])
                    else:
                        andar = int(interface_andares.split("<->")[0])

                self.parent().parent().andarSpinBox.setValue(andar)


                vertices = vertices.replace(" ","").replace("[","").replace("]","")
                coordenadas_str_arr = vertices.split("),(")
                coordenadas_novas = []
                for tupla_str in coordenadas_str_arr:
                    x = float(tupla_str.split(",")[0].replace("(","").replace(")",""))
                    y = float(tupla_str.split(",")[1].replace("(","").replace(")","")) 
                    x = int((x+inicial_vertical) * zoom * escala) - offsetLinhaVertical
                    y = int((y+inicial_horizontal) * zoom * escala) - offsetLinhaHorizontal
                    ponto = QtCore.QPoint (x,y)
                    coordenadas_novas.append(ponto)
                qp.setPen(self.pen_ambiente_selecionado)
                qp.drawPolygon(coordenadas_novas)
                qp.setPen(self.pen_poligono)

                #desenha o "buraco" como um espaço branco
                vertices = self.parent().table_horizontal.item(selected_row_interface, 7).text()
                vertices = vertices.replace(" ","").replace("],[", "|").replace("[","").replace("]","")
                buracos = vertices.split("|")
                for vertices_ in buracos:
                    coordenadas_str_arr = vertices_.split("),(")
                    coordenadas_buraco = []
                    for tupla_str in coordenadas_str_arr:

                        x = float(tupla_str.split(",")[0].replace("(","").replace(")",""))
                        y = float(tupla_str.split(",")[1].replace("(","").replace(")","")) 
                        x = int((x+inicial_vertical) * zoom * escala) - offsetLinhaVertical
                        y = int((y+inicial_horizontal) * zoom * escala) - offsetLinhaHorizontal
                        ponto = QtCore.QPoint (x,y)
                        coordenadas_buraco.append(ponto)

                    qp.setBrush(Qt.white)  # Defina a cor do pincel para a cor de fundo (para "apagar" o buraco)
                    qp.drawPolygon(coordenadas_buraco)
        except:
            None  

        # escreve os avisos da tela
        pen = QtGui.QPen(QtCore.Qt.black)
        pen.setWidth(1)
        pen.setColor(QColor("purple"))
        qp.setPen(pen)
        global modo_escolhido
        avisos_menores = ""
        if(len(self.lista_reguas[andar])!= 0):
            avisos_menores = "\n'ctrl + E' p/ apagar réguas\n 'Esc' para criar uma nova régua desconectada a anterior"
        qp.drawText(QtCore.QPoint(23,23), "modo: " + modo_escolhido + self.avisos_tela + avisos_menores) 

        #desenha a bussola
        bussola = QPixmap('icons/N2.png')
        bussola = bussola.transformed(QtGui.QTransform().rotate(-self.parent().angulo_N_geral), QtCore.Qt.SmoothTransformation)
        qp.drawPixmap(self.rect().width()-50, self.rect().height()-50, bussola)





    #adiciona a linha a array de linhas e a tabela
    def QLinha(self, coordenadas_iniciais, coordenadas_finais, cor, andar):
        print(str(coordenadas_iniciais))
        print(str(coordenadas_finais))
        self.linhas[int(andar)].append([(coordenadas_iniciais.x(), coordenadas_iniciais.y()), (coordenadas_finais.x(), coordenadas_finais.y())])
        self.update()
        linha = QtCore.QLine(coordenadas_iniciais, coordenadas_finais)
        ambiente = self.parent().atualizar_tabela(linha, cor, "linha", "", andar, "")
        return ambiente
    def CriarJanelaPorta(self, ponto_central, angulo_rad, andar, tipo, espessura, k, U, UouSHGC):

        if(tipo == "janela"):
            self.janelas[int(andar)].append([ponto_central, angulo_rad, self.SHGC, self.largura, self.altura, espessura, k, U, UouSHGC])
            self.parent().atualizar_tabela_janelas_portas(ponto_central, angulo_rad, self.SHGC, self.largura, self.altura, tipo, espessura, k, U, UouSHGC)
        if(tipo == "porta"):
            self.portas[int(andar)].append([ponto_central, angulo_rad, self.SHGC, self.largura, self.altura, espessura, k, U, UouSHGC])
            self.parent().atualizar_tabela_janelas_portas(ponto_central, angulo_rad, self.SHGC, self.largura, self.altura, tipo, espessura, k, U, UouSHGC)

    def Régua(self, coordenadas_iniciais, coordenadas_finais, cor, andar):
        self.lista_reguas[int(andar)].append([(coordenadas_iniciais.x(), coordenadas_iniciais.y()), (coordenadas_finais.x(), coordenadas_finais.y())])
        self.update()
        linha = QtCore.QLine(coordenadas_iniciais, coordenadas_finais)
        x1 = coordenadas_iniciais.x()/escala/zoom
        y1 = coordenadas_iniciais.y()/escala/zoom
        x2 = coordenadas_finais.x()/escala/zoom
        y2 = coordenadas_finais.y()/escala/zoom
        rowPosition = self.parent().table_reguas.rowCount()
        self.parent().table_reguas.insertRow(rowPosition)
        #["andar", "coordenadas"]
        self.parent().table_reguas.setItem(rowPosition, 0, QtWidgets.QTableWidgetItem(str(andar_atual)))
        self.parent().table_reguas.setItem(rowPosition, 1, QtWidgets.QTableWidgetItem(str(x1)))
        self.parent().table_reguas.setItem(rowPosition, 2, QtWidgets.QTableWidgetItem(str(y1)))
        self.parent().table_reguas.setItem(rowPosition, 3, QtWidgets.QTableWidgetItem(str(x2)))
        self.parent().table_reguas.setItem(rowPosition, 4, QtWidgets.QTableWidgetItem(str(y2)))
        


    #adiciona o retangulo a array de retangulos e a tabela
    def QRetangulo(self, coordenadas_iniciais, coordenadas_finais, cor, andar):
        if(converter_retangulo_p_polygono == False):
            retangulo = QtCore.QRect(coordenadas_iniciais, coordenadas_finais)
            nome_novo_retangulo = self.parent().atualizar_tabela(retangulo, cor, "retângulo", "", andar, "")
            self.rectangles[int(andar)].append((retangulo, cor,nome_novo_retangulo))
        else:
            x1, y1 = coordenadas_iniciais.x(), coordenadas_iniciais.y()
            x2, y2 = coordenadas_finais.x(), coordenadas_finais.y()
            p1 = coordenadas_iniciais
            p2 = QtCore.QPoint(x2, y1)
            p3 = QtCore.QPoint(x2, y2)
            p4 = QtCore.QPoint(x1, y2)
            pontos_poligono = [p1,p2,p3,p4]
            #fecha o poligono com o ponto inicial
            poligono = QtGui.QPolygon(pontos_poligono)
            ambiente = self.parent().atualizar_tabela(poligono, cor, "poligono", "remover_linhas_90g_e_normais", andar, "")
            dados_adicionais = {"Ocupantes":0}
            buracos = "NA"
            self.poligonos[int(andar)].append([poligono, cor, ambiente, dados_adicionais, buracos])

            p1_s = (shapely.Point(x1,y1), ambiente)
            p2_s = (shapely.Point(x2, y1), ambiente)
            p3_s = (shapely.Point(x2, y2), ambiente)
            p4_s = (shapely.Point(x1, y2), ambiente)
            self.pontos_existentes[int(andar)].extend([p1_s, p2_s, p3_s, p4_s])

    def QPoligono(self,coordenadas_linha, cor,andar):
        pontos_poligono = []
        pontos_shapely = []
        print(str(coordenadas_linha))
        for ponto in coordenadas_linha:
            ponto_poligono = QtCore.QPoint(ponto[0], ponto[1])
            pontos_poligono.append(ponto_poligono)


        #fecha o poligono com o ponto inicial
        poligono = QtGui.QPolygon(pontos_poligono)
        ambiente = self.parent().atualizar_tabela(poligono, cor, "poligono", "remover_linhas_90g_e_normais", andar,"")
        dados_adicionais = {"Ocupantes":0}
        buracos = "NA"
        self.poligonos[int(andar)].append([poligono, cor, ambiente, dados_adicionais, buracos])
        for ponto in coordenadas_linha:
            pontos_shapely.append( (shapely.Point(ponto[0], ponto[1]), ambiente) )
        self.pontos_existentes[int(andar)].extend(pontos_shapely)
        

    #caso tenha um ponto próximo cria nele
    def PontoProximo(self, x_click, y_click):
        global x_value, y_value
        ponto_click = shapely.Point(x_click, y_click)
        pontos = self.pontos_existentes[int(andar_atual)]
        menor_dist = 10000000
        ponto_menor_dist = shapely.Point()
        distancia_resol =  resolução_arredondamento/zoom * 2.5
        if(self.snap == True):

            for ponto, item_nome in pontos:
                x = ponto.x*zoom*escala/100 - x_value*zoom*escala/100
                y = ponto.y*zoom*escala/100 - y_value*zoom*escala/100
                ponto = shapely.Point(x,y)
                try:
                    distancia = ponto_click.distance(ponto)
                except:
                    print(type(ponto_click))
                    print(type(ponto))
                if(distancia<=menor_dist):
                    ponto_menor_dist = ponto
                    menor_dist = distancia
            
            if(menor_dist< distancia_resol):
                return int(ponto_menor_dist.x), int(ponto_menor_dist.y)
        
        return x_click, y_click

    def mousePressEvent(self, event):
        global x_value, y_value, zoom, resolução_arredondamento, modo_escolhido, andar_atual

        x=0
        y=0

        if  QtCore.Qt.MiddleButton:
            self.ultimo_ponto_x = event.globalPos().x() 
            self.ultimo_ponto_y = event.globalPos().y()
            self.ultimo_x_value = x_value
            self.ultimo_y_value = y_value
            self.inicio_x_arrastar_tela = event.globalPos().x() 
            self.inicio_y_arrastar_tela = event.globalPos().y()
        
        if(modo_escolhido == "janela" or modo_escolhido == "porta"):
            if event.button() == QtCore.Qt.LeftButton:
                x = event.pos().x()
                y = event.pos().y()

                #verifica o poligono mais próximo do mouse quando clicar
                encontrado = False
                i_distancia = 0
                ponto_novo_elemento = None
                while (encontrado == False):
                    ponto_vertical_N = QtCore.QPoint(x, y-i_distancia)   
                    ponto_vertical_S = QtCore.QPoint(x, y+i_distancia)
                    ponto_vertical_L = QtCore.QPoint(x + i_distancia, y)   
                    ponto_vertical_O = QtCore.QPoint(x - i_distancia, y)
                     
                    for i, (poligono, cor, nome_ambiente, dados_adicionais, buracos) in enumerate(self.poligonos[int(andar_atual)]):

                        if poligono.containsPoint  (ponto_vertical_N, Qt.OddEvenFill):
                            self.selected_poligono_index = i
                            encontrado = True
                            ponto_novo_elemento = ponto_vertical_N
                        elif poligono.containsPoint (ponto_vertical_S, Qt.OddEvenFill):
                            self.selected_poligono_index = i
                            encontrado = True
                            ponto_novo_elemento = ponto_vertical_S
                        elif poligono.containsPoint (ponto_vertical_L, Qt.OddEvenFill):
                            self.selected_poligono_index = i
                            encontrado = True
                            ponto_novo_elemento = ponto_vertical_L
                        elif poligono.containsPoint (ponto_vertical_O, Qt.OddEvenFill):
                            self.selected_poligono_index = i
                            encontrado = True
                            ponto_novo_elemento = ponto_vertical_O

                    if(i_distancia>100): #100 pixel de distancia é o max de distancia para detecção
                        break

                    i_distancia +=1

                if(encontrado == True):
                    centro_x = ponto_novo_elemento.x()
                    centro_y = ponto_novo_elemento.y()
                    i = self.selected_poligono_index
                    poligo = self.poligonos[int(andar_atual)][i][0]
                    ambiente = self.poligonos[int(andar_atual)][i][1]
                    lados = []
                    points = [poligo[i] for i in range(poligo.size())]

                    for i in range(len(points)):
                        if i < len(points) - 1:
                            lados.append([(points[i].x(), points[i].y()), (points[i + 1].x(), points[i + 1].y())])
                        else:
                            lados.append([(points[i].x(), points[i].y()), (points[0].x(), points[0].y())])


                    for lado in lados:
                        line = shapely.LineString(lado)
                        ponto_shapely = shapely.Point(centro_x, centro_y)
                        distancia = ponto_shapely.distance(line)
                        if(distancia <3):
                            seg = np.array(lado)
                            seg = seg[1] - seg[0]
                            angulo_radianos = np.angle(complex(*(seg)))

                            angulo_graus = angulo_radianos * 180 / math.pi          
                            ponto_criar_janela_shapely = nearest_points(line, ponto_shapely)[0]
                            p = ponto_criar_janela_shapely.coords[0]
                            ponto_criar_janela = QtCore.QPoint(int(p[0]), int(p[1]))
                            self.CriarJanelaPorta(ponto_criar_janela, angulo_radianos, andar_atual, modo_escolhido, self.espessura_janela_porta, self.k_janela_k, self.U, self.UouSHGC)

        elif modo_escolhido == "régua":
            if event.button() == QtCore.Qt.LeftButton:
                resolução = resolução_arredondamento / zoom
                x1 = int((self.begin.x() + x_value * zoom) / zoom)
                x1 = arredondamentos.arredondar_int(x1, resolução)
                y1 = int((self.begin.y() + y_value * zoom) / zoom)
                y1 = arredondamentos.arredondar_int(y1, resolução)
                x2 = int((event.pos().x() + x_value * zoom) / zoom)
                x2 = arredondamentos.arredondar_int(x2, resolução)
                y2 = int((event.pos().y() + y_value * zoom) / zoom)
                y2 = arredondamentos.arredondar_int(y2, resolução)
                régua_Criada = False
                if not self.begin.isNull():
                    dX = abs(x2-x1)
                    dY = abs(y2-y1)
                    # permite que retas muito longas sejam perfeitamente horizontais ou verticais
                    if(dY!= 0):
                        if(dX/dY>10):
                            y2 = y1
                    if(dX==0):
                        if(dX/dY<0.1):
                            x2 = x1                  
                    coordenadas_finais = QtCore.QPoint(x2, y2)
                    cor = self.parent().gerar_cor()
                    andar = andar_atual 
                    self.Régua(self.begin, coordenadas_finais, cor, andar)
                    self.begin = QtCore.QPoint()
                    coordenadas_finais = None
                    régua_Criada = True
                self.begin = QtCore.QPoint(x2, y2)                
                if(régua_Criada == True and self.medição_continua == False):

                    self.primeiro_ponto_poligono = []
                    self.begin = QtCore.QPoint()
                    self.begin =QtCore.QPoint()
                    self.begin_sem_zoom = QtCore.QPoint()
                    self.end = QtCore.QPoint()
                    régua_Criada = False

        elif modo_escolhido == "unir":
            if event.button() == QtCore.Qt.LeftButton:
                x = event.pos().x() 
                y = event.pos().y()
                self.begin = QtCore.QPoint(x, y)                
                for i, (poligono, cor, nome_ambiente, dados_adicionais, buracos) in enumerate(self.poligonos[int(andar_atual)]):
                    points = [poligono[i] for i in range(poligono.size())]
                    print(poligono)
                    print(points)
                    if poligono.containsPoint (self.begin,Qt.OddEvenFill):
                        self.selected_poligono_index = i

                        lista_vertices = []
                        points = [poligono[i] for i in range(poligono.size())]
                        for ponto in points:
                            ponto_x = ponto.x()
                            ponto_y = ponto.y()
                            lista_vertices.append((ponto_x, ponto_y))
                        polygon = Polygon(lista_vertices)
                        self.lista_poligonos_união.append(polygon)
                        self.lista_indices_poligonos_união.append(i)
                        self.lista_nome_ambiente_união.append(nome_ambiente)
                        if(len(self.lista_poligonos_união) == 2):
                            u = cascaded_union(self.lista_poligonos_união)
                            if isinstance(u, MultiPolygon): # caso dois poligonos não se encostem a união vira um multipoligon
                                self.lista_poligonos_união = []
                                self.lista_indices_poligonos_união = []
                                self.lista_nome_ambiente_união = []
                                break
                            i1 = self.lista_indices_poligonos_união[0]
                            i2 = self.lista_indices_poligonos_união[1]
                            poligono_unido_lista = list(u.exterior.coords)
                            qPontos = []
                            for ponto in poligono_unido_lista:
                                ponto_poligono = QtCore.QPoint(int((ponto[0] + x_value*zoom)/zoom), int((ponto[1] + y_value*zoom)/zoom))
                                qPontos.append(ponto_poligono)


                            tabela_arr = eventosTabela.ConteudosTabela_ARR(self.parent().table)
                            tabela_count = 0
                            i1_table = None
                            i2_table = None
                            for linha_tabela in tabela_arr:
                                if(linha_tabela[0] == self.lista_nome_ambiente_união[0]):
                                    i1_table = tabela_count
                                if(linha_tabela[0] == self.lista_nome_ambiente_união[1]):
                                    i2_table = tabela_count
                                tabela_count+=1

                            poligono_unido = QtGui.QPolygon(qPontos)  
                            indice_desejado = min([i1_table,i2_table])
                            ambiente = self.parent().atualizar_tabela(poligono_unido, cor, "poligono", "atualizar existente", int(andar_atual), indice_desejado) 
                            dados_adicionais = {"Ocupantes":0}
                            tupla = [poligono_unido, cor, ambiente, dados_adicionais]
                            



                            #muda a união para posição da mais antiga e a mais nova é deletada
                        
                            if(i1>i2):
                                self.poligonos[int(andar_atual)].pop(i1)


                            else:
                                self.poligonos[int(andar_atual)].pop(i2)



                            if(i1_table>i2_table):
                                self.parent().table.removeRow(i1_table)

                            else:
                                self.parent().table.removeRow(i2_table)



                            self.lista_poligonos_união = []
                            self.lista_indices_poligonos_união = []
                            self.lista_nome_ambiente_união = []
                            self.update()
                        

        if modo_escolhido == "alterar poligono":
            if event.button() == QtCore.Qt.LeftButton:
                x = event.pos().x() 

                y = event.pos().y()

                self.begin = QtCore.QPoint(x, y)
                print(self.begin)
                for i, (poligono, _, nome_retangulo, dados_adicionais) in enumerate(self.poligonos[int(andar_atual)]):
                    points = [poligono[i] for i in range(poligono.size())]
                    print(poligono)
                    print(points)
                    if poligono.containsPoint (self.begin,Qt.OddEvenFill):
                        self.selected_poligono_index = i
                        self.dialog = AlterarMedidas(self.parent().table, self.selected_poligono_index, self)
                        self.dialog.show()
                        
                        break


        elif modo_escolhido == "linha":
            if event.button() == QtCore.Qt.LeftButton:
                resolução = resolução_arredondamento / zoom
                x = int((event.pos().x() + x_value * zoom) / zoom)
                x = arredondamentos.arredondar_int(x, resolução)
                y = int((event.pos().y() + y_value * zoom) / zoom)
                y = arredondamentos.arredondar_int(y, resolução)
                print(x)
                print(y)
                if not self.begin_linha.isNull():

                    coordenadas_finais = QtCore.QPoint(x, y)
                    cor = self.parent().gerar_cor()
                    andar = andar_atual 
                    #self.QLinha(self.begin_linha, coordenadas_finais, cor, andar)
                    #self.begin_linha = None
                x = arredondamentos.arredondar_int(x, resolução)
                y = arredondamentos.arredondar_int(y, resolução)
                #self.begin_linha = QtCore.QPoint(x, y)
                

            


        elif modo_escolhido == "rastrear":
            if event.button() == QtCore.Qt.LeftButton:
                resolução = resolução_arredondamento / zoom
                x = int((event.pos().x() + x_value * zoom) / zoom)
                x = arredondamentos.arredondar_int(x, resolução)
                y = int((event.pos().y() + y_value * zoom) / zoom)
                y = arredondamentos.arredondar_int(y, resolução)
                print(f"Coordenadas do clique: ({x}, {y})")



        elif modo_escolhido == "retângulo" or modo_escolhido == "linha90g":  # linha90g é uma falsa linha, na real é um retangulo de espessura 0
            if event.button() == QtCore.Qt.LeftButton:
                resolução = resolução_arredondamento / zoom *escala/100
                x = event.pos().x()/ zoom*escala/100 + x_value *escala/100
                x = arredondamentos.arredondar_int(x, resolução)
                y = event.pos().y()/ zoom*escala/100 + y_value *escala/100
                y = arredondamentos.arredondar_int(y, resolução)
                x, y = self.PontoProximo(x,y)
                self.begin_sem_zoom = event.pos() + QtCore.QPoint(x, y)
                self.begin = QtCore.QPoint(x, y)
                print(self.begin)
                self.end = event.pos()


                self.update()

        #vai adicionando a uma lista de coordenadas de linha 90g, caso perceba que formou um poligono essa lista é zerada e se cria o polig
        if (modo_escolhido == "linha90g" or modo_escolhido == "linha"):
            resolução = resolução_arredondamento / zoom
            x = int((event.pos().x() + x_value * zoom) / zoom)
            x = arredondamentos.arredondar_int(x, resolução)
            y = int((event.pos().y() + y_value * zoom) / zoom)
            y = arredondamentos.arredondar_int(y, resolução)
            self.update()


        if(modo_escolhido == "selecionar"):
            tabela_arr = eventosTabela.ConteudosTabela_ARR(self.parent().table)
            for i, (poligono, _, nome_retangulo, dados_adicionais, buracos) in enumerate(self.poligonos[int(andar_atual)]):
                
                if poligono.containsPoint(event.pos(), Qt.OddEvenFill):
                    self.selected_rectangle_index = i
                    points = [poligono[i] for i in range(poligono.size())]
                    self.offset = event.pos() - points[0]
                    #self.resizing = True
                    posição = None
                    count = 0
                    for ambiente in tabela_arr:
                        nome_ambiente = ambiente[0]
                        if(nome_retangulo == nome_ambiente):
                            posição = count
                            
                        count+=1
                    print(posição)
                    self.parent().table.selectRow(posição)
                    break
            self.update()


        if(modo_escolhido == "arrastar"):
            for i, (poligono, _, nome_retangulo, dados_adicionais) in enumerate(self.poligonos[int(andar_atual)]):
                if poligono.contains(self.begin) and arrastar_ligado == True:
                    self.selected_rectangle_index = i
                    points = [poligono[i] for i in range(poligono.size())]
                    self.offset = event.pos() - points[0]
                    self.resizing = True
                    self.parent().table.selectRow(i)
                    break
            self.update()



    def mouseMoveEvent(self, event):
        global x_value, y_value, andar_atual
        andar = int(andar_atual)

        #responsavel por arrastar a tela
        if event.buttons() & QtCore.Qt.MiddleButton:
            self.diferença_x_arrastar_tela = (self.inicio_x_arrastar_tela - event.globalPos().x())/zoom
            self.diferença_y_arrastar_tela = (self.inicio_y_arrastar_tela - event.globalPos().y())/zoom
            x_value = int(self.diferença_x_arrastar_tela + self.ultimo_x_value)
            y_value = int(self.diferença_y_arrastar_tela + self.ultimo_y_value)
            self.parent().atualizar()

        if event.buttons() & QtCore.Qt.LeftButton:
            if(modo_escolhido == "retângulo" or modo_escolhido == "linha"):
                CURSOR_NEW = QtGui.QCursor(QtGui.QPixmap('cursor/drag.png'))
                self.setCursor(CURSOR_NEW) # muda o cursor 
                
            if self.selected_rectangle_index != -1 and self.resizing:
                print("Arrastando retângulo")
                poligono = self.poligonos[int(andar)][self.selected_rectangle_index][0]
                points = [poligono[i] for i in range(poligono.size())]
                ponto1 = event.pos() - points[0]
                delta = event.pos() - self.offset - ponto1
                poligono.translate(delta)
                
                
                self.poligonos[int(andar)][self.selected_rectangle_index][0]
        
                #self.rectangle[self.selected_rectangle_index] = (rect, self.rectangles[andar][self.selected_rectangle_index][1])
                #self.begin = event.pos()
                self.update()
                
            else:
                if(modo_escolhido == "retângulo"):
                    resolução = resolução_arredondamento / zoom *escala/100
                    x = self.begin.x()*zoom/escala*100 - x_value*zoom
                    x = arredondamentos.arredondar_int(x, resolução)
                    y = self.begin.y()*zoom/escala*100 - y_value*zoom
                    y = arredondamentos.arredondar_int(y, resolução)
                    x, y = self.PontoProximo(x,y)
                    posição__inicial = QtCore.QPoint(x, y)
                    x2, y2 = event.pos().x(), event.pos().y()
                    x2, y2 = self.PontoProximo(x2,y2)
                    self.posição__final = QtCore.QPoint(x2, y2)
                    
                    retangulo = QtCore.QRect(posição__inicial, self.posição__final)
                    cor = QtGui.QColor(12, 125, 125)
                    if len(self.rectangles[int(andar)])!= 0:
                        if self.rectangles[int(andar)][-1][2] == "temp":
                            self.rectangles[int(andar)].pop() # deleta a versão anterior do retangulo temporario
                    self.rectangles[int(andar)].append((retangulo, cor, "temp")) # trocar para salvar numa lista de itens temporarios da tela


                self.end = event.pos()
                self.update()
                
    def mouseDoubleClickEvent(self,event):
        print("clique duplo")
        if modo_escolhido == "selecionar":
            if(self.vista_contorno == False):
                resolução = resolução_arredondamento / zoom
                x = int((event.pos().x() + x_value * zoom) / zoom)
                x = arredondamentos.arredondar_int(x, resolução)
                y = int((event.pos().y() + y_value * zoom) / zoom)
                y = arredondamentos.arredondar_int(y, resolução)

                self.begin_sem_zoom = event.pos() + QtCore.QPoint(x, y)
                self.begin = QtCore.QPoint(x, y)
                print(self.begin)
                self.end = event.pos()
                for i, (poligono, _, nome_retangulo, dados_adicionais, buracos) in enumerate(self.poligonos[int(andar_atual)]):
                    if poligono.containsPoint (self.end, Qt.OddEvenFill):
                        self.selected_rectangle_index = i
                        self.parent().table.selectRow(i)
                self.update()
            if(self.vista_contorno == True):
                resolução = resolução_arredondamento / zoom
                x = int((event.pos().x() + x_value * zoom) / zoom)
                x = arredondamentos.arredondar_int(x, resolução)
                y = int((event.pos().y() + y_value * zoom) / zoom)
                y = arredondamentos.arredondar_int(y, resolução)

                self.begin_sem_zoom = event.pos() + QtCore.QPoint(x, y)
                self.begin = QtCore.QPoint(x, y)
                print(self.begin)
                self.end = event.pos()
                for i, (vertices_externos, buracos, dados_adicionais) in enumerate(self.condições_de_contorno[int(andar_atual)]):
                    interface = QtGui.QPolygon(vertices_externos)
                    if interface.containsPoint (self.end, Qt.OddEvenFill):
                        self.selected_rectangle_index = i
                        self.parent().table_horizontal.selectRow(i)
                self.update()                

    def mouseReleaseEvent(self, event):
        global x_value, y_value, zoom, resolução_arredondamento, modo_escolhido, andar_atual, coordenadas_linha90g
        x2= 0
        y2= 0
        andar = andar_atual

        #arrastar o poligono
        if event.button() == QtCore.Qt.LeftButton:
            if(modo_escolhido == "retângulo" or modo_escolhido == "linha"):

                self.setCursor(Qt.CrossCursor)
            
            #poe na nova posição
            if(self.resizing == True):

                #self.resizing = False
                x2 = event.pos().x()
                y2 = event.pos().y()


                x1 = self.begin.x()
                y1 = self.begin.y()

                delta_x = x2-x1
                delta_y = y2-y1

                delta_x = delta_x/escala/zoom
                delta_y = delta_y/escala/zoom

                delta_x_pixels = x2-x1 - self.offset.x()
                delta_y_pixels = y2-y1 - self.offset.y()
                i = self.selected_rectangle_index
                self.parent().mudar_coordenadas_ambiente(i, delta_x, delta_y, delta_x_pixels, delta_y_pixels, int(andar))
                resizing = False


        if modo_escolhido == "retângulo":
            print("Modo padrão de criação de retângulos ativado")
            if event.button() == QtCore.Qt.LeftButton:
                if self.selected_rectangle_index != -1:
                    self.selected_rectangle_index = -1
                    self.resizing = False
                else:
                    x2 = int((event.pos().x() + x_value * zoom) / zoom)
                    resolução = resolução_arredondamento / zoom
                    x2 = arredondamentos.arredondar_int(x2, resolução)
                    y2 = int((event.pos().y() + y_value * zoom) / zoom)
                    y2 = arredondamentos.arredondar_int(y2, resolução)
                    x2, y2 = self.PontoProximo(x2,y2)
                    coordenadas_finais = QtCore.QPoint(x2, y2)
                    x = int((self.begin.x() ) /escala*100)
                    x = arredondamentos.arredondar_int(x, resolução)
                    y = int((self.begin.y() ) /escala*100)
                    y = arredondamentos.arredondar_int(y, resolução)
                    coordenadas_iniciais = QtCore.QPoint(x, y)
                    cor = self.parent().gerar_cor()
                    self.QRetangulo(coordenadas_iniciais, coordenadas_finais, cor, andar)
                self.update()

        elif modo_escolhido == "linha90g":
            if event.button() == QtCore.Qt.LeftButton:
                if self.selected_rectangle_index != -1:
                    self.selected_rectangle_index = -1
                    self.resizing = False
                else:
                    resolução = resolução_arredondamento / zoom
                    x2 = int((event.pos().x() + x_value * zoom) / zoom)
                    x2 = arredondamentos.arredondar_int(x2, resolução)
                    y2 = int((event.pos().y() + y_value * zoom) / zoom)
                    y2 = arredondamentos.arredondar_int(y2, resolução)

                    x1 = self.begin.x()
                    y1 = self.begin.y()

                    #garante que teremos um retangulo quadrado fazendo o menor lado ter valor 0
                    if(abs(x2-x1) > abs(y2-y1)):
                        y2=y1
                    else:
                        x2=x1

                    coordenadas_finais = QtCore.QPoint(x2, y2)

                    retangulo = QtCore.QRect(self.begin, coordenadas_finais)
                    
                    cor = self.parent().gerar_cor()
                    
                    nome_novo_retangulo = self.parent().atualizar_tabela(retangulo, cor, "linha90g & retângulo", "", andar, "")
                    self.rectangles[int(andar)].append((retangulo, cor, nome_novo_retangulo))

            
            global coordenadas_linha90g
            if(x2 == self.primeiro_ponto_poligono[0] and y2 == self.primeiro_ponto_poligono[1]):
                cor = self.parent().gerar_cor()
                self.QPoligono(coordenadas_linha90g, cor, andar)

                coordenadas_linha90g = []
                self.primeiro_ponto_poligono = []

                
                    
            else:
                coordenadas = (x2,y2)
                coordenadas_linha90g.append(coordenadas)
              
                
                self.update()

        elif modo_escolhido == "linha":  
            if event.button() == QtCore.Qt.LeftButton:
                resolução = resolução_arredondamento / zoom
                x2 = int((event.pos().x()+x_value  * zoom) / zoom)
                x2 = arredondamentos.arredondar_int(x2, resolução)
                y2 = int((event.pos().y() +y_value * zoom) / zoom)
                y2 = arredondamentos.arredondar_int(y2, resolução)                    
                x2, y2 = self.PontoProximo(x2,y2)
                if self.selected_rectangle_index != -1:
                    self.selected_rectangle_index = -1
                    self.resizing = False
                elif not self.begin_linha.isNull():
                    coordenadas_finais = QtCore.QPoint(x2, y2)

                    cor = self.parent().gerar_cor()
                    ambiente = self.QLinha(self.begin_linha, coordenadas_finais, cor, andar)
                    ponto1_shapely = (shapely.Point(self.begin_linha.x(), self.begin_linha.y()), ambiente)
                    ponto2_shapely = (shapely.Point(x2, y2), ambiente)
                    self.pontos_existentes[int(andar)].extend([ponto1_shapely, ponto2_shapely])
                self.begin_linha = QtCore.QPoint(x2, y2)
    
            coordenadas = (x2,y2)
            x2, y2 = self.PontoProximo(x2,y2)
            if self.primeiro_ponto_poligono == []:
                self.primeiro_ponto_poligono = [x2,y2]
                coordenadas_linha90g.append(coordenadas)


            #Cria novo poligono quando fecha as retas
            if(x2 == self.primeiro_ponto_poligono[0] and y2 == self.primeiro_ponto_poligono[1] and len(coordenadas_linha90g)>1):
                cor = self.parent().gerar_cor()

                self.QPoligono(coordenadas_linha90g, cor, andar)

                coordenadas_linha90g = []
                self.primeiro_ponto_poligono = []
                self.begin = QtCore.QPoint()
                self.begin =QtCore.QPoint()
                self.begin_linha = QtCore.QPoint()
                self.begin_sem_zoom = QtCore.QPoint()
                self.end = QtCore.QPoint()

            else:
                coordenadas = (x2,y2)
                coordenadas_linha90g.append(coordenadas)
                self.update()

        # atualiza a tela com base na tabela
        self.parent().atualizar()



class AlterarMedidas(QDialog):
    def __init__(self, table_ambiente,  indice, parent):
        super().__init__(parent)


        
        self.table_ambiente = table_ambiente
        self.indice = indice
        arr = eventosTabela.ConteudosTabela_ARR(table_ambiente)
        vertices_str = arr[self.indice][7]
            
        # Layout
        layout = QtWidgets.QGridLayout()
        self.setLayout(layout)

        # Criando widgets
        self.label_verices = QtWidgets.QLabel("vertices:")
        self.textbox_vertices = QtWidgets.QPlainTextEdit()
        self.textbox_vertices.height = 40
        self.textbox_vertices.setPlainText(vertices_str)
        self.botao_alterar = QtWidgets.QPushButton("Alterar")
        self.botao_alterar.clicked.connect(self.Alterar)

        layout.addWidget(self.label_verices, 0,0)
        layout.addWidget(self.textbox_vertices, 0, 1)
        layout.addWidget(self.botao_alterar,1,0)



    def Alterar(self):
        global andar_atual
        #self.table_ambiente.setItem(self.indice, 7, QtWidgets.QTableWidgetItem(str("N/A")))
        #(1.4, 1.9),(2.8, 1.9),(2.8, 3.0),(1.4, 3.0)
        vertices_str = self.textbox_vertices.toPlainText()
        self.table_ambiente.setItem(self.indice, 7, QtWidgets.QTableWidgetItem(vertices_str))
        pontos_poligono_str = vertices_str.replace(" ","").split("),(")
        pontos_poligono = []

        poligono = QtGui.QPolygon()
        for ponto_str in pontos_poligono_str:
            ponto_str_divido = ponto_str.replace("(", "").replace(")", "").split(",")
            x_float = float(ponto_str_divido[0])
            y_float = float(ponto_str_divido[1])

            x = int(Transformações.AjusteCoordenada(x_float, x_value))
            y = int(Transformações.AjusteCoordenada(y_float, y_value))
            ponto_poligono = QtCore.QPoint(x, y)

            pontos_poligono.append(ponto_poligono)
        poligono = QtGui.QPolygon(pontos_poligono)
        self.parent().poligonos[int(andar_atual)][self.indice][0] = poligono
        self.close()


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    window = MainWindow()   

    

    window.setWindowTitle("Refrigeration Studio (release)")

    tema_pasta = "config/interface.txt"
    if tema_pasta:
        with open(tema_pasta, 'r') as file:
            text = file.read()
            linhas = text.split("\n")
            for linha in linhas:
                if("debug" in linha and "True" in linha):
                    debug = True
                    window.setWindowTitle("Refrigeration Studio (Debug State)")

    window.show()
    app.exec_()
