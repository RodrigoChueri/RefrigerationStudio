import eventosTabela
from PyQt5 import QtWidgets
import math
from Espaço import Espaço
from ZonaTermica import ZonaTermica
import matplotlib.pyplot as plt
import numpy as np
import arquivo_climatico
import time
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import calendar
from statistics import mean 
import eventosTabela
from PyQt5.QtCore import pyqtSignal
from progressbar import ProgressBar
from tqdm import tqdm
import tkinter as tk
from tkinter import ttk
from tkinter import *
import multiprocessing
from tkinter.ttk import *
import os
import threading
import subprocess
import angulo_solar
from threading import Thread
import relatorio
import parametros
import angulo_solar2

print("Carregando módulo de simulação...")

# algoritmo de cálculo de coeficiente 'h' de convecção
modo_Hc_opções_externo = ["J.A. Palyvos", "Emmel2007"]
modo_Hc_externo = modo_Hc_opções_externo[0]
modo_Hc_opções_interno = ["constante"]
modo_Hc_interno = modo_Hc_opções_interno[0]
modo_Hc_opções_solo = ["mil"]
modo_Hc_solo = modo_Hc_opções_solo[0]

# dia ano que exigiu a potencia max
dia_potencia_max = 0
mes_potencia_max = 0
potencia_max = 0


#geografia
Latitude_g = -23 #graus
Latitude_rad = Latitude_g/360*2*math.pi
cos_latitude = math.cos(Latitude_rad)



#constantes
ctrStefanBoltzmann = 5.67*pow(10,-8)
helio_crede = False  #livro instalaoes-de-ar-condicionado-helio-crede tabela 3.6
sol_air = True
COP = None


#condições iniciais
T_inicial_interno = None # °C

#especificação paredes e horizontais
k_parede_interna = None # W/mK 
k_parede_externa = None # W/mK 
k_parede_divisória = None # W/mK 
espessura_parede_interna = None # m
espessura_parede_externa = None # m
espessura_parede_divisória = None # m
espessura_horizontal = None # m


metodo_calculo_temp_solo, temp_solo_cte = "", None

#configurações de simulação
delta_Tempo = 15 #s
tempo_total_simulação = 86400 #seg #86400 é um dia
unidade_grafico_tempo = "min"
modificador_unidade_tempo = 1
if(unidade_grafico_tempo == "seg"):
    modificador_unidade_tempo = 1
if(unidade_grafico_tempo == "min"):
    modificador_unidade_tempo = 60
if(unidade_grafico_tempo == "h"):
    modificador_unidade_tempo = 3600
    
#refrigeração
segundo_inicial, segundo_final = 0, 86400 #horario de funcionamento do ar condicionado
compressão_convensional_ou_inverter = "inverter (controle proporcional)" # "inverter" ou "convencional"
T_desejada = None
diferencial_Temperatura_toleado_sistema_convencional = None # usado para sistema on-off, onde por exemplo se a temperatura desejada é 25 e essa variavel é 1.5 a temp pode chegar a 26.5
amplitude_temperatura_Inverter = None
T_min_Inverter = None

valores_salvos = pyqtSignal(str, str)  # Sinal personalizado


