import sys
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QGridLayout, QLabel, QScrollArea, QFrame
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
from matplotlib.widgets import Cursor, MultiCursor
from PyQt5 import QtWidgets, QtGui, QtCore, QtPrintSupport
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QAction, QFileDialog
import matplotlib as mpl
import matplotlib
import parametros
import scipy.spatial as spatial
from fpdf import FPDF
import tkinter as tk
from tkinter import filedialog
import pandas as pd
from scipy import interpolate
import json

taxa_kwh_reais = None

graficos_debug = False


idioma = parametros.linguagem() + "_relatorio"
textos_relatorio_diario = {}
textos_relatorio_anual = {}
# Opening JSON file
with open('data/interface.json', encoding='utf8') as json_file:
    data = json.load(json_file)
    textos_relatorio = data[idioma]
    textos_relatorio_diario = textos_relatorio["diario"]
    textos_relatorio_anual = textos_relatorio["anual"]


def RelatorioDia_Iniciar(unidade_grafico_tempo, Tempo_arr, Temperatura_arr, Temperatura_externa, Temperatura_solo, calorInserido_arr, deltaQrefrigeracao_arr, calorEquipamentos_arr, calor_total_removido_por_dia_arr, energia_gasta_por_dia_arr, COP, ventilação_minima, Rb_arr, Hb_arr, Rb2_arr, _taxa_kwh_reais, ACH_min_ashrae, volume_total_m3, ACH_troca_de_ar_h, calorInserido_janela_porta_arr,calorInseridoUnicamenteParede, calorInseridoUnicamenteAtmosfera , calorInserido_solo):
    global taxa_kwh_reais
    taxa_kwh_reais = _taxa_kwh_reais
    window = RelatorioDia(unidade_grafico_tempo, Tempo_arr, Temperatura_arr, Temperatura_externa, Temperatura_solo, calorInserido_arr, deltaQrefrigeracao_arr, calorEquipamentos_arr, calor_total_removido_por_dia_arr, energia_gasta_por_dia_arr, COP, ventilação_minima,Rb_arr, Hb_arr, Rb2_arr, ACH_min_ashrae, volume_total_m3, ACH_troca_de_ar_h, calorInserido_janela_porta_arr, calorInseridoUnicamenteParede, calorInseridoUnicamenteAtmosfera , calorInserido_solo)   
    return window

def RelatorioAno_Iniciar(unidade_grafico_tempo, Tempo_arr, Temperatura_arr, Temperatura_externa, Temperatura_solo, calorInserido_arr, deltaQrefrigeracao_arr, calorEquipamentos_arr, calor_total_removido_por_dia_arr, energia_gasta_por_dia_arr, COP, potencia_max, dia_potencia_max, mes_potencia_max, ventilação_minima, _taxa_kwh_reais, ACH_min_ashrae, volume_total_m3, ACH_troca_de_ar_h, energia_gasta_mes_arr):
    global taxa_kwh_reais
    taxa_kwh_reais = _taxa_kwh_reais
    window = RelatorioAno(unidade_grafico_tempo, Tempo_arr, Temperatura_arr, Temperatura_externa, Temperatura_solo, calorInserido_arr, deltaQrefrigeracao_arr, calorEquipamentos_arr, calor_total_removido_por_dia_arr, energia_gasta_por_dia_arr, COP, potencia_max, dia_potencia_max, mes_potencia_max, ventilação_minima, ACH_min_ashrae, volume_total_m3, ACH_troca_de_ar_h, energia_gasta_mes_arr)   
    return window

