from Espaço import Espaço
class ZonaTermica:
    def __init__(self, temperatura_inicial,  calor_inicial, ambientes):
        self.temperatura = temperatura_inicial
        self.calor = calor_inicial
        self.ambientes = ambientes
        self.volumeAr = self.VolumeAr()
        self.volumeParede = self.VolumeParede()

    def Temperatura(self):
        return self.temperatura
    
    def VolumeAr(self): #m^3
        vol = 0
        for nome_ambiente, ambiente_valor in self.ambientes.items():
            vol+=ambiente_valor.VolumeAr()
        return vol
    
    def VolumeParede(self): #m^3
        vol = 0
        for nome_ambiente, ambiente_valor in self.ambientes.items():
            vol+=ambiente_valor.VolumeParede()
        return vol
        
    def DeltaT(self,  deltaQ):
        Car = 1000 #J/kgK
        Car = Car * 1.27 #J/kgK * kg/m^3 = J/m^3 . K
        Cparede = 1000 #J/m³·K
        deltaT = deltaQ / (Car*self.volumeAr + Cparede*self.volumeParede)
        return deltaT
    

    def DeltaQ(self, T1, T2):
        deltaT = T2-T1
        Car = 1000 #J/kgK
        Car = Car * 1.27 #J/kgK * kg/m^3 = J/m^3 . K
        Cparede = 1000 #J/m³·K

        deltaQ = deltaT * (Car*self.volumeAr + Cparede*self.volumeParede)
        return deltaQ   