class Laterais:
    
    def __init__(self):
        self.historico = arquivo_climatico.Historico()
        self.Angulo_Solar2 = angulo_solar2.AnguloSolar()
        self.ContinuarSimulação = True
        self.ventilação_minima = None
        self.zonaTermica = None
        #limpar barras de progresso
        with open("temp/progresso.txt", "w") as arquivo:
            valor = "0"
            arquivo.write(valor)

            arquivo.close()




    
        #para encerrar a barra de progresso
        self.i_barra_progresso = 999999

    def Iniciar(self, tables_dicionario, pé_direito, potencia_maxima, tipo_simulação, dia_, mes_, adicionais, qualidade_simulacao_text, latitude_graus, unidade_potencia, COP_, paredes_default, temperatura_desejada, taxa_kwh_reais, ACH_troca_de_ar_h, horas_hvac, andar_terreo, angulo_N_geral, tipo_compressor_hvac, temperatura_limite_inferior, refrigeração_ideal, somente_iterar, metodo_calculo_temp_solo_, temp_solo_cte_):
        global segundo_inicial, segundo_final
        global dia, mês, Latitude_g, Latitude_rad, cos_latitude, COP
        global k_parede_interna, k_parede_externa, k_parede_divisória, espessura_parede_interna, espessura_parede_externa, espessura_parede_divisória,espessura_horizontal
        global T_desejada, T_min_Inverter, amplitude_temperatura_Inverter
        global diferencial_Temperatura_toleado_sistema_convencional
        global compressão_convensional_ou_inverter
        global metodo_calculo_temp_solo, temp_solo_cte
        self.on_off_ligado = None
        metodo_calculo_temp_solo = metodo_calculo_temp_solo_
        temp_solo_cte = temp_solo_cte_
        compressão_convensional_ou_inverter = tipo_compressor_hvac
        self.angulo_N_geral = angulo_N_geral
        Qtabela_paredes, Qtabela_ambientes,Qtable_horizontal, Qtable_equipamentos = tables_dicionario["Qtabela_paredes"], tables_dicionario["Qtabela_ambientes"], tables_dicionario["Qtable_horizontal"], tables_dicionario["Qtable_equipamentos"]
        self.Qtabela_janelas_portas = tables_dicionario["Qtabela_janelas_portas"]
        self.espessura_entre_pisos = float(paredes_default["interfaces_horizontais"]["espessura"])
        self.andar_terreo = andar_terreo
        self.pé_direito = pé_direito
        hora_inicial, minuto_inicial, hora_final, minuto_final = horas_hvac["hora_inicial"],horas_hvac["minuto_inicial"],horas_hvac["hora_final"],horas_hvac["minuto_final"]
        self.somente_iterar=somente_iterar

        #encontra as temperaturas inferior e setpoint(inverter)/superior(on-off)
        T_desejada = temperatura_desejada
        diferencial_Temperatura_toleado_sistema_convencional = T_desejada-temperatura_limite_inferior # usado para sistema on-off, onde por exemplo se a temperatura desejada é 25 e essa variavel é 1.5 a temp pode chegar a 26.5
        
        T_min_Inverter = T_desejada-abs(diferencial_Temperatura_toleado_sistema_convencional)
        amplitude_temperatura_Inverter = diferencial_Temperatura_toleado_sistema_convencional
        #encontra potencia ideal para um sistema split (on-off)
        # if(refrigeração_ideal == True  and tipo_simulação != "Ano"):
        #     tipo_compressor_original = tipo_compressor_hvac
        #     tipo_compressor_hvac_2 = "inverter (controle ideal)"
        #     somente_iterar2 = True
        #     refrigeração_ideal = False
        #     potencia_maxima = 1.0*self.Iniciar(tables_dicionario, pé_direito, potencia_maxima, tipo_simulação, dia_, mes_, adicionais, qualidade_simulacao_text, latitude_graus, unidade_potencia, COP_, paredes_default, temperatura_desejada, taxa_kwh_reais, ACH_troca_de_ar_h, horas_hvac, andar_terreo, angulo_N_geral, tipo_compressor_hvac_2, temperatura_limite_inferior, refrigeração_ideal, somente_iterar2, metodo_calculo_temp_solo, temp_solo_cte)
        #     self.somente_iterar = False
        #     compressão_convensional_ou_inverter = tipo_compressor_original
            
            
        # #retorna ao 
        # if(refrigeração_ideal == True and tipo_simulação == "Ano"):
        #     temp_maxima, mes_temp_max, dia_temp_max = self.historico.temperatura_maxima, self.historico.mes_temp_max, self.historico.dia_temp_max
        #     tipo_compressor_original = tipo_compressor_hvac
        #     tipo_compressor_hvac_2 = "inverter (controle ideal)"
        #     tipo_simulação = "Dia"
        #     somente_iterar2 = True
        #     refrigeração_ideal = False
        #     potencia_maxima = 1.0*self.Iniciar(tables_dicionario, pé_direito, potencia_maxima, tipo_simulação, dia_temp_max, mes_temp_max, adicionais, qualidade_simulacao_text, latitude_graus, unidade_potencia, COP_, paredes_default, temperatura_desejada, taxa_kwh_reais, ACH_troca_de_ar_h, horas_hvac, andar_terreo, angulo_N_geral, tipo_compressor_hvac_2, temperatura_limite_inferior, refrigeração_ideal, somente_iterar2, metodo_calculo_temp_solo, temp_solo_cte)
        #     self.somente_iterar = False
        #     compressão_convensional_ou_inverter = tipo_compressor_original
        #     tipo_simulação = "Ano"
        #     with open("temp/progresso.txt", "w") as arquivo:
        #         valor = "0"
        #         arquivo.write(valor)

        #         arquivo.close()
        #     self.ContinuarSimulação  =True

        segundo_inicial  = hora_inicial *3600 + minuto_inicial *60
        segundo_final = hora_final *3600 + minuto_final *60
        COP = COP_
        self.taxa_kwh_reais = taxa_kwh_reais


    
        self.ACH_troca_de_ar_h = ACH_troca_de_ar_h

        paredes_internas = paredes_default["paredes_internas"]
        paredes_externas = paredes_default["paredes_externas"]
        divisórias = paredes_default["divisorias"]
        interaces_horizontais = paredes_default["interfaces_horizontais"]
        
        k_parede_interna = float(paredes_internas["k"])
        k_parede_externa = float(paredes_externas["k"])
        k_parede_divisória = float(interaces_horizontais["k"])
        espessura_parede_interna = float(paredes_internas["espessura"])
        espessura_parede_externa = float(paredes_externas["espessura"])
        espessura_parede_divisória = float(divisórias["espessura"])
        espessura_horizontal = float(interaces_horizontais["espessura"])

        self.unidade_potencia = unidade_potencia
        #condições geograficas
        Latitude_g = float(latitude_graus) #graus
        Latitude_rad = Latitude_g/360*2*math.pi
        cos_latitude = math.cos(Latitude_rad)
        self.tabela_ambientes = eventosTabela.ConteudosTabela_ARR(Qtabela_ambientes)
        self.table_equipamentos = eventosTabela.ConteudosTabela_ARR(Qtable_equipamentos)
        self.ventilação_minima = self.VentilaçãoMinima(self.tabela_ambientes, self.table_equipamentos)
        self.ventilação_minima_m3_h = self.ventilação_minima *3.6
        dia = dia_
        mês = mes_
        self.It_registros = []
        self.adicionais = adicionais
        self.tipo_simulação = tipo_simulação
        self.potencia_maxima = (-1) * float(potencia_maxima) #refrigeração é negativa
        if(self.unidade_potencia == "W"):
            self.deltaQ_J_s = self.potencia_maxima
        if(self.unidade_potencia == "cal/h"):
            self.deltaQ_J_s = self.potencia_maxima*4.184/60/60
        if(self.unidade_potencia ==  "Btu/h"):
            self.deltaQ_J_s = self.potencia_maxima*0.2930710702 

        global delta_Tempo
        if(tipo_simulação != "Ano"):
            
            return self.main (Qtabela_paredes, Qtabela_ambientes,Qtable_horizontal, Qtable_equipamentos, self.pé_direito, self.ACH_troca_de_ar_h)
        else:

            delta_Tempo = int(qualidade_simulacao_text.split("=")[1].split("s")[0])
            return self.main (Qtabela_paredes, Qtabela_ambientes,Qtable_horizontal, Qtable_equipamentos, self.pé_direito, self.ACH_troca_de_ar_h)
                
    def RegistrarProgresso(self):
        self.i_barra_progresso=0
        # Abre o arquivo para leitura e escrita (modo "a+" cria o arquivo se não existir)
        while(True):
            with open("temp/progresso.txt", "a+") as arquivo:
                valor = ""
                if(self.ContinuarSimulação == True):
                    valor = ";;;" + str(self.i_barra_progresso)
                elif(self.ContinuarSimulação == True):
                    valor = "FimSimulação"
                arquivo.write(valor)
                time.sleep(3)  # Espera 10 segundos antes de ler o arquivo novamente
            arquivo.close()


    def VentilaçãoMinima(self, tabela_ambientes, table_equipamentos):
        #NBR16401-3 Tabela 1
        dicionario_parametros_ambientes =parametros.parametros_refrigeração_ambientes()
        vazão = 0
        for linha in tabela_ambientes:
            tipo = linha[12]
            area = float(linha[11])
            [Rp,Ra] = dicionario_parametros_ambientes[tipo]
            ambiente = linha[0]
            vazão += area*Ra 
            for cargas_line in table_equipamentos:
                if(cargas_line[0] == ambiente and cargas_line[2] == "Ocupantes"):
                    n_ocupantes = float(cargas_line[3])
                    vazão += n_ocupantes*Rp
        print("vazão " + str(vazão))
        return vazão
                    


    def simulação_ano_parte2(self,Qtabela_paredes, Qtabela_ambientes, Qtable_horizontal, Qtable_equipamentos, altura):
        inicio = time.time()
        #vai registrando o progresso
        thread_barraProgresso = threading.Thread(target=self.RegistrarProgresso)
        thread_barraProgresso.start()        
        self.Temp_interna_media_arr = []
        self.Temp_externa_media_arr = []
        self.Temp_solo_medio_arr = []
        self.Calor_inserido_medio_arr = []
        self.Refrigeração_media_arr = []
        self.dias = []
        if(self.tipo_simulação == "Ano"):
            pbar = tqdm(total=370) # cria a barra de progresso
            self.i_barra_progresso = 0
            #dados de cada dia encontrados
            for _mês in range (13):
                if(_mês!=0):
                    numero_de_dias_mes = self.historico.Dias_no_mes_Historico(_mês, self.ano)
                    for _dia in range (numero_de_dias_mes+1):
                        if(_dia!=0):
                            self.simualação_dia(self.table_equipamentos, altura, _dia, _mês, self.ano)
                            self.i_barra_progresso+=1
                            pbar.update(1)
                            
                            #self.bar['value'] = self.i_barra_progresso
                            #self.perncentagem_carregado = str(self.i_barra_progresso) + "/370"
                            #self.app.update_idletasks()
    
            fim = time.time()
            tempo_execucao = fim - inicio
            print("Tempo total de simulação: " + str(tempo_execucao) + "s")
            pbar.close()
            return self.Plot_ano()
        

