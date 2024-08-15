import sys
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtGui import QTransform

import random
import arredondamentos

# Inicializa os valores de x, y e zoom
x_value = 0
y_value = 0
zoom = 1
scroll_zoom = 0
escala_original = 100  # px/metro
escala = int(escala_original)  # px/metro
resolução_arredondamento_ = 0.05
resolução_arredondamento = escala_original * zoom * resolução_arredondamento_
modo_escolhido = "retângulo"  # Modo inicial


class MyWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        # Configurando o layout de grade
        layout = QtWidgets.QGridLayout()
        self.setLayout(layout)

        # Parte esquerda: texto "botões" e tabela para coordenadas
        left_panel = QtWidgets.QVBoxLayout()
        layout.addLayout(left_panel, 0, 0)

        label = QtWidgets.QLabel("Botões")
        label.setAlignment(QtCore.Qt.AlignCenter)
        left_panel.addWidget(label)

        # constroi a tabela
        self.ConstruirTabela()

        left_panel.addWidget(self.table)

        # Botão "Atualizar"
        atualizar_button = QtWidgets.QPushButton("Atualizar")
        atualizar_button.clicked.connect(self.atualizar)
        left_panel.addWidget(atualizar_button)

        # Botão "Limpar"
        limpar_button = QtWidgets.QPushButton("Limpar")
        limpar_button.clicked.connect(self.limpar)
        left_panel.addWidget(limpar_button)

        # Botão "Rastrear Cliques"
        rastrear_button = QtWidgets.QPushButton("Rastrear Cliques")
        rastrear_button.clicked.connect(self.rastrear_cliques)
        left_panel.addWidget(rastrear_button)

        # Botão "Criar Linhas"
        criar_linhas_button = QtWidgets.QPushButton("Criar Linhas (teste)")
        criar_linhas_button.clicked.connect(self.criar_linhas)
        left_panel.addWidget(criar_linhas_button)

        # Botão "Criar Linhas de 90°"
        criar_linhas_90_button = QtWidgets.QPushButton("Criar Linhas (90°)")
        criar_linhas_90_button.clicked.connect(self.criar_linhas_90graus)
        left_panel.addWidget(criar_linhas_90_button)

        # Botão "Modo Retângulo"
        retangulo_button = QtWidgets.QPushButton("Modo Retângulo")
        retangulo_button.clicked.connect(self.modo_retangulo)
        left_panel.addWidget(retangulo_button)

        # Parte direita: área de desenho de retângulos
        self.drawing_area = DrawingArea(self)
        layout.addWidget(self.drawing_area, 0, 1)
        layout.setColumnMinimumWidth(1, 1000)  # Define a largura mínima da segunda coluna como 1000 pixels

        # Adicionando uma região de 30 pixels abaixo da área de desenho
        text_area = QtWidgets.QWidget()
        text_layout = QtWidgets.QHBoxLayout()
        text_area.setLayout(text_layout)
        layout.addWidget(text_area, 1, 1)

        # Adicionando o texto "x:y:"
        self.x_label = QtWidgets.QLabel("x:")
        text_layout.addWidget(self.x_label)

        self.y_label = QtWidgets.QLabel("y:")
        text_layout.addWidget(self.y_label)

        self.zoom_label = QtWidgets.QLabel("zoom:")
        text_layout.addWidget(self.zoom_label)

        self.escala_label = QtWidgets.QLabel("escala:")
        text_layout.addWidget(self.escala_label)

        self.update_labels()  # Atualiza os valores iniciais de x, y e zoom nos rótulos

        self.setGeometry(30, 30, 1200, 430)  # Ajusta a largura total para acomodar a tabela e a área de desenho
        self.show()

    def ConstruirTabela(self):
        # Cria e configura a tabela para mostrar as coordenadas dos retângulos
        self.table = QtWidgets.QTableWidget()
        self.table.setColumnCount(7)  # Adiciona uma coluna extra para os vértices
        self.table.setHorizontalHeaderLabels(
            ["Ambiente", "X1", "Y1", "X2", "Y2", "Cor", "Vértices"])  # Cabeçalhos da tabela
        self.table.setMaximumWidth(200)  # Limita a largura da tabela a 200 pixels

        # Definindo a largura das colunas da tabela
        for i in range(self.table.columnCount()):
            self.table.setColumnWidth(i, 30)

        # Conectar evento keyPressEvent da tabela
        self.table.keyPressEvent = self.keyPressEventTable

    def RetornarTabelaEmPixels(self):
        # Função não implementada, deve retornar a tabela em pixels
        None

    def update_labels(self):
        # Atualiza os rótulos com os valores atuais de x, y e zoom
        global x_value, y_value, zoom, escala
        self.x_label.setText(f"x: {x_value}")
        self.y_label.setText(f"y: {y_value}")
        self.zoom_label.setText(f"zoom: {zoom * 100}%")
        self.escala_label.setText(f"escala: {escala}")

    def atualizar_tabela(self, retangulo, cor, tipo):
        # Atualiza a tabela com as coordenadas e cores do retângulo desenhado
        global escala
        rowPosition = self.table.rowCount()
        self.table.insertRow(rowPosition)

        nome_ambiente = self.gerar_nome_ambiente()
        item = QtWidgets.QTableWidgetItem(nome_ambiente)
        self.table.setItem(rowPosition, 0, item)
        topLeftX =  0
        topLeftY=0
        bottomRightX=0
        bottomRightY=0
        if tipo == "retângulo":
            topLeftX = retangulo.topLeft().x() / escala
            topLeftY = retangulo.topLeft().y() / escala
            bottomRightX = retangulo.bottomRight().x() / escala
            bottomRightY = retangulo.bottomRight().y() / escala
        
        if tipo == "linha":
            topLeftX = retangulo.x1() / escala
            topLeftY = retangulo.y1() / escala
            bottomRightX = retangulo.x2() / escala
            bottomRightY = retangulo.y2() / escala  
        


        vertices = f"({topLeftX}, {topLeftY}), ({bottomRightX}, {topLeftY}), ({bottomRightX}, {bottomRightY}), ({topLeftX}, {bottomRightY})"
        self.table.setItem(rowPosition, 1, QtWidgets.QTableWidgetItem(str(topLeftX)))
        self.table.setItem(rowPosition, 2, QtWidgets.QTableWidgetItem(str(topLeftY)))
        self.table.setItem(rowPosition, 3, QtWidgets.QTableWidgetItem(str(bottomRightX)))
        self.table.setItem(rowPosition, 4, QtWidgets.QTableWidgetItem(str(bottomRightY)))
        self.table.setItem(rowPosition, 5,
                           QtWidgets.QTableWidgetItem(str(cor.red()) + ', ' + str(cor.green()) + ', ' + str(cor.blue())))
        self.table.setItem(rowPosition, 6, QtWidgets.QTableWidgetItem(vertices))
        self.table.setItem(rowPosition, 6, QtWidgets.QTableWidgetItem(tipo))




    def redesenhar_quadro(self):
        # Função para redesenhar o quadro, não implementada
        QtWidgets.QMessageBox.information(self, 'Redesenhado', 'O quadro foi redesenhado')

    def gerar_nome_ambiente(self):
        # Gera um nome de ambiente único para cada retângulo
        nome_base = "Ambiente"
        numero_ambiente = 1
        while True:
            novo_nome = f"{nome_base} {numero_ambiente}"
            if not self.nome_ambiente_existe(novo_nome):
                return novo_nome
            numero_ambiente += 1

    def nome_ambiente_existe(self, nome):
        # Verifica se o nome do ambiente já existe na tabela
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)
            if item and item.text() == nome:
                return True
        return False

    def atualizar(self):
        # Atualiza os retângulos na tela com base nos valores da tabela
        global escala
        print("atualizar")
        tabela_str = "Valores da Tabela:\n"
        tabela_arr = []
        for row in range(self.table.rowCount()):
            linha = ""
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                if item:
                    tabela_str += f"{item.text()} "
                    linha += item.text() + ";"
                else:
                    tabela_str += "None "
            tabela_str += "\n"
            tabela_arr.append(linha)

        self.limpar()

        for item in tabela_arr:
            coordenadas = item.split(";")
            tipo = coordenadas[6]
            x1 = int(zoom * (int(float(coordenadas[1]) * escala) - x_value))
            y1 = int(zoom * (int(float(coordenadas[2]) * escala) - y_value))
            x2 = int(zoom * (int(float(coordenadas[3]) * escala) - x_value))
            y2 = int(zoom * (int(float(coordenadas[4]) * escala) - y_value))

            w = int(x2-x1)
            h = int(y2-y1)
            cor_str = coordenadas[5].split(',')
            cor = QtGui.QColor(int(cor_str[0]), int(cor_str[1]), int(cor_str[2]))
            #renderiza como retangulo
            if(tipo == "retângulo"):
                retangulo = QtCore.QRect(x1, y1, w, h)
                self.drawing_area.rectangles.append((retangulo, cor))
            #renderiza como linha
            if(tipo == "linha"):
                #
                linha = [(x1,y1), (x2,y2)]
                self.drawing_area.linhas.append((linha, cor))

            self.update()

    def limpar(self):
        # Limpa todos os retângulos da tela e a tabela
        self.drawing_area.rectangles = []
        self.drawing_area.linhas = []
        self.drawing_area.update()

    def gerar_cor(self):
        # Gera uma cor aleatória
        return QtGui.QColor(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

    def keyPressEvent(self, event):
        # Manipula os eventos de teclado para mover a visualização
        global x_value, y_value
        if event.key() == QtCore.Qt.Key_Right:
            x_value += 1
            self.atualizar()
        elif event.key() == QtCore.Qt.Key_Left:
            x_value -= 1
            self.atualizar()
        elif event.key() == QtCore.Qt.Key_Up:
            y_value -= 1
            self.atualizar()
        elif event.key() == QtCore.Qt.Key_Down:
            y_value += 1
            self.atualizar()

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
            scroll_zoom = 0
            escala = escala / 2
        print(scroll_zoom)
        zoom = pow(2, scroll_zoom)
        print(zoom)
        self.update_labels()
        event.accept()
        self.atualizar()

    def keyPressEventTable(self, event):
        # Verificar se a tecla pressionada é a tecla "Delete"
        if event.key() == QtCore.Qt.Key_Delete:
            # Obter a linha selecionada
            selected_row = self.table.currentRow()
            # Verificar se uma linha está selecionada
            if selected_row >= 0:
                # Remover a linha selecionada
                self.table.removeRow(selected_row)
                # Atualizar o desenho na área de desenho
                self.atualizar()
        else:
            # Se a tecla pressionada não for "Delete", chamar o keyPressEvent original da tabela
            super().keyPressEvent(event)

    def rastrear_cliques(self):
        global modo_escolhido
        modo_escolhido = "rastrear"

    def criar_linhas(self):
        global modo_escolhido
        modo_escolhido = "linha"

    def criar_linhas_90graus(self):
        global modo_escolhido
        modo_escolhido = "linha90g"

    def modo_retangulo(self):
        global modo_escolhido
        modo_escolhido = "retângulo"



class DrawingArea(QtWidgets.QWidget):
    def __init__(self, parent):
        # Inicializa a área de desenho
        super().__init__(parent)
        self.begin = QtCore.QPoint()
        self.begin_sem_zoom = QtCore.QPoint()
        self.end = QtCore.QPoint()
        self.rectangles = []
        self.linhas = []
        self.selected_rectangle_index = -1
        self.offset = QtCore.QPoint()
        self.resizing = False

    def paintEvent(self, event):
        # Desenha os retângulos na área de desenho
        global zoom, x_value, y_value
        qp = QtGui.QPainter(self)

        qp.setBrush(QtCore.Qt.white)  # Define a cor de fundo branca
        qp.drawRect(self.rect())

        offsetLinhaVertical = x_value * zoom
        offsetLinhaHorizontal = y_value * zoom

        pen = QtGui.QPen()
        pen.setWidth(3)
        qp.setPen(pen)

        pen.setWidth(1)
        qp.setPen(pen)

        
        for y in range(0, self.height(), 50):
            qp.drawLine(0, y - offsetLinhaHorizontal, self.width(), y - offsetLinhaHorizontal)
            qp.drawText(5, y + 15 - offsetLinhaHorizontal, str(y / zoom / escala))

        for x in range(0, self.width(), 50):
            qp.drawLine(x - offsetLinhaVertical, 0, x - offsetLinhaVertical, self.height())
            qp.drawText(x + 5 - offsetLinhaVertical, 15, str(x / zoom / escala))

        for i, (retangulo, cor) in enumerate(self.rectangles):
            brush = QtGui.QBrush(cor)
            qp.setBrush(brush)
            qp.drawRect(retangulo)

            if i == self.selected_rectangle_index:
                qp.setPen(QtGui.QPen(QtCore.Qt.red, 2, QtCore.Qt.DashLine))
                qp.drawRect(retangulo.adjusted(0, 0, -1, -1))
            
            # anotações que aparecem nas figuras geometricas
            # cuida do texto das retas90g (tipo retangulo)
            if(retangulo.width() == 0 or retangulo.height()==0):
                print("é uma reta (feita de retangulo)")

                qp.drawText(retangulo.topLeft() + QtCore.QPoint(30, 30),
                            "Parede")
                            
                
            # cuida do texto dos retangulos
            else:
                print("é um retangulo")
                qp.drawText(retangulo.topLeft() + QtCore.QPoint(5, -5),
                            f"W: {retangulo.width() / zoom}" + f" H: {retangulo.height() / zoom}")
                nome_ambiente = "ambiente"
                qp.drawText(retangulo.center() + QtCore.QPoint(-len(nome_ambiente) * 2 - 3, 5), nome_ambiente)

        # Desenha as linhas
        pen = QtGui.QPen(QtCore.Qt.black)
        pen.setWidth(2)
        qp.setPen(pen)
        for linha in self.linhas:
            ponto1, ponto2 = linha
            print("pontos")
            print(ponto1)
            print(ponto2)
            if(type(ponto2) == tuple):
                qp.drawLine(QtCore.QPoint(*ponto1), QtCore.QPoint(*ponto2))
            else:
                ponto1_ = ponto1[0]
                ponto2_ = ponto1[1]
                qp.drawLine(QtCore.QPoint(*ponto1_), QtCore.QPoint(*ponto2_))


    def mousePressEvent(self, event):
        global x_value, y_value, zoom, resolução_arredondamento, modo_escolhido

        if modo_escolhido == "linha":
            print("Modo de criação de linhas ativado")
            if event.button() == QtCore.Qt.LeftButton:
                x = int((event.pos().x() + x_value * zoom) / zoom)
                x = arredondamentos.arredondar_int(x, resolução_arredondamento)
                y = int((event.pos().y() + y_value * zoom) / zoom)
                y = arredondamentos.arredondar_int(y, resolução_arredondamento)
                if not self.begin.isNull():
                    print(f"Ponto de início: {self.begin.x()}, {self.begin.y()}")
                    self.linhas.append([(self.begin.x(), self.begin.y()), (x, y)])
                    print(f"Adicionada linha: {(self.begin.x(), self.begin.y())} -> {(x, y)}")
                    self.update()
                    coordenadas_finais = QtCore.QPoint(x, y)
                    linha = QtCore.QLine(self.begin, coordenadas_finais)
                    cor = self.parent().gerar_cor()
                    self.parent().atualizar_tabela(linha, cor, "linha")
                self.begin = event.pos()

            


        elif modo_escolhido == "rastrear":
            if event.button() == QtCore.Qt.LeftButton:
                x = int((event.pos().x() + x_value * zoom) / zoom)
                x = arredondamentos.arredondar_int(x, resolução_arredondamento)
                y = int((event.pos().y() + y_value * zoom) / zoom)
                y = arredondamentos.arredondar_int(y, resolução_arredondamento)
                print(f"Coordenadas do clique: ({x}, {y})")



        elif modo_escolhido == "retângulo" or modo_escolhido == "linha90g":  # linha90g é uma falsa linha, na real é um retangulo de espessura 0
            if event.button() == QtCore.Qt.LeftButton:
                x = int((event.pos().x() + x_value * zoom) / zoom)
                x = arredondamentos.arredondar_int(x, resolução_arredondamento)
                y = int((event.pos().y() + y_value * zoom) / zoom)
                y = arredondamentos.arredondar_int(y, resolução_arredondamento)
                self.begin_sem_zoom = event.pos() + QtCore.QPoint(x, y)
                self.begin = QtCore.QPoint(x, y)
                print(self.begin)
                self.end = event.pos()

                for i, (retangulo, _) in enumerate(self.rectangles):
                    if retangulo.contains(self.begin):
                        self.selected_rectangle_index = i
                        self.offset = event.pos() - retangulo.topLeft()
                        self.resizing = True
                        break
                self.update()




    def mouseMoveEvent(self, event):
        global x_value, y_value
        print("Mouse movido")
        if event.buttons() & QtCore.Qt.LeftButton:
            if self.selected_rectangle_index != -1 and self.resizing:
                print("Arrastando retângulo")
                rect = self.rectangles[self.selected_rectangle_index][0]
                delta = event.pos() - self.offset - rect.topLeft()
                rect.translate(delta)

                self.rectangles[self.selected_rectangle_index] = (
                    rect, self.rectangles[self.selected_rectangle_index][1])
                self.begin = event.pos()
                self.update()
                print("arrastando")
            else:
                print("Atualizando posição final")
                self.end = event.pos()
                self.update()


    def mouseReleaseEvent(self, event):
        global x_value, y_value, zoom, resolução_arredondamento, modo_escolhido

        if modo_escolhido == "retângulo":
            print("Modo padrão de criação de retângulos ativado")
            if event.button() == QtCore.Qt.LeftButton:
                if self.selected_rectangle_index != -1:
                    self.selected_rectangle_index = -1
                    self.resizing = False
                else:
                    x2 = int((event.pos().x() + x_value * zoom) / zoom)
                    x2 = arredondamentos.arredondar_int(x2, resolução_arredondamento)
                    y2 = int((event.pos().y() + y_value * zoom) / zoom)
                    y2 = arredondamentos.arredondar_int(y2, resolução_arredondamento)
                    coordenadas_finais = QtCore.QPoint(x2, y2)
                    retangulo = QtCore.QRect(self.begin, coordenadas_finais)
                    cor = self.parent().gerar_cor()
                    self.rectangles.append((retangulo, cor))
                    self.parent().atualizar_tabela(retangulo, cor, "retângulo")
                self.update()


        elif modo_escolhido == "linha90g":
            if event.button() == QtCore.Qt.LeftButton:
                if self.selected_rectangle_index != -1:
                    self.selected_rectangle_index = -1
                    self.resizing = False
                else:
                    x2 = int((event.pos().x() + x_value * zoom) / zoom)
                    x2 = arredondamentos.arredondar_int(x2, resolução_arredondamento)
                    y2 = int((event.pos().y() + y_value * zoom) / zoom)
                    y2 = arredondamentos.arredondar_int(y2, resolução_arredondamento)

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
                    self.rectangles.append((retangulo, cor))
                    self.parent().atualizar_tabela(retangulo, cor, "retângulo")
                self.update()


        # atualiza a tela com base na tabela
        self.parent().atualizar()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MyWidget()
    window.show()
    app.aboutToQuit.connect(app.deleteLater)
    sys.exit(app.exec_())
