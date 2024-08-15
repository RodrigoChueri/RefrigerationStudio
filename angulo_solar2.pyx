from math import *
import matplotlib.pyplot as plt
import numpy as np
import time
#CAP 14 da ASHRAE
#E_b é o raio que sai perpendicular a coroa solar, é o indice 14 de um arquivo epw
#E_d é a radiação difusa medida em uma surperficie horizontal, é o indice 15 de um arquivo epw
#Et_b é o raio direto que incide em uma superficie
#Et_d é a difusa que incide em uma superficie
#Et_r é a que reflete no chão e incide em uma superficie

class AnguloSolar():
    def __init__(self):
        None

    def EstimarRadiação(self, n, altitude_solar):
        Esc = 1367 #ASHRAE, Iqbal 1983 e World Meteorological Organization 1981
        E0 = Esc*(1+0.033*cos(2*pi*(n-3)/365))
        m = 1/ (sin(altitude_solar) +0.50572 * pow(6.07995+altitude_solar,-1.6364)   )

        Eb = E0*exp(-tau_b*pow(m,a*b))

    def TempoSolar(self,Long, h, n):
        x = 2*pi*(n-1)/365
        ET = 2.2918*(0.0075+0.1868*cos(x)-3.2077*sin(x)-1.4615*cos(2*x)-4.089*sin(2*x))
        AST = h + ET/60 +(Long-h)/15



    def Declinação(self, D):
        declinação = 23.45 * sin( (284+D)/ 365 * 2 *  pi)
        return declinação

    def main(self, azimute_superficie_graus, angulo_vertical_graus, LAT_graus, D, h, E_b, E_d):
        declinação_graus = self.Declinação(D)
        #print("declinação_graus " + str(declinação_graus))
        #beta_sol = 90 - abs(LAT_graus-declinação_graus)
        LAT = LAT_graus * 2 * pi/360
        declinação = declinação_graus * 2 * pi/360
        #print("beta_sol " + str(beta_sol))
        H_angulo_graus = 15 * (h-12)
        H_angulo = H_angulo_graus * 2*pi/360
        beta_ang_solar_altitude = asin (cos(LAT)*cos(declinação)*cos(H_angulo)+sin(LAT)*sin(declinação))
        beta_ang_solar_altitude_graus = beta_ang_solar_altitude * 360/2/pi
        #print("beta_ang_solar_graus " + str(beta_ang_solar_altitude_graus))
        cosseno_azimute_solar=  (cos(H_angulo)*cos(declinação)*sin(LAT) - sin(declinação)*cos(LAT))/cos(beta_ang_solar_altitude) 
        seno_azimute_solar = sin(H_angulo)*cos(declinação)/cos(beta_ang_solar_altitude)
        if(cosseno_azimute_solar-1 < 0.001 and cosseno_azimute_solar>1):
            cosseno_azimute_solar=1
        if(cosseno_azimute_solar+1 > -0.001 and cosseno_azimute_solar<-1):
            cosseno_azimute_solar=-1
        azimute_solar = None
        try:

            azimute_solar = acos( cosseno_azimute_solar     )
        except:
            None
        if(seno_azimute_solar>=0):
            azimute_solar = - azimute_solar
        azimute_solar2 = asin( seno_azimute_solar     )
        azimute_solar_graus = azimute_solar * 360/2/pi
        #print("azimute_solar_graus"  + str(azimute_solar_graus))
        azimute_superficie = azimute_superficie_graus/360*2*pi
        azimute_superficie_sol = azimute_solar - azimute_superficie
        azimute_superficie_sol_graus = azimute_superficie_sol * 360 / 2 / pi
        #print("azimute_superficie_sol_graus " + str(azimute_superficie_sol_graus))
        angulo_vertical = angulo_vertical_graus * 2 * pi /360
        teta = acos(cos(beta_ang_solar_altitude)*cos(azimute_superficie_sol)*sin(angulo_vertical)+sin(beta_ang_solar_altitude)*cos(angulo_vertical))
        teta_graus = teta * 360/2/pi
        #print("teta_graus " + str(teta_graus))
        
        Et_b = E_b * cos(teta)
        if(Et_b<0 or teta < 0):
            Et_b = 0
 

        Y = max([0.45, 0.55 + 0.437*cos(teta) + 0.313*pow(cos(teta),2) ])
        Et_d = E_d * Y
        if(Et_d<0):
            Et_d = 0
            
        refletividade_solo = 0.2
        Et_r = (E_b*sin(beta_ang_solar_altitude) + E_d) *refletividade_solo* (1+cos(beta_ang_solar_altitude))/2
        if(Et_r<0):
            Et_r = 0
        # print("Et_b " + str(Et_b))
        # print("Et_d " + str(Et_d))
        # print("Et_r " + str(Et_r))



            
        Et = Et_b+Et_d+Et_r
        return Et, Et_b, Et_d, Et_r, azimute_superficie_sol_graus, teta_graus, azimute_solar_graus,azimute_solar2*360/2/pi, cosseno_azimute_solar, seno_azimute_solar