#coeficiente de convecção
# J.A. Palyvos 
# A survey of wind convection coefficient correlations for building envelope energy systems’ modeling 
    def Hc_r (self, angulo_norte, ano, mes, dia, hora, minuto, interno_ou_externo): 
    
        hc_r = None
        hc = None
        hr = None
        
        [direção, velocidade] = self.historico.Vento(ano, mes, dia, hora, minuto)
        #h convecção
        if(modo_Hc_externo == "Emmel2007" and interno_ou_externo == "externo"):
            if(angulo_norte=="horizontal"):
                hc = 4.6 * math.pow(velocidade,0.79)
            else:
                angulo_tangencial = angulo_norte-90
                if(angulo_tangencial>180):
                    angulo_tangencial = angulo_tangencial-180
                deferença_angulos = direção-angulo_tangencial
                velocidade_tangencial = velocidade*abs(math.cos(deferença_angulos))
                if(angulo_tangencial <=22.5):
                    hc = 5.15 * math.pow(velocidade,0.81)
                if(22.5<angulo_tangencial <= 67.5):
                    hc = 3.34 * math.pow(velocidade,0.84)
                if(67.5<angulo_tangencial <= 112.5):
                    hc = 4.78 * math.pow(velocidade,0.71)
                if(112.5<angulo_tangencial <= 157.5):
                    hc = 4.05 * math.pow(velocidade,0.77)
                if(157.5<angulo_tangencial <= 180):
                    hc = 3.54 * math.pow(velocidade,0.76)
                    
        if(modo_Hc_externo == "J.A. Palyvos"  and interno_ou_externo == "externo"):
            if(angulo_norte=="horizontal"):
                hc = 5.8 + velocidade*3.95
            else:
                angulo_tangencial = angulo_norte-90
                if(angulo_tangencial>180):
                    angulo_tangencial = angulo_tangencial-180
                deferença_angulos = direção-angulo_tangencial
                velocidade_tangencial = velocidade * abs(math.cos(deferença_angulos))
                hc = 5.8 + velocidade_tangencial * 3.95

        if(modo_Hc_interno == "constante"  and interno_ou_externo == "interno"): #https://designbuilder.co.uk/helpv7.0/Content/Surface_Convection.htm item 2 "simple"
            if(angulo_norte=="horizontal"):
                hc = 2
            else:
                hc = 2.5

        if(modo_Hc_solo == "mil"  and interno_ou_externo == "solo"): #considerando q n ocorre convecção, somente condução para o solo logo convecção deve ser próxima de infinito, ou seja, resistência zero para parcela "h" no circuito térmico
            hc = 10000

        
        #h radiante
        hr=0
        #hr = e*ctrStefanBoltzmann*(2*T^2)*2*T
        
        hc_r = hc +hr
        return hc_r
    #Qtabela_paredes, Qtabela_ambientes,Qtable_horizontal, Qtable_equipamentos, self.pé_direito, self.ACH_troca_de_ar_h
    def main (self, Qtabela_paredes, Qtabela_ambientes, Qtable_horizontal, Qtable_equipamentos, altura, ACH_troca_de_ar_h):
        inicio = time.time()
        self.ano = self.historico.ano
        #tabelas
        self.tabela_ambientes = eventosTabela.ConteudosTabela_ARR(Qtabela_ambientes)
        self.tabela_janelas_portas = self.Configurar_Tabela_Janelas_Portas(self.Qtabela_janelas_portas)
        self.tabela_paredes = self.Configurar_Tabela_Paredes(Qtabela_paredes)
        self.table_horizontal = self.Configurar_Tabela_Interface_Horizontal(Qtable_horizontal)
        self.table_equipamentos = eventosTabela.ConteudosTabela_ARR(Qtable_equipamentos)
        self.calor_total_removido_por_dia_arr = []
        self.energia_gasta_por_dia_arr = []
        self.energia_gasta_mes_arr = [0,0,0,0,0,0,0,0,0,0,0,0]
        self.Temp_interna_media_arr = []
        self.Temp_externa_media_arr = []
        self.Temp_solo_medio_arr = []
        self.Calor_inserido_medio_arr = []
        self.Refrigeração_media_arr = []
        self.dias = []
        Relatorio = None

        self.ambientes = {}


        if(self.tipo_simulação == "Ano"):
            T_inicial_interno =self.historico.TempBulboSeco(self.ano, 1, 1, 0, 0)
            for ambiente in self.tabela_ambientes:
                nome_ambiente = ambiente[0]
                vertices = ambiente[7].replace(" ","")
                andar = ambiente[8]
                espaço = Espaço(T_inicial_interno, vertices, 0, altura)
                self.ambientes[nome_ambiente] = espaço
            self.zonaTermica = ZonaTermica(T_inicial_interno, 0, self.ambientes)
            #calcula a o ACH de acordo com a ashrae
            self.volume_total_m3 = self.zonaTermica.VolumeAr()
            self.ACH_min_ashrae = self.ventilação_minima_m3_h/self.volume_total_m3
            
            Relatorio = self.simulação_ano_parte2(Qtabela_paredes, Qtabela_ambientes, Qtable_horizontal, self.table_equipamentos, altura)

        if(self.tipo_simulação == "Dia"):
            T_inicial_interno =self.historico.TempBulboSeco(self.ano, mês, dia, 0, 0)
            for ambiente in self.tabela_ambientes:
                nome_ambiente = ambiente[0]
                vertices = ambiente[7].replace(" ","")
                andar = ambiente[8]
                espaço = Espaço(T_inicial_interno, vertices, 0, altura)
                self.ambientes[nome_ambiente] = espaço
            self.zonaTermica = ZonaTermica(T_inicial_interno, 0, self.ambientes)       
            #calcula a o ACH de acordo com a ashrae
            self.volume_total_m3 = self.zonaTermica.VolumeAr()
            self.ACH_min_ashrae = self.ventilação_minima_m3_h/self.volume_total_m3  
            Relatorio = self.simualação_dia(self.table_equipamentos, altura, dia, mês, self.ano)

        #calcula a o ACH de acordo com a ashrae
        self.volume_total_m3 = self.zonaTermica.VolumeAr()
        self.ACH_min_ashrae = self.ventilação_minima_m3_h/self.volume_total_m3


        if(self.adicionais == "potencia ideal"):


            self.CalcularPotenciaIdeal()

        self.ContinuarSimulação = False
        return Relatorio
    
    def simualação_dia(self, table_equipamentos, altura, _dia, _mês, _ano):
        global segundo_inicial, segundo_final, c, metodo_calculo_temp_solo, temp_solo_cte

        self.deltaQ_arr = []
        self.deltaQCondução_arr  = []
        self.deltaQConvecção_arr  = []
        self.deltaT_arr  = []
        self.calorInserido_arr = []
        self.calorJanela_arr = []
        self.calorUnicamenteParede_arr = []
        self.calorUnicamenteTeto_arr = []
        self.calorUnicamentePiso_arr = []
        self.deltaQrefrigeração_arr = []
        self.Temperatura_arr  = []
        self.Tempo_arr =[]
        self.CalorEquipamentos_arr = []
        self.Temp_externa_arr = []
        self.Temp_solo_arr = []
        
        T_inicial_interno =self.historico.TempBulboSeco(_ano, _mês, _dia, 0, 0)

        
        
        

        T_externa = self.zonaTermica.Temperatura()
        T1 = self.zonaTermica.Temperatura()

        self.Temperatura_arr = [T1]

        print("simulando data: " + str(_dia) + "/" + str(_mês) + "/" + str(_ano))

        inicio = time.time()

        D_ano = self.historico.DiaAno(_ano, _dia, _mês)
        E = None
        D = None
        F = None
        i = 0
        hora = 0
        self.Rb_count = 0
        self.Rb_arr = []
        self.Rb2_arr = []
        self.Hb_arr = []
        while (i<int(tempo_total_simulação/delta_Tempo)):

            
            estudo_apagar = []
            tempo = i*delta_Tempo/modificador_unidade_tempo
            hora = int(i*delta_Tempo/3600) % 24 #
            minuto = int(i*delta_Tempo/60) % 60
            hvac_ligado = None
            segundo_atual = i*delta_Tempo
            if(segundo_atual<=segundo_final and segundo_atual>=segundo_inicial):
                hvac_ligado = True
            else:
                hvac_ligado = False
            deltaQ = 0
            calorInserido = 0
            deltaQ_janela_porta = 0
            calor_unicamente_parede = 0
            calor_unicamente_solo = 0
            calor_unicamente_atmosfera = 0

            T_externa = self.historico.TempBulboSeco(_ano, _mês, _dia, hora, minuto)
            T2 = self.historico.TempBulboSeco(_ano, _mês, _dia, hora, minuto)
            #INFILTRAÇÃO
            fração_troca_ar_por_time_step = self.ACH_troca_de_ar_h /3600
            #print(str(zonaTermica.DeltaQ(T1, T_externa) * fração_troca_ar_por_time_step))
            if(self.zonaTermica.DeltaQ(T1, T_externa) * fração_troca_ar_por_time_step>10000):
                None
            calorInserido += self.zonaTermica.DeltaQ(T1, T_externa) * fração_troca_ar_por_time_step #calor que entra por infiltração


            GHW, DHR = self.historico.GHW_e_difusa(_ano, _mês, _dia, hora, minuto)

            #PAREDE
            calor_parede = 0
            for parede in self.tabela_paredes:

                deltaQ_parede = 0
                interfaces = parede[1].replace("[","").replace("]","").split(",")
                angulo = parede[10]
                cor = parede[8]
                area = float(parede[6])
                andar = int(parede[5])
                k_parede,espessura_parede = None, None
                if parede[2] == "externa":
                    k_parede = k_parede_externa
                    espessura_parede = espessura_parede_externa
                if parede[2] == "interna":
                    k_parede = k_parede_interna
                    espessura_parede = espessura_parede_interna
                if parede[2] == "contato c/solo":
                    k_parede = k_parede_externa
                    espessura_parede = espessura_parede_externa
                if parede[2] == "adiabatico":
                    k_parede = k_parede_interna
                    espessura_parede = espessura_parede_interna               
                h1_convec= self.Hc_r(angulo, _ano, _mês, _dia, hora, minuto, "externo")
                h2_convec = self.Hc_r(angulo, _ano, _mês, _dia, hora, minuto, "interno")
                U = self.CoeficienteGlobalTransferencia(h1_convec, h2_convec, k_parede, espessura_parede)

                
                vertical = True
                sol = True
                if(parede[2]== "interna" and False): #ignorar a interna
                    sol = False
                    mesma_zona_climatica = True

                    if(mesma_zona_climatica == True):
                        T2=T1
                    deltaQ_parede = self.Transferencia_calor_parede(T1, T2, altura, espessura_parede, area, U, angulo, cor, GHW, DHR, vertical, sol, hora, minuto, D_ano,h1_convec)

                if(parede[2]== "adiabatico" and False): #ignorar a interna
                    sol = False
                    mesma_zona_climatica = True

                    if(mesma_zona_climatica == True):
                        T2=T1
                    deltaQ_parede = self.Transferencia_calor_parede(T1, T2, altura, espessura_parede, area, U, angulo, cor, GHW, DHR, vertical, sol, hora, minuto, D_ano,h1_convec)
           

                elif(parede[2]=="externa"):
                    sol = True
                    deltaQ_parede = self.Transferencia_calor_parede(T1, T_externa, altura, espessura_parede, area, U, angulo, cor, GHW, DHR, vertical, sol, hora, minuto, D_ano,h1_convec)
                
                elif(parede[2] == "contato c/solo"):
                    sol = False
                    profundidade_meio_parede = None
                    if(self.andar_terreo>=andar):
                        profundidade_meio_parede = (self.andar_terreo - andar-0.5)*(self.pé_direito+self.espessura_entre_pisos) #0.5 indica o meio da parede como profundidade
                    else:
                        profundidade_meio_parede = 0
                    T_solo = self.historico.Temperatura_Solo_Ano(profundidade_meio_parede, _ano, _dia, _mês, hora, minuto, metodo_calculo_temp_solo, temp_solo_cte)

                    deltaQ_parede = self.Transferencia_calor_parede(T1, T_solo, altura, espessura_parede, area, U, 0, cor, GHW, DHR, vertical, sol, hora, minuto, D_ano, h1_convec)

                
                calorInserido += deltaQ_parede
                calor_unicamente_parede+= deltaQ_parede
                estudo_apagar.append(deltaQ_parede)
                
            #INTERFACE HORIZONTAL
            calor_horizontal = 0
            for interface in self.table_horizontal:
                cor = interface[9]
                deltaQ_parede = 0
                area = float(interface[6])
                
                if(interface[4] == "atmosfera" or interface[4] == "atmosfera s/sol"):
                    h1_convec= self.Hc_r("horizontal", _ano, _mês, _dia, hora, minuto, "externo")
                    h2_convec = self.Hc_r("horizontal", _ano, _mês, _dia, hora, minuto, "interno")
                else:
                    h1_convec= self.Hc_r("horizontal", _ano, _mês, _dia, hora, minuto, "interno")
                    h2_convec = self.Hc_r("horizontal", _ano, _mês, _dia, hora, minuto, "solo")


                U = self.CoeficienteGlobalTransferencia(h1_convec, h2_convec, k_parede, espessura_horizontal)
                GHW, DHR = self.historico.GHW_e_difusa(_ano, _mês, _dia, hora, minuto)
                vertical = False
                T_solo = None
                
                interfaces = interface[1].replace("[","").replace("]","").split("<->")
                if(interface[4] == "atmosfera"):
                    sol = True 
                    deltaQ_parede = self.Transferencia_calor_parede(T1, T_externa, altura, espessura_horizontal, area, U, 0, cor, GHW, DHR, vertical, sol, hora, minuto, D_ano, h1_convec)
                    calorInserido += deltaQ_parede  
                    calor_unicamente_atmosfera += deltaQ_parede
                if(interface[4] == "atmosfera s/sol"):
                    sol = False 
                    deltaQ_parede = self.Transferencia_calor_parede(T1, T_externa, altura, espessura_horizontal, area, U, 0, cor, GHW, DHR, vertical, sol, hora, minuto, D_ano, h1_convec)
                    calorInserido += deltaQ_parede 
                    calor_unicamente_atmosfera += deltaQ_parede 

                if(interface[4] == "contato c/solo"):
                    sol = False
                    profundidade = None
                    if(interface[2] == "teto"):
                        andar_teto = int(interface[5].split("<->")[0])
                        profundidade = (self.andar_terreo - andar_teto-1)*(self.pé_direito+self.espessura_entre_pisos) #-1 devido a ser o teto e não o piso
                        if(profundidade<0): #isso evita por exemplo que andares com o teto acima do chão tenham uma profundidade negativa
                            profundidade = 0
                    if(interface[2] == "piso"):
                        andar_piso = int(interface[5].split("<->")[1])
                        if(self.andar_terreo>=andar_piso):
                            profundidade = (self.andar_terreo - andar_piso)*(self.pé_direito+self.espessura_entre_pisos)
                        else:
                            profundidade = 0
                    T_solo = self.historico.Temperatura_Solo_Ano(profundidade, _ano, _dia, _mês, hora, minuto, metodo_calculo_temp_solo, temp_solo_cte)
                    deltaQ_parede = self.Transferencia_calor_parede(T1, T_solo, altura, espessura_horizontal, area, U, 0, cor, GHW, DHR, vertical, sol, hora, minuto, D_ano, h1_convec)
                    calor_unicamente_solo+= deltaQ_parede
                    
                    calorInserido += deltaQ_parede  
                estudo_apagar.append(deltaQ_parede)
            #JANELAS E PORTAS