class RelatorioDia(QMainWindow):
    def __init__(self, unidade_grafico_tempo, Tempo_arr, Temperatura_arr, Temperatura_externa, Temperatura_solo, calorInserido_arr, deltaQrefrigeracao_arr, calorEquipamentos_arr, calor_total_removido_por_dia_arr, energia_gasta_por_dia_arr, COP, ventilação_minima, Rb_arr, Hb_arr, Rb2_arr, ACH_min_ashrae, volume_total_m3, ACH_troca_de_ar_h, calorInserido_janela_porta_arr, calorInseridoUnicamenteParede, calorInseridoUnicamenteAtmosfera , calorInserido_solo):
        super().__init__()
        self.ACH_min_ashrae, self.volume_total_m3 =  ACH_min_ashrae, volume_total_m3
        self.ventilação_minima = ventilação_minima
        self.ACH_real_h = ACH_troca_de_ar_h

        # Cria o widget principal
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)

        # Define o layout principal
        self.layout = QVBoxLayout()
        self.main_widget.setLayout(self.layout)

        # Cria a aba principal
        self.tab_widget = QTabWidget()
        self.layout.addWidget(self.tab_widget)

        # Adiciona abas (substitua por suas abas personalizadas)
        page = QWidget(self.tab_widget)
        self.page_layout = QGridLayout()
        page.setLayout(self.page_layout)

        # Adiciona a página a um QScrollArea
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(page)

        self.tab_widget.addTab(scroll_area, 'Resumo')

        self.gerarpdfAction = QtWidgets.QPushButton(textos_relatorio_diario["gerar pdf"], self)
        self.gerarpdfAction.clicked.connect(lambda: self.GerarPDF(['temp/relatorio/plots.png'], [texto1]))
        self.page_layout.addWidget(self.gerarpdfAction)
        # Adiciona o texto antes do gráfico
        texto1 = self.TextosRelatorio(unidade_grafico_tempo, Tempo_arr, Temperatura_arr, Temperatura_externa, Temperatura_solo, calorInserido_arr, deltaQrefrigeracao_arr, calorEquipamentos_arr, calor_total_removido_por_dia_arr, energia_gasta_por_dia_arr, COP)
        text_before = QLabel(texto1)
        self.page_layout.addWidget(text_before)

        canvas = None
        # Chama o método para adicionar o gráfico
        canvas = self.Graficos(unidade_grafico_tempo, Tempo_arr, Temperatura_arr, Temperatura_externa, Temperatura_solo, calorInserido_arr, deltaQrefrigeracao_arr, calorEquipamentos_arr, Rb_arr, Hb_arr, Rb2_arr, calorInserido_janela_porta_arr, calorInseridoUnicamenteParede, calorInseridoUnicamenteAtmosfera , calorInserido_solo)


        # Adiciona o gráfico ao layout da página
        self.page_layout.addWidget(canvas)

        # Adiciona o texto depois do gráfico
        text_after = QLabel("Encerrado Relatório.")
        self.page_layout.addWidget(text_after)

        # Define a janela principal
        self.setCentralWidget(self.main_widget)

        





    

    def TextosRelatorio(self, unidade_grafico_tempo, Tempo_arr, Temperatura_arr, Temperatura_externa, Temperatura_solo, calorInserido_arr, deltaQrefrigeracao_arr, calorEquipamentos_arr, calor_total_removido_por_dia_arr, energia_gasta_por_dia_arr, COP):

        print(np.mean(energia_gasta_por_dia_arr))
        gasto_diario_energiakwH = np.mean(energia_gasta_por_dia_arr) / (3.6 *pow(10,6))   #J/d ->kwh/d = 
        potencia_max_necessaria = np.max(calorInserido_arr)
        texto = textos_relatorio_diario["vol total"] + str(round(self.volume_total_m3,2)) + " m3\n"
        texto += textos_relatorio_diario["potencia max"] + str(round(potencia_max_necessaria,2)) + " J/s\n"
        texto += textos_relatorio_diario["ventilação minima ashrae"] + str(self.ventilação_minima) + textos_relatorio_diario["ventilação minima ashrae 2"]
        texto += textos_relatorio_diario["renovação minima ashrae"] + str(round(self.ACH_min_ashrae,3)) + textos_relatorio_diario["renovação minima ashrae 2"]
        texto += textos_relatorio_diario["ach real"] + str(self.ACH_real_h) + "\n"
        texto += textos_relatorio_diario["tarifa base"] + str(taxa_kwh_reais) + "\n"
        texto += "COP: " +  str(COP) + "\n"
        texto += textos_relatorio_diario["gasto diario"] + str(round(gasto_diario_energiakwH,3)) + textos_relatorio_diario["gasto diario 2"] + str(round(taxa_kwh_reais*gasto_diario_energiakwH, 3)) +"\n"
        np.max(calorInserido_arr)
        return texto




        
        #self.Relatorio_dia(self, Tempo_arr, Temperatura_arr, Temperatura_externa, Temperatura_solo, calorInserido_arr, deltaQrefrigeracao_arr, calorEquipamentos_arr)
    def Graficos(self,unidade_grafico_tempo, Tempo_arr, Temperatura_arr, Temperatura_externa, Temperatura_solo, calorInserido_arr, deltaQrefrigeracao_arr, calorEquipamentos_arr, Rb_arr, Hb_arr, Rb2_arr, calorInserido_janela_porta_arr, calorInseridoUnicamenteParede, calorInseridoUnicamenteAtmosfera , calorInserido_solo):
        # Criando o gráfico
        numero_graficos = 3
        if(parametros.debug == True and graficos_debug == True):
            numero_graficos = 5
        fig, axs = plt.subplots(numero_graficos, 1, figsize=(10, 6))
        Tempo_arr = Tempo_arr/60

        # Plotagem dos dados


        axs[0].plot(Tempo_arr, Temperatura_arr, label=textos_relatorio_diario["Temperatura interna"])
        axs[0].plot(Tempo_arr, Temperatura_externa, label=textos_relatorio_diario["Temperatura externa"])
        axs[0].plot(Tempo_arr, Temperatura_solo, label=textos_relatorio_diario["Temperatura solo"])
        axs[1].plot(Tempo_arr, calorInserido_arr, label=textos_relatorio_diario["Calor inserido"])
        axs[1].plot(Tempo_arr, deltaQrefrigeracao_arr, label=textos_relatorio_diario["Refrigeração"])
        axs[1].plot(Tempo_arr, calorEquipamentos_arr, label=textos_relatorio_diario["Pessoas + equipamentos"])
        axs[2].plot(Tempo_arr, calorInserido_arr, label = textos_relatorio_diario["Calor total"],  linewidth=3)
        axs[2].plot(Tempo_arr, calorEquipamentos_arr, label = textos_relatorio_diario["Calor equipamentos"])
        axs[2].plot(Tempo_arr, calorInserido_janela_porta_arr, label = textos_relatorio_diario["Calor através janela"])
        axs[2].plot(Tempo_arr, calorInseridoUnicamenteAtmosfera, label = textos_relatorio_diario["Calor através do sol"])
        axs[2].plot(Tempo_arr, calorInserido_solo, label = textos_relatorio_diario["calor através solo"])
        axs[2].plot(Tempo_arr, calorInseridoUnicamenteParede, label = textos_relatorio_diario["calor através das paredes"])
        #amaciando as curvas
        #xnew = np.linspace(Tempo_arr.min(), Tempo_arr.max(), len(Tempo_arr/10))  
        x_lista = []
        y_lista = []
        y_temp = []
        x_temp = []
        for i in range(len(Tempo_arr)-1):
            y_temp.append(deltaQrefrigeracao_arr[i])
            x_temp.append(i)
            if(i%20 == 0):
                y = np.sum(y_temp)/20
                y_lista.append(y)
                x_lista.append(Tempo_arr[i])
                y_temp = []
                x_temp = []
        
        tck_s = interpolate.splrep(np.array(x_lista), np.array(y_lista), s=len(x_lista) )
        xnew = np.array(x_lista)
        axs[1].plot(xnew, interpolate.BSpline(*tck_s)(xnew), '--', label='Média de Refrigeração', linewidth=3,  c='b')


        # Ajustando rótulos e legendas
        axs[0].set_xlabel('Tempo [' + unidade_grafico_tempo + ']')
        axs[0].set_ylabel('Temperatura [°C]')
        axs[0].set_xticks(np.arange(0, 24, 1))
        # Enabling minor grid lines:
        axs[0].grid(which = "major", linewidth = 1)
        axs[0].grid(which = "minor", linewidth = 0.2)
        axs[0].minorticks_on()
        
        axs[1].set_xlabel('Tempo [' + unidade_grafico_tempo + ']')
        axs[1].set_ylabel('Calor [J/s]')
        axs[1].set_xticks(np.arange(0, 24, 1))

        axs[2].set_xlabel('Tempo [' + unidade_grafico_tempo + ']')
        axs[2].set_ylabel('Calor [J/s]')
        axs[2].set_xticks(np.arange(0, 24, 1)) 

        axs[0].legend()
        axs[1].legend()
        axs[2].legend()
        # Ajustando títulos
        axs[0].set_title('Temperatura interna')
        axs[1].set_title('Calor inserido vs Calor removido ')
        axs[2].set_title('Calor inserido por fontes ')
        # Ajustando a grade
        axs[0].grid(True)
        axs[1].grid(True)
        axs[2].grid(True)
        #cursor

        if(parametros.debug == True and graficos_debug == True):
            axs[2].plot(Tempo_arr, Rb_arr, 'o', label="Rb", markersize=1)
            axs[2].grid(True)
            axs[2].set_xticks(np.arange(0, 24, 1))
            axs[3].plot(Tempo_arr, Hb_arr, 'o', label="Hb", markersize=1)
            axs[3].grid(True)
            axs[3].set_xticks(np.arange(0, 24, 1))
            axs[4].plot(Tempo_arr, Rb2_arr, 'o', label="Rb2", markersize=1)
            axs[4].grid(True)
            axs[4].set_xticks(np.arange(0, 24, 1))
        #ponto de max
        hora_carga_max = Tempo_arr[np.argmax(calorInserido_arr)]
        
        carga_max = calorInserido_arr.max()
        text= "{:.1f}h , Carga={:.1f} J/s".format(hora_carga_max, carga_max)

        axs[1].annotate(text, xy=(hora_carga_max, carga_max), xytext=(hora_carga_max, carga_max+5),
            arrowprops=dict(facecolor='black', shrink=1),
            )

        # Cria um objeto FigureCanvas
        canvas = FigureCanvas(fig)

        fig.savefig('temp/relatorio/plots.png') #salva os graficos



        # canvas.setCursor(QtGui.QCursor(QtCore.Qt.CrossCursor))
        # canvas.setCursor(QtCore.Qt.CrossCursor)
        # cursor = mpl.widgets.Cursor(axs[0], useblit=True, color='red', linewidth=2)
        canvas_frame = QFrame()
        layout = QtWidgets.QGridLayout()
        layout.setRowMinimumHeight(0, numero_graficos*500) #altura do grafico
        layout.addWidget(canvas,0,0)
        layout.geometry()
        canvas_frame.setLayout(layout)
        coleção_cursor = []
        cursor = FollowDotCursor(axs[0], Tempo_arr, Temperatura_arr, tolerance=20)
        cursor = FollowDotCursor(axs[1], Tempo_arr, calorInserido_arr, tolerance=20)
        return canvas_frame
    

    #GERA PDF
    def GerarPDF(self, imagens, textos):
        fileName_txt, _ = QFileDialog.getSaveFileName(self, "Salvar Arquivo", "", "Arquivos de PDF (*.pdf)")
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font('arial','', 10)
        pdf.multi_cell(150,7,textos[0])
        pdf.image(imagens[0], 10, 100, w=180, h=120)
        pdf.output(fileName_txt, 'F')