import arquivo_climatico
if __name__ == '__main__':
    L = -22.83
    D = 203
    azimute_superficie = 90
    angulo_vertical = 90

    anguloSolar = AnguloSolar()
    historico = arquivo_climatico.Historico()
    #main(azimute_superficie, angulo_vertical, L, D, h, E_b, E_d)
    ano = 2005
    mes = 9
    dia = 8
    radiação_normal_superficie_list = []
    Et_b_list = []
    Et_d_list =[]
    Et_r_list = []
    hora_list = []
    azimute_superficie_sol_list = []
    teta_list = []
    azimute_solar_list = []
    azimute_solar_list2 = []
    cosseno_azimute_solar_list = []
    seno_azimute_solar_list = []
    for hora in range(24):
        for min in range(60):
            h = hora + min/60
            GHW, DHR = historico.GHW_e_difusa(ano, mes, dia, hora, min)
            Et, Et_b, Et_d, Et_r, azimute_superficie_sol, teta, azimute_solar, azimute_solar2, cosseno_azimute_solar, seno_azimute_solar = anguloSolar.main(azimute_superficie, angulo_vertical, L, D, h, GHW, DHR)
            radiação_normal_superficie_list.append(Et)
            Et_b_list.append(Et_b)
            Et_d_list.append(Et_d)
            Et_r_list.append(Et_r)
            azimute_superficie_sol_list.append(azimute_superficie_sol)
            teta_list.append(teta)
            hora_list.append(h)
            azimute_solar_list.append(azimute_solar)
            azimute_solar_list2.append(azimute_solar2)
            cosseno_azimute_solar_list.append(cosseno_azimute_solar)
            seno_azimute_solar_list.append(seno_azimute_solar)


    fig, axs = plt.subplots(3, 1, figsize=(10, 6))
    xpoints = np.array(hora_list)
    ypoints = np.array(radiação_normal_superficie_list)
    y2points = np.array(Et_b_list)
    y3points = np.array(Et_d_list)
    y4points = np.array(Et_r_list)
    y5points = np.array(azimute_superficie_sol_list)
    y6points = np.array(teta_list)
    y7points = np.array(azimute_solar_list)
    y8points = np.array(azimute_solar_list2)
    y9points = np.array(cosseno_azimute_solar_list)
    y10points = np.array(seno_azimute_solar_list)

    axs[0].plot(xpoints, ypoints, label = "Total")
    axs[0].plot(xpoints, y2points, label="normal")
    axs[0].plot(xpoints, y3points, label = "difusa")
    axs[0].plot(xpoints, y4points, label = "refletida")
    axs[1].plot(xpoints, y5points, label = "azimute_sol_superficie")
    axs[1].plot(xpoints, y6points, label = "teta")
    axs[1].plot(xpoints, y7points, label = "azimute solar (seno)")
    axs[1].plot(xpoints, y8points, label = "azimute solar (cos)")
    axs[2].plot(xpoints, y9points, label = "cos(azimute solar) ")
    axs[2].plot(xpoints, y10points, label = "sin(azimute solar)")

    axs[0].set_xticks(np.arange(0, 24, 1))
    axs[2].set_xticks(np.arange(0, 24, 1))
    axs[0].grid(True)
    axs[2].grid(True)
    axs[0].legend()
    axs[1].legend()
    axs[2].legend()
    fig.show()

    time.sleep(100000)