#  ["andar", "x1","y1","x2","y2", 5 "SHGC", "largura", 7 "altura", 8 "tipo", 9 "angulo_rad", "interface", "material", 12 "area", 13 "angulo_Norte", 
# 14 "angulo_horizontal", 15 "interno/ext", 16 "U", 17 "espessura", 18 "k"]

            for elemento in self.tabela_janelas_portas:
                U = None
                k = None
                deltaQ_parede = 0
                A = float(elemento[6])/100 * float(elemento[7])/100
                angulo_norte = float(elemento[13])
                angulo_horizontal = float(elemento[14])
                espessura = float(elemento[17])/100
                UouSHGC = str(elemento[19])
                GHW, DHR = self.historico.GHW_e_difusa(_ano, _mês, _dia, hora, minuto)
                vertical = True
                It = self.RadiaçõesParede(GHW, DHR, hora, vertical, minuto, angulo_norte, D_ano)
                if(elemento[8] == "janela"): # atribui os valores de SHGC e cor
                    SHGC = float(elemento[5])
                    cor = SHGC      
                    k = 0 # k despresivel para janelas          
                if(elemento[8] == "janela" and elemento[15] == "externa"):
                    deltaQ_parede += A * It * SHGC
                    
                if(elemento[8] == "porta"):
                    #aqui não se deve usar o UouSHGC
                    SHGC = elemento[5]
                    cor = SHGC
                    k = float(elemento[18])
                
                if(elemento[8] == "porta"):
                    h1_convec= self.Hc_r(angulo_norte, _ano, _mês, _dia, hora, minuto, "externo")
                    h2_convec = self.Hc_r(angulo_norte, _ano, _mês, _dia, hora, minuto, "interno")
                    U = self.CoeficienteGlobalTransferencia(h1_convec, h2_convec, k, espessura)                   
                elif(elemento[8] == "janela"):
                    U = float(elemento[16])
                    # o false bloqueia esse bloco
                    if(U == float(0) and False):
                        h1_convec= self.Hc_r(angulo_norte, _ano, _mês, _dia, hora, minuto)
                        h2_convec = 5.7
                        U = self.CoeficienteGlobalTransferencia(h1_convec, h2_convec, k, espessura)
                
                sol = True
                if(elemento[15] == "interna"):
                    sol = False
                    mesma_zona_climatica = True
                    h1_convec= self.Hc_r(angulo_norte, _ano, _mês, _dia, hora, minuto, "interno")
                    h2_convec = self.Hc_r(angulo_norte, _ano, _mês, _dia, hora, minuto, "interno")
                    if(mesma_zona_climatica == True):
                        T2=T1
                    deltaQ_parede += self.Transferencia_calor_parede(T1, T2, altura, espessura, area, U, angulo, cor, GHW, DHR, vertical, sol, hora, minuto, D_ano, h1_convec)
 
                elif(elemento[15]=="externa"):
                    h1_convec= self.Hc_r(angulo_norte, _ano, _mês, _dia, hora, minuto, "externo")
                    h2_convec =self.Hc_r(angulo_norte, _ano, _mês, _dia, hora, minuto, "interno")
                    sol = True
                    
                    deltaQ_parede += self.Transferencia_calor_parede(T1, T_externa, altura, espessura, area, U, angulo, cor, GHW, DHR, vertical, sol, hora, minuto, D_ano, h1_convec)
                calorInserido += deltaQ_parede
                deltaQ_janela_porta += deltaQ_parede

            #print("Parede " + str(calor_parede) + " Horizontal " + str(calor_horizontal))

            calorEquipamentos = self.CargasTermicas_Aparelhos(table_equipamentos, hora, minuto)
            self.CalorEquipamentos_arr.append(calorEquipamentos)
            calorInserido += calorEquipamentos
            self.calorInserido_arr.append(calorInserido)
            self.calorJanela_arr.append(deltaQ_janela_porta)
            self.calorUnicamenteParede_arr.append(calor_unicamente_parede)
            self.calorUnicamenteTeto_arr.append(calor_unicamente_atmosfera)
            self.calorUnicamentePiso_arr.append(calor_unicamente_solo)
            deltaQrefrigeração = 0

            if (hvac_ligado ): #horario de funcionamento do HVAC
                try:
                    int(T1)
                    int(calorInserido)
                except:
                    None
                deltaQrefrigeração = self.Refrigeração(T1, calorInserido)
            #print("T1: " + str(T1))
            #print("T2: " + str(T2))
            #print("deltaQrefrigeração " + str(deltaQrefrigeração))
            #print("calorInserido " + str(calorInserido) +"\n")
            try:

                deltaQ =deltaQrefrigeração + calorInserido
            except:
                None
            self.deltaT_arr.append(self.zonaTermica.DeltaT(deltaQ*delta_Tempo))
            self.Temperatura_arr.append(self.Temperatura_arr[-1]+self.deltaT_arr[-1])




            #caso a temperatura fique abaixo da desejada mantemos igual a desejada em vez de ser menor e o calor removido é o mesmo que o inserido caso o compressor seja do tipo inverter 
            if(self.Temperatura_arr[-1] < T_desejada and compressão_convensional_ou_inverter=="inverter (controle ideal)" and hvac_ligado):

                deltaQrefrigeração = self.zonaTermica.DeltaQ(self.Temperatura_arr[-2], T_desejada)/delta_Tempo - calorInserido
                if(deltaQrefrigeração)>0:
                    deltaQrefrigeração = 0
                if(abs(self.deltaQ_J_s)<abs(deltaQrefrigeração)):
                    deltaQrefrigeração = self.deltaQ_J_s
                deltaQ =deltaQrefrigeração + calorInserido
                self.deltaT_arr[-1] = self.zonaTermica.DeltaT(deltaQ*delta_Tempo)
                self.Temperatura_arr[-1] = self.Temperatura_arr[-2]+self.deltaT_arr[-1]



            
            self.Temp_externa_arr.append(T_externa)
            try:
                self.Temp_solo_arr.append(T_solo)
            except:
                None
            self.Tempo_arr.append(tempo)
            self.deltaQ_arr.append(deltaQ)

            self.deltaQrefrigeração_arr.append(deltaQrefrigeração)
            T1 = self.Temperatura_arr[-1]



            i+=1
        fim = time.time()
        tempo_execucao = fim - inicio
        global potencia_max
        #registra a potência máxima atingida
        
        try:
            if min(self.deltaQrefrigeração_arr) > potencia_max:
                global dia_potencia_max, mes_potencia_max
                potencia_max = min(self.deltaQrefrigeração_arr)
                dia_potencia_max = _dia
                mes_potencia_max = _mês
        except:

            None
        calor_removido_por_dia = sum(self.deltaQrefrigeração_arr)/len(self.deltaQrefrigeração_arr) * 86400 *(-1) #J/d
        #print(mean(self.deltaQrefrigeração_arr))
        energia_gasta_por_dia = calor_removido_por_dia/COP
        self.calor_total_removido_por_dia_arr.append(calor_removido_por_dia)
        self.energia_gasta_por_dia_arr.append(energia_gasta_por_dia)
        self.energia_gasta_mes_arr[_mês-1] += energia_gasta_por_dia
        #print(f"Tempo de execução: {tempo_execucao} segundos")
        if(self.tipo_simulação == "Dia"):
            return self.Plot_dia()
             

        if(self.tipo_simulação == "Ano"):
            #tira as médias
            Temp_interna_media = mean(self.Temperatura_arr)
            self.Temp_interna_media_arr.append(Temp_interna_media)
            Temp_externa_media = mean(self.Temp_externa_arr)
            self.Temp_externa_media_arr.append(Temp_externa_media)
            if(self.Temp_solo_arr[1] != None): #as vezes não estamos usando as temperaturas do solo
                Temp_solo_medio = mean(self.Temp_solo_arr)
                self.Temp_solo_medio_arr.append(Temp_solo_medio)

            Calor_inserido_medio = mean(self.calorInserido_arr)
            self.Calor_inserido_medio_arr.append(Calor_inserido_medio)
            Refrigeração_media = mean(self.deltaQrefrigeração_arr)
            self.Refrigeração_media_arr.append(Refrigeração_media)

            if(len(self.dias)>0):
                self.dias.append(self.dias[-1]+1)
            else:
                self.dias = [1]

            

    def CalcularPotenciaIdeal(self):
        # faz uma lista sem o pico inicial
        lista_calor = self.calorInserido_arr[100:]
        calor_max = max(lista_calor)
        #print(str(calor_max) + "J/s")


    def CoeficienteGlobalTransferencia(self, h1,h2,k,L):
        U = 1/(1/h1+L/k+1/h2)

        return U
    
    #NBR 15220
    def CoeficienteGlobalTransferencia_15220(self, h1,h2,k,L):
        None


    def FatorTemperaturaSolAir(alfa, u, he, tau): #https://www.youtube.com/watch?v=Upx97dSOOWk tau = 0 para opacos (parede):
        None

    #NBR 15220-2 Anexo C
    def ResistenciaSuperficial(self, T_celcius, e, hc):
        #hc é de conveccção e hr de radiação

        T_kelvin = T_celcius + 273.15 #kelvin
        hr0 = 4*ctrStefanBoltzmann * pow(T_kelvin, 4)
        hr = e*hr0
        Rs = 1/(hc+hr)
        return Rs
    

    # sol 12h incidente no teto math.cos((12-12)/12 t* math.pi+0) = 1
    # sol 18h incidente no teto math.cos((18-12)/12 t* math.pi+0) = 1
    # sol 12h incidente na parede math.cos((12-12)/12 * math.pi+math.pi/2) = 0
    # sol 18h incidente na parede math.cos((18-12)/12 * math.pi+math.pi/2) = 1
    
    def RadiaçõesParede(self, GHW, DHR, hora, vertical, minuto, angulo_Norte, D_ano):
        global Latitude_g, Latitude_rad
        hora += minuto/60
        beta = None # ang vertical
        #beta_rad = None
        if(vertical == True):
            beta = 90
            #beta_rad = math.pi/2
        else:
            beta = 0
            #beta_rad = 0

        Incidente_normal_superficie=None
        #aaa = angulo_solar.Angulo_Solar()
        #Et,Rb_, HB_, Rb_2 = aaa.RadIncidente(hora, GHW, DHR, D_ano, angulo_Norte, beta_rad, Latitude_rad)
        Et, Et_b, Et_d, Et_r, azimute_superficie_sol, teta, azimute_solar, azimute_solar2, cosseno_azimute_solar, seno_azimute_solar = self.Angulo_Solar2.main(angulo_Norte, beta, Latitude_g, D_ano, hora, GHW, DHR)

        #horizontal em horas redondas (minuto = 0)
        #if(vertical==False and (minuto == 60 or minuto == 0)):
        #    print(str(hora) + "h - > delta:" + str(It))

        return Et

    #livro instalaoes-de-ar-condicionado-helio-crede tabela 3.6
    #vertical = True para paredes e False para cobertura
    def AcrescimoDiferencialDeTemperatura(self, angulo, cor, GHW, DHR, vertical, sol, hora, minuto, D_ano, hc_r):
        if(helio_crede == True):
            dicionario = {"Telhado":{"Escuro":25, "Medio":16.6, "Claro":8.3}, "L":{"Escuro":16.6, "Medio":11.1, "Claro":5.5},"O":{"Escuro":16.6, "Medio":11.1, "Claro":5.5}, "N":{"Escuro":8.3, "Medio":5.5, "Claro":2.7}, "S":{"Escuro":0, "Medio":0, "Claro":0}}
            if(angulo == 0):
                return dicionario["N"][cor]
            if(angulo == 90):
                return dicionario["L"][cor]
            if(angulo == 180):
                return dicionario["S"][cor]
            if(angulo == 270):
                return dicionario["O"][cor]
            
            if(0<angulo<90):
                delta = (dicionario["N"][cor] * (90-angulo) + dicionario["L"][cor] *(angulo - 0))/90
                return delta
            if(90<angulo<180):
                delta = (dicionario["L"][cor] *(180-angulo) + dicionario["S"][cor] *(angulo - 90))/90
                return delta
            if(180<angulo<270):
                delta = (dicionario["S"][cor] *(270-angulo) + dicionario["O"][cor] *(angulo - 180))/90
                return delta        
            if(270<angulo<360):
                delta = (dicionario["O"][cor] *(360-angulo) + dicionario["N"][cor] *(angulo - 270))/90
                return delta
        
        
        if(sol_air == True and sol == True):
            # ASHRAE pag 494 a 495

            It = self.RadiaçõesParede(GHW, DHR, hora, vertical, minuto, angulo, D_ano)
            self.It_registros.append(It)
  
            # 17/hc_r é um ajuste para o valor da ultima parcela da irradiação com a ashrae p494
            try:
                if(cor == "branco" or cor == "preto" or cor == "marmore"):
                  dicionario_cores = {"branco":0.8, "preto":0.91, "marmore":0.931}
                  e = dicionario_cores[cor]
                  if(vertical == True):
                    return e/hc_r  * It - 2*17/hc_r 
                  if(vertical == False):
                    return e/hc_r  * It - 4*17/hc_r        

                if(cor == "Claro"  and vertical == True):  
                    return 0.026*It      # parede Clara
                if(cor == "Medio"  and vertical == True):  
                    return 0.039*It     # parede Média
                if(cor == "Escuro" and vertical == True):  
                    return 0.052*It     # parede Escura
                if(cor == "Claro"  and vertical == False): 
                    return 0.026*It - 4 *17/hc_r # cobertura Clara
                if(cor == "Medio"  and vertical == False): 
                    return 0.039*It - 4 *17/hc_r # cobertura Média
                if(cor == "Escuro" and vertical == False): 
                    return 0.052*It - 4 *17/hc_r # cobertura Escura
            except:
                None
        
        return 0

    def ResistenciaInterna(k):
        return 1/k

    def Plot_ano(self):
        # Dados
        Tempo_arr = np.array(self.dias)
        Temperatura_arr = np.array(self.Temp_interna_media_arr)
        Temperatura_externa = np.array(self.Temp_externa_media_arr)
        Temperatura_solo = np.array(self.Temp_solo_medio_arr)
        calorInserido_arr = np.array(self.Calor_inserido_medio_arr)
        deltaQrefrigeracao_arr = np.array(self.Refrigeração_media_arr)
        calorEquipamentos_arr = np.array(self.CalorEquipamentos_arr)
        calor_total_removido_por_dia_arr = np.array(self.calor_total_removido_por_dia_arr)
        energia_gasta_por_dia_arr = np.array(self.energia_gasta_por_dia_arr)
        energia_gasta_mes_arr = np.array(self.energia_gasta_mes_arr)
        #print(str(len(Tempo_arr)) + " " + str(len(Temperatura_arr)) + " " + str(len(calorInserido_arr))+ " " + str(len(deltaQrefrigeracao_arr)))
        potencia_max = np.max(calorInserido_arr)
        if(self.somente_iterar == True):
            return potencia_max
        if(self.somente_iterar == False):
            Relatorio = relatorio.RelatorioAno_Iniciar(unidade_grafico_tempo, Tempo_arr, Temperatura_arr, Temperatura_externa, Temperatura_solo, calorInserido_arr, deltaQrefrigeracao_arr, calorEquipamentos_arr, calor_total_removido_por_dia_arr, energia_gasta_por_dia_arr, COP, potencia_max, dia_potencia_max, mes_potencia_max, self.ventilação_minima, self.taxa_kwh_reais, self.ACH_min_ashrae, self.volume_total_m3, self.ACH_troca_de_ar_h, energia_gasta_mes_arr)

        return Relatorio

    def Plot_dia(self):
        # Dados
        Tempo_arr = np.array(self.Tempo_arr)
        Temperatura_arr = np.array(self.Temperatura_arr[:-1])
        Temperatura_externa = np.array(self.Temp_externa_arr)
        Temperatura_solo = np.array(self.Temp_solo_arr)
        calorInserido_arr = np.array(self.calorInserido_arr)
        calorInserido_janela_porta_arr = np.array(self.calorJanela_arr)
        calorInseridoUnicamenteParede = np.array(self.calorUnicamenteParede_arr)
        calorInseridoUnicamenteAtmosfera = np.array(self.calorUnicamenteTeto_arr)
        calorInserido_solo = np.array(self.calorUnicamentePiso_arr)
        deltaQrefrigeracao_arr = np.array(self.deltaQrefrigeração_arr)
        calorEquipamentos_arr = np.array(self.CalorEquipamentos_arr)
        calor_total_removido_por_dia_arr = np.array(self.calor_total_removido_por_dia_arr)
        energia_gasta_por_dia_arr = np.array(self.energia_gasta_por_dia_arr)
        #print(str(len(Tempo_arr)) + " " + str(len(Temperatura_arr)) + " " + str(len(calorInserido_arr))+ " " + str(len(deltaQrefrigeracao_arr)))

        try:
            print("Registro IT:")
            print("It médio: " + str(mean(self.It_registros)))
            print("It máx: " + str(max (self.It_registros) )) 
            print("Fim Registro IT")
        except:
            None

        potencia_max = np.max(calorInserido_arr)
        if(self.somente_iterar == True):
            return potencia_max
        if(self.somente_iterar == False):
            print("potmax " + str(potencia_max))
            Relatorio = relatorio.RelatorioDia_Iniciar(unidade_grafico_tempo, Tempo_arr, Temperatura_arr, Temperatura_externa, Temperatura_solo, calorInserido_arr, deltaQrefrigeracao_arr, calorEquipamentos_arr, calor_total_removido_por_dia_arr, energia_gasta_por_dia_arr, COP, self.ventilação_minima, self.Rb_arr, self.Rb2_arr, self.Hb_arr, self.taxa_kwh_reais, self.ACH_min_ashrae, self.volume_total_m3, self.ACH_troca_de_ar_h, calorInserido_janela_porta_arr, calorInseridoUnicamenteParede, calorInseridoUnicamenteAtmosfera , calorInserido_solo)
        return Relatorio


    def Configurar_Tabela_Cargas(self, tabela_paredes):
        tabela = eventosTabela.ConteudosTabela_ARR(tabela_paredes)
        tabela_nova = []
        for _linha in tabela:
            linha = _linha.copy()
            vertices = linha[3].split("),(")
            
            _linha = linha
            _linha[3] = vertices

            
            # Obtendo o nome do item clicado
            angulo = _linha[10]
            _linha[10] = float(angulo)
            tabela_nova.append(_linha)

        return tabela_nova


    #indice, interface, tipo de parede, vertices, não sei, não sei, altura, U (coef global de transf)
    def Configurar_Tabela_Paredes(self, tabela_paredes):
        tabela = eventosTabela.ConteudosTabela_ARR(tabela_paredes)
        tabela_nova = []
        for _linha in tabela:
            linha = _linha.copy()
            vertices = linha[3].split("),(")
            
            _linha = linha
            _linha[3] = vertices

            
            # Obtendo o nome do item clicado
            angulo = _linha[10]
            _linha[10] = float(angulo)
            tabela_nova.append(_linha)

        return tabela_nova


    #indice, interface, tipo de parede, vertices, não sei, não sei, altura, U (coef global de transf)
    def Configurar_Tabela_Janelas_Portas(self, tabela_paredes_janelas):
        tabela = eventosTabela.ConteudosTabela_ARR(tabela_paredes_janelas)
        tabela_nova = []
        for _linha in tabela:
##["0andar", "x1","y1","x2",4 "y2", "SHGC", "largura", "altura",8 "tipo", "angulo_rad", 10 "interface", "material", 12 "area", 13 "angulo_Norte"
# , "angulo_horizontal", "interno/ext", 16 "U", "espessura", "k"]
            linha = _linha.copy()
            espessura_elemento = float(_linha[17])/100
            
            _linha = linha

            # U = None
            # if (linha[8] == "janela"):
            #     k_janela = float(_linha[18])
            #     h1_convec_janela = 10
            #     h2_convec_janela = 10
            #     U = self.CoeficienteGlobalTransferencia(h1_convec_janela, h2_convec_janela, k_janela, espessura_elemento)
            # if (linha[8] == "porta"):
            #     k_porta = float(_linha[18])
            #     h1_convec_porta = 10
            #     h2_convec_porta = 10
            #     U = self.CoeficienteGlobalTransferencia(h1_convec_porta, h2_convec_porta, k_porta, espessura_elemento)            
            # _linha[16] = U            

            tabela_nova.append(_linha)

        return tabela_nova

    def Configurar_Tabela_Interface_Horizontal(self, tabela_interfaces):
        tabela = eventosTabela.ConteudosTabela_ARR(tabela_interfaces)
        tabela_nova = []
        for _linha in tabela:
            linha = _linha.copy()
            vertices = linha[3].split("),(")

            _linha = linha
            _linha[3] = vertices
  
            
            _linha.append(0)
            tabela_nova.append(_linha)

        return tabela_nova



    def Comprimento(self, tupla):
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
    


    
    #apenas convecção e condução, falta irradiação
    def Transferencia_calor_parede(self,  T1, T2, altura, espessura_parede, area, U, angulo_parede, cor, GHW, DHR, vertical, sol, hora, minuto, D_ano, hcr):
        delta = 0
        angulo_parede = angulo_parede + self.angulo_N_geral
        delta = self.AcrescimoDiferencialDeTemperatura(angulo_parede, cor, GHW, DHR, vertical, sol, hora, minuto, D_ano, hcr )

        deltaQ = U*area*(T2-T1+delta)
        if(hora == 12):
            None
        return deltaQ

    def Condução_interface_horizontal(self, area, T1, T2, espessura, k ):
        deltaQ = k* (T2-T1) * area/espessura
        return deltaQ
        
    def Convecção_interface_horizontal(self, area, T1, T2, h_convec):
        deltaQ = h_convec * (T2-T1) * area
        return deltaQ
    

    def Refrigeração(self, T1, Q_inserido):
        # ar condicionado 12000 BTU -> -3500 J/s
        global T_min_Inverter, T_desejada, amplitude_temperatura_Inverter
    
        # compressor com inverter
        if(compressão_convensional_ou_inverter == "inverter (controle proporcional)"):
            #temperatura muito abaixo, inverter desligado
            if(T1<T_min_Inverter):
                return 0
            if(T1<T_desejada):
                
                if((-Q_inserido)>self.deltaQ_J_s):
                    Q_removido = (T1-T_min_Inverter)/amplitude_temperatura_Inverter * self.deltaQ_J_s
                    if(Q_removido<0):
                        None
                else:
                    Q_removido = (T1-T_min_Inverter)/amplitude_temperatura_Inverter * self.deltaQ_J_s 


                return min([Q_removido,0])
            #inverter e temperatura alta
            if(T1>=T_desejada):
                return self.deltaQ_J_s 
            #inverter e temperatura baixa
            if(T1 ==T_desejada):
                None
                return self.deltaQ_J_s
            else:
                None

        # compressor com inverter
        if(compressão_convensional_ou_inverter == "inverter (controle ideal)"):
            #temperatura muito abaixo, inverter desligado
            if(T1<T_min_Inverter):
                return 0
            if(T1<T_desejada):
                
                if((-Q_inserido)>self.deltaQ_J_s):
                    Q_removido = (T1-T_min_Inverter)/amplitude_temperatura_Inverter * Q_inserido *(-1)
                    if(Q_removido<0):
                        None
                else:
                    Q_removido = (T1-T_min_Inverter)/amplitude_temperatura_Inverter * self.deltaQ_J_s 

                return min([Q_removido,0])
            #inverter e temperatura alta
            if(T1>T_desejada):
                return self.deltaQ_J_s 
            #inverter e temperatura baixa
            if(T1 ==T_desejada):
                None
                return - min([abs(Q_inserido), abs(self.deltaQ_J_s)])
            else:
                None


        # compressor convencional
        elif(compressão_convensional_ou_inverter == "normal split (on-off)"):

            deltaT = self.zonaTermica.DeltaT(Q_inserido*delta_Tempo)
            T_novo = T1+deltaT
            if(T_novo>=T_desejada or self.on_off_ligado == True):
                self.on_off_ligado = True
                deltaT = self.zonaTermica.DeltaT(self.deltaQ_J_s*delta_Tempo)
                T_novo2 = T_novo+deltaT
                if(T_novo2 >= T_min_Inverter):
                    return - abs(self.deltaQ_J_s)
                else:
                    self.on_off_ligado = False
                    calor_necessario = self.zonaTermica.DeltaQ(T_novo,T_min_Inverter)/delta_Tempo
                    return - abs(calor_necessario)
            if(T_novo<=T_min_Inverter):
                self.on_off_ligado = False   
                return 0
            else:
                self.on_off_ligado = False  
                return 0

            
        #print("OI")
    def CargasTermicas_Aparelhos(self, tabela_equipamentos, hora, minuto):
        
        calor = 0
        
        for linha_arr in tabela_equipamentos:
            inicio = int(linha_arr[6])
            fim = int(linha_arr[7])
            if(inicio<= hora and hora<=fim):
                calor += float(linha_arr[3]) * float(linha_arr[5])
        return calor

    # calor por PESSOA
    def CargasOcupação(self, tabela_schedule_pessoas):
        None
        