class RelatorioAno(QMainWindow):
    def __init__(self, unidade_grafico_tempo, Tempo_arr, Temperatura_arr, Temperatura_externa, Temperatura_solo, calorInserido_arr, deltaQrefrigeracao_arr, calorEquipamentos_arr, calor_total_removido_por_dia_arr, energia_gasta_por_dia_arr, COP, potencia_max, dia_potencia_max, mes_potencia_max, ventilação_minima, ACH_min_ashrae, volume_total_m3, ACH_troca_de_ar_h, energia_gasta_mes_arr):
        super().__init__()
        self.ventilação_minima = ventilação_minima
        self.ACH_min_ashrae, self.ACH_real_h, self.volume_total_m3 = ACH_min_ashrae, ACH_troca_de_ar_h, volume_total_m3



        # Cria o widget principal
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)

        # Define o layout principal
        self.layout = QVBoxLayout()
        self.main_widget.setLayout(self.layout)

        # Cria a aba principal
        self.tab_widget = QTabWidget()
        self.layout.addWidget(self.tab_widget)

        # Adiciona abas (substitua por suas abas personalizadas)
        page = QWidget(self.tab_widget)
        self.page_layout = QVBoxLayout()
        page.setLayout(self.page_layout)

        # Adiciona a página a um QScrollArea
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(page)

        self.tab_widget.addTab(scroll_area, 'Resumo')

        self.gerarpdfAction = QtWidgets.QPushButton(textos_relatorio_anual["gerar pdf"], self)
        self.gerarpdfAction.clicked.connect(lambda: self.GerarPDF(['temp/relatorio/plots.png'], [texto1]))
        self.page_layout.addWidget(self.gerarpdfAction)

        self.gerarpdfAction = QtWidgets.QPushButton(textos_relatorio_anual["gerar pdf"], self)
        self.gerarpdfAction.clicked.connect(lambda: self.GerarPDF(['temp/relatorio/plots.png'], [texto1]))
        self.page_layout.addWidget(self.gerarpdfAction)

        # Adiciona o texto antes do gráfico
        texto1 =  self.TextosRelatorio(unidade_grafico_tempo, Tempo_arr, Temperatura_arr, Temperatura_externa, Temperatura_solo, calorInserido_arr, deltaQrefrigeracao_arr, calorEquipamentos_arr, calor_total_removido_por_dia_arr, energia_gasta_por_dia_arr, COP, potencia_max, dia_potencia_max, mes_potencia_max)
        text_before = QLabel(texto1)
        self.page_layout.addWidget(text_before)

        canvas = None
        # Chama o método para adicionar o gráfico
        canvas = self.Graficos(unidade_grafico_tempo, Tempo_arr, Temperatura_arr, Temperatura_externa, Temperatura_solo, calorInserido_arr, deltaQrefrigeracao_arr, calorEquipamentos_arr, energia_gasta_mes_arr)
        # Adiciona o gráfico ao layout da página
        self.page_layout.addWidget(canvas)

        text_after_str = "Encerrado Relatório."
        text_after = QLabel(text_after_str)
        self.page_layout.addWidget(text_after)

        # Define a janela principal
        self.setCentralWidget(self.main_widget)
        

        
    def TextosRelatorio(self, unidade_grafico_tempo, Tempo_arr, Temperatura_arr, Temperatura_externa, Temperatura_solo, calorInserido_arr, deltaQrefrigeracao_arr, calorEquipamentos_arr, calor_total_removido_por_dia_arr, energia_gasta_por_dia_arr, COP, potencia_max, dia_potencia_max, mes_potencia_max):
        calor_max = np.max(calorInserido_arr)
        dia_calor_max = Tempo_arr[np.argmax(calorInserido_arr)]
        gasto_diario_energiakwH = np.mean(energia_gasta_por_dia_arr) / (3.6 *pow(10,6))   #J/d ->kwh/d = 
        gasto_anual_energia = gasto_diario_energiakwH*365
        texto = textos_relatorio_anual["vol total"] + str(round(self.volume_total_m3,2)) + " m3\n"
        texto += textos_relatorio_anual["potencia max"] + str(round(potencia_max,2)) + textos_relatorio_anual["potencia max2"] + str(dia_potencia_max) + "/" + str(mes_potencia_max) +"\n"
        texto += textos_relatorio_anual["Carga média máxima"].format(calor_max, dia_calor_max)
        texto += textos_relatorio_anual["ventilação minima ashrae"] + str(round(self.ventilação_minima,2)) +textos_relatorio_anual["ventilação minima ashrae 2"]
        texto += textos_relatorio_anual["renovação minima ashrae"] + str(round(self.ACH_min_ashrae,2)) + textos_relatorio_anual["renovação minima ashrae 2"]
        texto += textos_relatorio_anual["ach real"] + str(self.ACH_real_h) + "\n"
        texto += textos_relatorio_anual["tarifa base"] + str(taxa_kwh_reais) 
        texto += "\nCOP: " +  str(COP) 
        texto += textos_relatorio_anual["gasto diario"] + str(round(gasto_diario_energiakwH,3)) + textos_relatorio_anual["gasto diario 2"] + str(round(taxa_kwh_reais*gasto_diario_energiakwH, 2)) +"\n"
        texto += textos_relatorio_anual["gasto anual"] + str(round(gasto_anual_energia,0)) + textos_relatorio_anual["gasto anual 2"] + str(round(taxa_kwh_reais*gasto_anual_energia,2)) +"\n"
        return texto
    
    def Graficos(self, unidade_grafico_tempo, Tempo_arr, Temperatura_arr, Temperatura_externa, Temperatura_solo, calorInserido_arr, deltaQrefrigeracao_arr, calorEquipamentos_arr, energia_gasta_mes_arr):
 


        # Criando o gráfico
        numero_graficos = 3
        if(parametros.debug == True and graficos_debug == True):
            numero_graficos = 5
        fig, axs = plt.subplots(numero_graficos, 1, figsize=(10, 6))

        # Plotagem dos dados
        axs[0].plot(Tempo_arr, Temperatura_arr, label=textos_relatorio_anual["Temperatura interna"])
        axs[0].plot(Tempo_arr, Temperatura_externa, label=textos_relatorio_anual["Temperatura externa"])
        if (len(Temperatura_solo)!=0): #nem sempre teremos o dado do solo
            axs[0].plot(Tempo_arr, Temperatura_solo, label=textos_relatorio_anual['Temperatura do solo'])
        axs[1].plot(Tempo_arr, calorInserido_arr, label=textos_relatorio_anual['Calor inserido'])
        axs[1].plot(Tempo_arr, deltaQrefrigeracao_arr, label=textos_relatorio_anual['Refrigeração'])

        # Ajustando rótulos e legendas
        axs[0].set_xlabel(textos_relatorio_anual['Tempo [dias]'])
        axs[0].set_ylabel(textos_relatorio_anual['temperatura'])
        axs[1].set_xlabel(textos_relatorio_anual['Tempo [dias]'])
        axs[1].set_ylabel(textos_relatorio_anual['calor'])

        axs[0].legend()
        axs[1].legend()

        # Ajustando títulos
        axs[0].set_title(textos_relatorio_anual["Temperatura interna"])
        axs[1].set_title(textos_relatorio_anual["calor inserido x calor removido"])

        # Ajustando a grade
        axs[0].grid(True)
        axs[1].grid(True)

        dia_temp_max = Tempo_arr[np.argmax(Temperatura_externa)]
        temp_max = Temperatura_externa.max()
        text= textos_relatorio_anual["data_mais_quente_grafico"].format(dia_temp_max, temp_max)
        axs[0].annotate(textos_relatorio_anual["dia_mais_quente_grafico"], xy=(dia_temp_max, temp_max), xytext=(0.94,0.96))
        axs[0].annotate(text, xy=(dia_temp_max, temp_max), xytext=(dia_temp_max, temp_max+5),
            arrowprops=dict(facecolor='black', shrink=1),
            )

        i=0
        for item in energia_gasta_mes_arr:
            energia_gasta_mes_arr[i] = energia_gasta_mes_arr[i]/ (3.6 *pow(10,6))   #J/d ->kwh/d = 
            i+=1
        # Plotar as somas
        axs[2].bar(np.arange(12), energia_gasta_mes_arr)
        axs[2].set_xticks(np.arange(12), textos_relatorio_anual["meses_nomes"])
        axs[2].set_xlabel(textos_relatorio_anual["meses"])

        
        

        fig.savefig('temp/relatorio/plots.png') #salva os graficos


        # Cria um objeto FigureCanvas
        canvas = FigureCanvas(fig)

        # canvas.setCursor(QtGui.QCursor(QtCore.Qt.CrossCursor))
        # canvas.setCursor(QtCore.Qt.CrossCursor)
        # cursor = mpl.widgets.Cursor(axs[0], useblit=True, color='red', linewidth=2)
        canvas_frame = QFrame()
        layout = QtWidgets.QGridLayout()
        layout.setRowMinimumHeight(0, numero_graficos*800) #altura do grafico
        layout.addWidget(canvas,0,0)
        layout.geometry()
        canvas_frame.setLayout(layout)
        coleção_cursor = []
        cursor = FollowDotCursor(axs[0], Tempo_arr, Temperatura_arr, tolerance=20)
        cursor = FollowDotCursor(axs[1], Tempo_arr, calorInserido_arr, tolerance=20)
        return canvas_frame
    

    #GERA PDF
    def GerarPDF(self, imagens, textos):
        fileName_txt, _ = QFileDialog.getSaveFileName(self, "Salvar Arquivo", "", "Arquivos de PDF (*.pdf)")
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font('arial','', 10)
        pdf.multi_cell(150,7,textos[0])
        pdf.image(imagens[0], 10, 100, w=180, h=120)
        pdf.output(fileName_txt, 'F')





