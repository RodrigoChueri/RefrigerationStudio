class Material:
    def __init__(self, nome, k):
        self.nome = nome
        self.k = k

    def __str__(self):
        return f'Material: {self.nome} k={self.k}'

class ElementoEstrutural:
    def __init__(self, espessura, material):
        self.espessura = espessura
        self.material = material
        self.k = self.material.k

    def __str__(self):
        return f'{type(self).__name__}: Espessura={self.espessura} Material={self.material.nome} k={self.k}'

class Parede(ElementoEstrutural):
    def __init__(self, espessura, material, descricao):
        super().__init__(espessura, material)
        self.descricao = descricao

class Porta(ElementoEstrutural):
    def __init__(self, espessura, material, altura, largura):
        super().__init__(espessura, material)
        self.altura = altura
        self.largura = largura

# Materiais pré-definidos
materiais_predefinidos = {
    'madeira': Material('madeira', 0.1),
    'concreto': Material('concreto', 1.5),
    'vidro': Material('vidro', 0.8),
    'divisoria_material': Material('divisoria_material', 1.0),
    'automatico_material': Material('automatico_material', 1.0)
}

# Elementos estruturais pré-definidos
elementos_predefinidos = {
    'parede_interna_laboratorio': Parede(4, materiais_predefinidos['divisoria_material'], 'Parede interna do laboratório'),
    'parede_externa_laboratorio': Parede(24, materiais_predefinidos['concreto'], 'Parede externa do laboratório'),
    'porta_laboratorio': Porta(5, materiais_predefinidos['madeira'], 200, 80),
    'automatico_parede' : Parede(24 , materiais_predefinidos['automatico_material'], 'método automatico de parede')
}

# Exemplo de uso
if __name__ == "__main__":
    print("Materiais pré-definidos:")
    for nome, material in materiais_predefinidos.items():
        print(nome, ":", material)

    print("\nElementos estruturais pré-definidos:")
    for nome, elemento in elementos_predefinidos.items():
        print(nome, ":", elemento)
