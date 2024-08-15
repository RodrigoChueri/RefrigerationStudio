from PyQt5 import QtGui, QtCore
import math



class Espaço:
    def __init__(self, temperatura_inicial, poligono_str, calor_inicial, altura):
        self.temperatura = temperatura_inicial
        self.poligono_str = poligono_str
        self.calor = calor_inicial
        self.altura = altura
        self.espessura = 0.24

        self.poligono = self.QPoligono()
        self.area = self.Area()

    def QPoligono(self):
        pontos_poligono_str = self.poligono_str.split("),(")
        pontos_poligono = []
        poligono = QtGui.QPolygon()
        for ponto_str in pontos_poligono_str:
            ponto_str_divido = ponto_str.replace("(", "").replace(")", "").split(",")
            x = float(ponto_str_divido[0])
            y = float(ponto_str_divido[1])


            ponto_poligono = (x, y)

            pontos_poligono.append(ponto_poligono)
        

        poligono = pontos_poligono
        return poligono
        


    def Area(self):
        area = 0
        for i in range(len(self.poligono)):
            p1 = self.poligono[i]
            p2 = self.poligono[(i + 1) % len(self.poligono)]
            d = p1[0] * p2[1] - p2[0] * p1[1]
            area += d

        area = abs(area) /2.0
        
        return area


    def AreaParede(self):
        perimetro_parede = 0
        for i in range(len(self.poligono)):
            p1 = self.poligono[i]
            p2 = p1
            try:
                p2 = self.poligono[(i + 1)]
            except:
                p2 = self.poligono[-1]
            x = abs(p1[0]-p2[0])
            y = abs(p1[1]-p2[1])
            comprimento = math.sqrt(math.pow(x,2)+math.pow(y,2))
            perimetro_parede+=comprimento
        area = perimetro_parede*self.espessura
        return area

    #preciso das espessuras das paredes para subtrair
    def AreaAr(self):
        area = self.Area()-self.AreaParede()/2
        return area
    
    # area total - perimetro * t_parede/2
        None

    def DeltaT(self, Car, Cp, deltaQ):
        deltaT = deltaQ / (Car*self.VolumeAr() + Cp*self.VolumeParede())
        return deltaT
    def Calor(self, volume):
        None

    def VolumeParede(self):
        vol = self.AreaParede() * self.altura

        return vol

    def VolumeAr(self):
        vol = self.AreaAr() * self.altura

        return vol
    