#GERENCIA OS CURSORES NO GRÁFICO
#https://stackoverflow.com/questions/20637113/possible-to-make-labels-appear-when-hovering-over-a-point-in-matplotlib-in-stem
#https://stackoverflow.com/questions/44726280/include-matplotlib-in-pyqt5-with-hover-labels
def fmt(x, y):
    return 'x: {x:0.2f}\ny: {y:0.2f}'.format(x=x, y=y)
class FollowDotCursor(object):
    """Display the x,y location of the nearest data point.
    https://stackoverflow.com/a/4674445/190597 (Joe Kington)
    https://stackoverflow.com/a/13306887/190597 (unutbu)
    https://stackoverflow.com/a/15454427/190597 (unutbu)
    """
    def __init__(self, ax, x, y, tolerance=5, formatter=fmt, offsets=(-20, 20)):
        try:
            x = np.asarray(x, dtype='float')
        except (TypeError, ValueError):
            x = np.asarray(mdates.date2num(x), dtype='float')
        y = np.asarray(y, dtype='float')
        mask = ~(np.isnan(x) | np.isnan(y))
        x = x[mask]
        y = y[mask]
        self._points = np.column_stack((x, y))
        self.offsets = offsets
        y = y[np.abs(y-y.mean()) <= 3*y.std()]
        self.scale = x.ptp()
        self.scale = y.ptp() / self.scale if self.scale else 1
        self.tree = spatial.cKDTree(self.scaled(self._points))
        self.formatter = formatter
        self.tolerance = tolerance
        self.ax = ax
        self.fig = ax.figure
        self.ax.xaxis.set_label_position('top')
        self.dot = ax.scatter(
            [x.min()], [y.min()], s=130, color='green', alpha=0.7)
        self.annotation = self.setup_annotation()
        plt.connect('motion_notify_event', self)

    def scaled(self, points):
        points = np.asarray(points)
        return points * (self.scale, 1)

    def __call__(self, event):
        ax = self.ax
        # event.inaxes is always the current axis. If you use twinx, ax could be
        # a different axis.
        if event.inaxes == ax:
            x, y = event.xdata, event.ydata
        elif event.inaxes is None:
            return
        else:
            inv = ax.transData.inverted()
            x, y = inv.transform([(event.x, event.y)]).ravel()
        annotation = self.annotation
        x, y = self.snap(x, y)
        annotation.xy = x, y
        annotation.set_text(self.formatter(x, y))
        self.dot.set_offsets(np.column_stack((x, y)))
        bbox = self.annotation.get_window_extent()
        self.fig.canvas.blit(bbox)
        self.fig.canvas.draw_idle()

    def setup_annotation(self):
        """Draw and hide the annotation box."""
        annotation = self.ax.annotate(
            '', xy=(0, 0), ha = 'right',
            xytext = self.offsets, textcoords = 'offset points', va = 'bottom',
            bbox = dict(
                boxstyle='round,pad=0.5', fc='yellow', alpha=0.75),
            arrowprops = dict(
                arrowstyle='->', connectionstyle='arc3,rad=0'))
        return annotation

    def snap(self, x, y):
        """Return the value in self.tree closest to x, y."""
        dist, idx = self.tree.query(self.scaled((x, y)), k=1, p=1)
        try:
            return self._points[idx]
        except IndexError:
            # IndexError: index out of bounds
            return self._points[0]
        


if __name__ == '__main__':
    texto = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Etiam eget ligula eu lectus lobortis condimentum. Aliquam nonummy auctor massa. Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas. Nulla at risus. Quisque purus magna, auctor et, sagittis ac, posuere eu, lectus. Nam mattis, felis ut adipiscing."
    textos = [texto]
    imagens = ['temp/relatorio/plots.png']
    GerarPDF(imagens, textos)
    print("Feito")