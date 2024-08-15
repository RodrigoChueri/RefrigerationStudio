from elementos_e_materiais import ElementoEstrutural, elementos_predefinidos


class Ponto:
    #tipo = [parede, ambiente, etc]
    def __init__(self, x, y, ambiente, tipo):
        self.x = x
        self.y = y
        self.ambiente = ambiente
        self.tipo = tipo
        self.ambientesVizinhos =[]
        self.ambienteSuperior = []
        self.ambienteInferior = []
    def Ambiente(self):
        return self.ambiente
    
    def Tipo(self):
        return self.tipo
    
    def AmbientesVizinhos(self):
        return self.ambientesVizinhos

    def AmbienteSuperior(self):
        return self.ambienteSuperior

    def AmbienteInferior(self):
        return self.ambienteInferior

if __name__ == '__main__':
    # Criar pontos e armazená-los em um dicionário
    pontos = {}

    # Exemplo de como adicionar um ponto
    ponto1 = Ponto(553, 123, 25.5, 100, {'propriedade1': 10, 'propriedade2': 20})
    pontos[(ponto1.x, ponto1.y)] = ponto1

    # Exemplo de como acessar a temperatura de um ponto específico
    coordenadas = (553, 123)
    if coordenadas in pontos:
        temperatura_do_ponto = pontos[coordenadas].temperatura
        print("Temperatura do ponto {}: {}".format(coordenadas, temperatura_do_ponto))
    else:
        print("Coordenadas não encontradas")

    # Iterar sobre todos os pontos
    for coordenadas, ponto in pontos.items():
        print("Coordenadas: {}, Temperatura: {}".format(coordenadas, ponto.temperatura))