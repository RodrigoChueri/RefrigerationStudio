import math
from datetime import datetime
#import numpy, scipy.optimize
#from scipy.optimize import leastsq
from pyestimate import sin_param_estimate
import numpy as np
#ano,mes,dia,hora,min

#explicação
#[ano,mes,dia,hora,minuto, data source, temperatura de bulbo seco,
#temperatura de bubo úmido, umidade relativa, pressão atmosférica da estação meteorológica, ...]
metod_calculo_temp_solo_simplificado = False
w_ano = 2*math.pi/365
Dh_ano = 5 * math.pow(10,-7) * 86400 #4.17·10-7 m²/s segundo o Cableizer, passando para dia  4.17·10-7 * 86400
z0_ano = math.sqrt(2*Dh_ano/w_ano)
w_dia = 2*math.pi/86400
Dh_dia = 6.82 * math.pow(10,-7) # 5 10^-7 segundo o IEC 60853-2 #4.17·10-7 m²/s segundo o Cableizer
z0_dia = math.sqrt(2*Dh_dia/w_dia)


class Historico():
    def __init__(self):
        super().__init__()

        #criação de histórico
        self.ano = None
        self.historico = {}
        self.historico_temp_max_media = {}
        self.leitura_arquivo_climatico()

        #dados usados ao longo do ano
        self.temperatura_maxima, self.mes_temp_max, self.dia_temp_max = self.Temperatura_maxima(self.ano)
        self.temperatura_media = self.Temperatura_media(self.ano)
        self.Historico_TemperaturaMax_Media(self.ano) #historico diario de média e max
        self.T_amplitude_ano = None
        self.F_Ano = None
        self.fase_ano  = None
        self.Curvas_ano()

        #dados usados ao longo do dia
        self.dia_analisado, self.mes_analisado = None, None # anota o ultimo dia a ser analisado na simulação evitando ter de recalcular muitos dados
        self.segundo_media_dia_analisado = None
        self.temperatura_media_dia_analisado = None
        self.amplitude_dia_analisado = None

        #dados usados em determinado minuto e hora
        self.minuto_agora = None
        self.hora_agora = None 
        self.direção_vento_agora = None
        self.velocidade_vento_agora = None

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
            with open(caminho, 'r') as arquivo:
                None
                        
        except FileNotFoundError:
            print(f'O arquivo "{nome_arquivo}" não foi encontrado.')
            return None



        with open(caminho, 'r') as arquivo:
                # Itera sobre cada linha do arquivo
            for linha in arquivo:
                # Imprime cada linha
                _linha = linha.strip()  # strip() remove espaços em branco extras, como quebras de linha
                arr = _linha.split(",")

                #verifica se o primeiro elemento da linha é um número para analisar
                try: 
                    int(arr[0])
                    ano = int(arr[0])
                    self.ano = ano
                    mes = int(arr[1])
                    dia = int(arr[2])
                    hora = int(arr[3])
                    minuto  = int(arr[4])
                    temp_bulbo_seco = float(arr[6])
                    temp_bulbo_umido = float(arr[7])
                    umid_rel = float(arr[8])
                    Patm = int(arr[9])
                    GHW = int(arr[14]) #Direct normal irradiance (DNI) Não tem inclusa a radiação difusa #https://en.wikipedia.org/wiki/Solar_irradiance#:~:text=Direct%20normal%20irradiance%20(DNI)%2C,or%20reflected%20by%20atmospheric%20components).
                    Diffuse_Horizontal_Radiation = int(arr[15])
                    DireçãoVento = int(arr[20]) #graus
                    VelocidadeVento = float(arr[21])
                    if(ano not in self.historico):
                        matriz_data = [[[[0 for minutos in range(1)] for horas in range(25)] for dias in range(33)]  for meses in range(13)]
                        self.historico[ano] = matriz_data
                        self.historico[ano][mes][dia][hora][minuto] = [temp_bulbo_seco, temp_bulbo_umido, umid_rel, Patm, GHW, Diffuse_Horizontal_Radiation, DireçãoVento, VelocidadeVento]
                    else:
                        self.historico[ano][mes][dia][hora][minuto] = [temp_bulbo_seco, temp_bulbo_umido, umid_rel, Patm, GHW, Diffuse_Horizontal_Radiation, DireçãoVento, VelocidadeVento]

                except:
                    None


    #vento
    def Vento(self, ano, mes, dia, hora, minuto):
        if(hora!= self.hora_agora or minuto != self.minuto_agora):
            if(hora == 0):
                hora = 24

            direção_0_min  = self.historico[ano][mes][dia][hora][0][6] 
            velocidade_0_min  = self.historico[ano][mes][dia][hora][0][7]
            direção_60_min= 1999999999
            velocidade_60_min= 1999999999
            if(hora!=24):#caso menor que 24h
                direção_60_min = self.historico[ano][mes][dia][hora+1][0][6]
                velocidade_60_min = self.historico[ano][mes][dia][hora+1][0][7]
            else:#caso seja 24h
                try:
                    direção_60_min = self.historico[ano][mes][dia+1][1][0][6] # se não for o ultimo dia do mês
                    velocidade_60_min = self.historico[ano][mes][dia+1][1][0][7] # se não for o ultimo dia do mês
                except:
                    if(mes!=12):
                        direção_60_min = self.historico[ano][mes+1][1][1][0][6] #caso seja o ultimo vamos para o dia 1 do mês seguinte
                        velocidade_60_min = self.historico[ano][mes+1][1][1][0][7] #caso seja o ultimo vamos para o dia 1 do mês seguinte
                    else:
                        direção_60_min = direção_0_min #caso seja o ultimo dia do ano
                        velocidade_60_min = velocidade_0_min
            self.direção_vento_agora = direção_0_min + (direção_60_min-direção_0_min)/60*minuto
            self.velocidade_vento_agora = velocidade_0_min + (velocidade_60_min-velocidade_0_min)/60*minuto


        self.minuto_agora = minuto
        self.hora_agora = hora 
        return [self.direção_vento_agora, self.velocidade_vento_agora]


    #GHW e DHR
    def GHW_e_difusa(self, ano, mes, dia, hora, minuto):
        if(hora == 0):
            hora = 24

        GHW_0_min  = self.historico[ano][mes][dia][hora][0][4] 
        Diffuse_Horizontal_Radiation_0_min  = self.historico[ano][mes][dia][hora][0][5]
        GHW_60_min= 1999999999
        Diffuse_Horizontal_Radiation_60_min= 1999999999
        if(hora!=24):#caso menor que 24h
            GHW_60_min = self.historico[ano][mes][dia][hora+1][0][4]
            Diffuse_Horizontal_Radiation_60_min = self.historico[ano][mes][dia][hora+1][0][5]
        else:#caso seja 24h
            try:
                GHW_60_min = self.historico[ano][mes][dia+1][1][0][4] # se não for o ultimo dia do mês
                Diffuse_Horizontal_Radiation_60_min = self.historico[ano][mes][dia+1][1][0][5] # se não for o ultimo dia do mês
            except:
                if(mes!=12):
                    GHW_60_min = self.historico[ano][mes+1][1][1][0][4] #caso seja o ultimo vamos para o dia 1 do mês seguinte
                    Diffuse_Horizontal_Radiation_60_min = self.historico[ano][mes+1][1][1][0][5] #caso seja o ultimo vamos para o dia 1 do mês seguinte
                else:
                    GHW_60_min = GHW_0_min #caso seja o ultimo dia do ano
                    Diffuse_Horizontal_Radiation_60_min = Diffuse_Horizontal_Radiation_0_min
        GHW_agora = GHW_0_min + (GHW_60_min-GHW_0_min)/60*minuto
        Diffuse_Horizontal_Radiation_agora = Diffuse_Horizontal_Radiation_0_min + (Diffuse_Horizontal_Radiation_60_min-Diffuse_Horizontal_Radiation_0_min)/60*minuto
        return [GHW_agora, Diffuse_Horizontal_Radiation_agora]


    def TempBulboSeco(self, ano, mes, dia, hora, minuto):
        if(hora == 0):
            hora = 24
        temperatura_0_min = self.historico[ano][mes][dia][hora][0][0] #ultimo zero é do bulbo seco

        temperatura_60_min= 1999999999
        if(hora!=24):#caso menor que 24h
            temperatura_60_min = self.historico[ano][mes][dia][hora+1][0][0]
        else:#caso seja 24h
            try:
                temperatura_60_min = self.historico[ano][mes][dia+1][1][0][0] # se não for o ultimo dia do mês
            except:
                if(mes!=12):
                    temperatura_60_min = self.historico[ano][mes+1][1][1][0][0] #caso seja o ultimo vamos para o dia 1 do mês seguinte
                else:
                    temperatura_60_min = temperatura_0_min #caso seja o ultimo dia do ano
        temperatura_agora = temperatura_0_min + (temperatura_60_min-temperatura_0_min)/60*minuto
        return temperatura_agora
        #return self.historico[ano][mes][dia][hora][0][0]

    def Temperatura_media(self,ano):
        temperatura_total = 0
        vezes_somadas = 0
        for mes in range(12):
            if(mes>0):
                for dia in range(len(self.historico[ano][mes])-1):
                    if(dia>0):
                        for hora in range(24):
                            if(hora>0):
                                try:
                                    temperatura_total+=self.historico[ano][mes][dia][hora][0][0]
                                    vezes_somadas+=1
                                except:
                                    None
        
        temp_media = temperatura_total/vezes_somadas
        return temp_media

    #PEGA A TEMP DO DIA MAIS QUENTE
    def Temperatura_maxima(self,ano):
        temp_maxima = -9999
        mes_temp_max = -9999
        dia_temp_max = -9999
        for mes in range(13):
            if(mes>0):
                
                for dia in range(len(self.historico[ano][mes])-1):

                    if(dia>0):
                        temperatura_dia_soma = 0
                        soma_horas = 0
                        for hora in range(25):
                            if(hora>0):
                                try:
                                    temperatura_dia_soma+=self.historico[ano][mes][dia][hora][0][0]
                                    soma_horas+=1
                                except:
                                    None
                        if(soma_horas>1):
                            temperatura_media_dia = temperatura_dia_soma/soma_horas
                            if(temperatura_media_dia>temp_maxima):
                                temp_maxima = temperatura_media_dia
                                mes_temp_max = mes
                                dia_temp_max = dia

        
        return temp_maxima, mes_temp_max, dia_temp_max
    
    def Dias_no_mes_Historico(self,mes,ano):
        contagem = 1
        try:
            while(True):

                if(type(self.historico[ano][mes][contagem][1][0][0]) == float):
                    contagem+=1
                else:
                    break
        except: None

        return contagem-1
        
    #temperatura média ao longo do dia
    def Temperatura_media_dia(self,ano, mes, dia):
        temperatura_total = 0
        vezes_somadas = 0
        for hora in range(24):
            if(hora>0):
                try:
                    temperatura_total+=self.historico[ano][mes][dia][hora][0][0]
                    vezes_somadas+=1
                except:
                    None
        
        temp_media = temperatura_total/vezes_somadas
        return temp_media

    def Temperatura_maxima_dia(self,ano, mes, dia):
        temp_maxima = -9999
        mes_temp_max = -9999
        dia_temp_max = -9999
        temperatura_dia_soma = 0
        soma_horas = 0
        for hora in range(25):
            if(hora>0):
                try:
                    temperatura_dia_soma+=self.historico[ano][mes][dia][hora][0][0]
                    soma_horas+=1
                except:
                    None
        if(soma_horas>1):
            temperatura_media_dia = temperatura_dia_soma/soma_horas
            if(temperatura_media_dia>temp_maxima):
                temp_maxima = temperatura_media_dia


                    
        return temp_maxima


        


    def Curvas_ano(self):
        temperatura_dias = []
        i_mes = 0
        for mes in self.historico_temp_max_media[self.ano]:
            if(i_mes>0):
                for dia in mes:
                    if(dia !={}):
                        media_do_dia = dia["temperatura_media_dia"]
                        temperatura_dias.append(media_do_dia)

            i_mes +=1
        x = np.array(temperatura_dias)
        A,f,phi = sin_param_estimate(x)
        self.T_amplitude_ano = A
        self.F_Ano = f
        self.fase_ano  = phi

    #ao longo do ano variando senoidalmente
    def Temperatura_Solo_Ano(self, profundidade, ano, dia, mes, hora, minuto, metodo_calculo_temp_solo, temp_solo_cte):
        global  z0_ano
        if(metodo_calculo_temp_solo == "Constante"):
            return temp_solo_cte
        if(metodo_calculo_temp_solo == "senoidal (comb.lin. solução dia + ano)"):

            delta_t = self.Diferença_dias(1, 1, self.ano, dia, mes, self.ano)
            z=profundidade
            lambda_ = -z/z0_ano

            segunda_parecela = self.T_amplitude_ano * math.pow(math.e, lambda_) * math.cos(w_ano*delta_t-z/z0_ano + self.fase_ano)
            terceira_parcela = self.Temperatura_Solo_Dia(profundidade, ano, dia, mes, hora, minuto, metodo_calculo_temp_solo, temp_solo_cte)[1]
            T = self.temperatura_media + segunda_parecela + terceira_parcela
            
            return T
        
        if(metodo_calculo_temp_solo == "senoidal simples (solução somente ao longo do ano)"):
            delta_t = self.Diferença_dias(self.dia_temp_max, self.mes_temp_max, self.ano, dia, mes, self.ano)
            z=profundidade
            lambda_ = -z/z0_ano

            segunda_parecela = self.T_amplitude_ano * math.pow(math.e, lambda_) * math.cos(w_ano*delta_t-z/z0_ano + self.fase_ano)
            terceira_parcela = 0
            T = self.temperatura_media + segunda_parecela + terceira_parcela

            return T            
        

    def Temperatura_Solo_Dia(self, profundidade, ano, dia, mes, hora, minuto, metodo_calculo_temp_solo, temp_solo_cte):
        global z0_dia
        if(metodo_calculo_temp_solo == "Constante"):
            return temp_solo_cte
        if(metodo_calculo_temp_solo == "senoidal (comb.lin. solução dia + ano)"):
            #self.historico_temp_max_media[ano][mes][dia] = {"temperatura_media_dia" "hora_media" "temp_max" "hora_t_max" "temp_min" "hora_t_min"}
            if(dia!= self.dia_analisado or mes!=self.mes_analisado):
                try:
                    temperatura_max = self.historico_temp_max_media[ano][mes][dia]["temp_max"]
                except:
                    None
                temperatura_min = self.historico_temp_max_media[ano][mes][dia]["temp_min"]
                self.amplitude_dia_analisado = (temperatura_max-temperatura_min)/2
                self.temperatura_media_dia_analisado = self.historico_temp_max_media[ano][mes][dia]["temperatura_media_dia"]
                hora_media = self.historico_temp_max_media[ano][mes][dia]["hora_media"]
                self.segundo_media_dia_analisado = 3600*hora_media
            delta_t = (hora*3600+minuto*60) - self.segundo_media_dia_analisado #medido em segundos
            z=profundidade


            lambda_ = -z/z0_dia
            segunda_parte = self.amplitude_dia_analisado * math.pow(math.e, lambda_) * math.sin(w_dia*delta_t + lambda_)
            T = self.temperatura_media_dia_analisado + segunda_parte
            
            self.dia_analisado = dia
            self.mes_analisado = mes

            return [T, segunda_parte]


    def Historico_TemperaturaMax_Media(self, ano):
        if(ano not in self.historico_temp_max_media):
            matriz_data = [[{} for dias in range(32)]  for meses in range(13)]
            self.historico_temp_max_media[ano] = matriz_data
        

        for mes in range(13):
            if(mes>0):
                for dia in range(len(self.historico[ano][mes])-1):

                    if(dia>0):
                        temperatura_dia_soma = 0
                        soma_horas = 0
                        temp_max = -9999
                        hora_t_max = 0
                        temp_min = 9999
                        hora_t_min = 0 
                        for hora in range(25):
                            if(hora>0):
                                try:
                                    temperatura_dia_soma+=self.historico[ano][mes][dia][hora][0][0]
                                    soma_horas+=1
                                    if(temp_max<self.historico[ano][mes][dia][hora][0][0]):
                                        temp_max = self.historico[ano][mes][dia][hora][0][0]
                                        hora_t_max = hora
                                    if(temp_min>self.historico[ano][mes][dia][hora][0][0]):
                                        temp_min = self.historico[ano][mes][dia][hora][0][0]
                                        hora_t_min = hora
                                except:
                                    None
                        if(soma_horas>1):
                            temperatura_media_dia = temperatura_dia_soma/soma_horas
                            hora_media = (hora_t_max+hora_t_min)/2
                            self.historico_temp_max_media[ano][mes][dia] = {"temperatura_media_dia": temperatura_media_dia, "hora_media": hora_media, "temp_max": temp_max, "hora_t_max": hora_t_max, "temp_min": temp_min, "hora_t_min": hora_t_min}
        None

    def Diferença_dias(self, dia1,mes1,ano1, dia2,mes2,ano2):
        data_inicial = datetime(ano1, mes1, dia1)
        data_final = datetime(ano2, mes2, dia2)
        diferenca = data_final - data_inicial
        numero_dias = diferenca.days
        return numero_dias
    
    def DiaAno(self, ano, dia, mes):
        dias = self.Diferença_dias(1,1,ano, dia, mes, ano) + 1
        return dias
    



if __name__ == '__main__':
    historico = Historico()
    print("ar: " + str(historico.TempBulboSeco(2008, 7, 23, 12,0)))
    print("solo: " + str(historico.Temperatura_Solo_Dia(0, 23, 7)))


    print("ar: " + str(historico.TempBulboSeco(2008, 2, 23, 12,0)))
    print("solo: " + str(historico.Temperatura_Solo_Dia(0, 23, 2)))