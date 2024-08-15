import tkinter as tk
from tkinter import ttk
from PyQt5.QtWidgets import QMenuBar, QDialog
from PyQt5 import QtWidgets
import ast
import eventosTabela
import customtkinter
import parametros
debug = False


print("Carregando módulo de schedules...")

class Cronograma(customtkinter.CTk):
    def __init__(self, atividades, table_cargas, poligonos):
        super().__init__()
        global debug
        pasta_debug = "config/interface.txt"
        
        if pasta_debug:
            with open(pasta_debug, 'r') as file:
                text = file.read()
                linhas = text.split("\n")
                for linha in linhas:
                    if("debug" in linha and "True" in linha):
                        debug = True

        self.folga_clique = 15 #quanto
        self.largura_coluna = 30
        self.margem_esquerda = 250
        self.valorrrr = "b"
        self.title("Cronograma")
        w, h = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry("%dx%d+0+0" % (w, h))


        self.altura_linha = 30
        self.canvas_frame = customtkinter.CTkScrollableFrame(self)
        self.canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.canvas = tk.Canvas(self.canvas_frame, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.atividades =   atividades
        self.table_cargas = table_cargas
        self.poligonos = poligonos
        self.retangulo_selecionado = None
        self.offset_x = 0
        self.exibir_cronograma()
        self.exibir_horas()
        
        self.canvas.bind("<Button-1>", self.selecionar_retangulo)
        self.canvas.bind("<B1-Motion>", self.arrastar_retangulo)
        self.canvas.bind("<Motion>", self.atualizar_label_dicionario)  # Adicionando o evento de movimento do mouse
        
        self.label_frame = tk.Frame(self)
        if(debug == True):
            self.label_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=10, pady=10) #serve para mostrar os dados do dicionario no canto da tela
        
        self.label_dicionario = ttk.Label(self.label_frame, text="", justify="left")
        self.label_dicionario.pack(fill=tk.BOTH, expand=True)

        self.atualizar_label_dicionario()  # Inicializando a label com os valores corretos

    def atualizar_label_dicionario(self, event=None):  # Adicionando um argumento opcional
        try:
            # Captura as coordenadas de todos os retângulos
            coordenadas_retangulos = self.canvas.find_withtag("atividades")
            atividades = []
            i=0
            for retangulo in coordenadas_retangulos:

                x1, y1, x2, y2 = self.canvas.coords(retangulo)
                #print(str(x1) +","+ str(x2))
                atividades.append( (x1,x2))
            
            # Atualiza o texto da label com as atividades associadas às coordenadas
            texto = ""
            i=0
            dicionario = {}
            for nome,coords in self.atividades.items():
                coords_atuais = atividades[i]
                hora_inicial = (coords_atuais[0]-self.margem_esquerda)/self.largura_coluna
                hora_final = (coords_atuais[1]-self.margem_esquerda)/self.largura_coluna
                self.atividades[nome] = {"inicio": hora_inicial, "fim": hora_final}
                texto+= "'" + nome + "'" + ": " + str(self.atividades[nome]) +'\n'

                i+=1

            #print(str(self.atividades))
            self.label_dicionario.config(text=texto)


            self.enviar_valor(self.atividades) #mantem o valor atualizado na classe pai
        except:
            print("erro de captura de movimento do mouse no Cronograma")




    def exibir_cronograma(self):
        self.canvas.delete("atividades")
        y_pos = 50
        for nome, horarios in self.atividades.items():
            inicio = horarios["inicio"]
            fim = horarios["fim"]
            cor = "lightblue"  # Cor para os retângulos das tarefas
            self.canvas.create_text(self.altura_linha, y_pos, anchor=tk.W, text=nome)
            
            x_inicio = self.margem_esquerda + inicio * self.largura_coluna
            x_fim = self.margem_esquerda + fim * self.largura_coluna
            retangulo = self.canvas.create_rectangle(x_inicio, y_pos - self.altura_linha/2+3, x_fim, y_pos + self.altura_linha/2 - 3, fill=cor, tags=("atividades",))
            self.canvas.tag_bind(retangulo, "<Button-1>", lambda event, nome=nome: self.selecionar_retangulo(event, nome))
            y_pos += self.altura_linha

    def exibir_horas(self):
        for hora in range(25):
            x = self.margem_esquerda + hora * self.largura_coluna
            self.canvas.create_text(x, 10, text=str(hora), anchor=tk.N)

    def selecionar_retangulo(self, event, nome=None):
        self.retangulo_selecionado = event.widget.find_closest(event.x, event.y)[0]
        x1, _, x2, _ = self.canvas.coords(self.retangulo_selecionado)
        self.offset_x = event.x - x1 if event.x < x2 - 5 else x2 - event.x

    def arrastar_retangulo(self, event):
        try:
            if self.retangulo_selecionado:
                x, _ = event.x, event.y  # Apenas atualize a coordenada horizontal
                x1, _, x2, _ = self.canvas.coords(self.retangulo_selecionado)
                if event.x < x2 - self.folga_clique and event.x<=self.margem_esquerda+20+24*self.largura_coluna:  # Arraste para a esquerda (início)
                    novo_inicio = max(0, (x - self.margem_esquerda) // self.largura_coluna)
                    self.canvas.coords(self.retangulo_selecionado, self.margem_esquerda + novo_inicio * self.largura_coluna, self.canvas.coords(self.retangulo_selecionado)[1], x2, self.canvas.coords(self.retangulo_selecionado)[3])
                elif event.x > x1 + self.folga_clique and event.x<=self.margem_esquerda+20+24*self.largura_coluna:  # Arraste para a direita (fim)
                    novo_fim = max(1, (x - self.margem_esquerda) // self.largura_coluna)
                    self.canvas.coords(self.retangulo_selecionado, x1, self.canvas.coords(self.retangulo_selecionado)[1], self.margem_esquerda + novo_fim * self.largura_coluna, self.canvas.coords(self.retangulo_selecionado)[3])
                self.atualizar_label_dicionario()
        except:
            print("Erro no Schedule")

    def atualizar_label_continuamente(self):
        try:

            self.atualizar_label_dicionario()
            self.after(500, self.atualizar_label_continuamente)  # Atualiza a cada 1 segundo (1000 milissegundos)
        except:
            print("Erro tipo 2 no Schedule")   


    def converter_para_horas_minutos(self, valor):
        horas = valor // 60
        minutos = valor % 60
        return f"{horas:02d}:{minutos:02d}"

    def atualizar_dicionario(self, event):
        try:
            if self.retangulo_selecionado:
                x1, y1, x2, y2 = self.canvas.coords(self.retangulo_selecionado)
                inicio = max(0, (x1 - self.margem_esquerda) // self.largura_coluna)
                fim = min(24, (x2 - self.margem_esquerda) // self.largura_coluna)
                for nome, coords in self.atividades.items():
                    if coords["inicio"] == inicio and coords["fim"] == fim:
                        # Verifica se houve mudança nos valores
                        if coords != {"inicio": inicio, "fim": fim}:
                            self.atividades[nome] = {"inicio": inicio, "fim": fim}
                            self.atualizar_label_dicionario()
                        break
                self.retangulo_selecionado = None
        
        except:
            print("Erro do tipo 3 no Schedule")

    def enviar_valor(self, dicionario_atividades):
        self.valorrrr = dicionario_atividades
        i = 0
        for nome_equipamento, valor  in dicionario_atividades.items():
            inicio = int(valor["inicio"])
            fim = int(valor["fim"])

            self.table_cargas.setItem(i,6, QtWidgets.QTableWidgetItem(str(inicio)))
            self.table_cargas.setItem(i,7, QtWidgets.QTableWidgetItem(str(fim)))
            i+=1
        self.atualizar_anotações_ambientes()


    def atualizar_anotações_ambientes(self):
        #zera as anotações de cada ambiente
        tabela_arr = eventosTabela.ConteudosTabela_ARR(self.table_cargas)
        i_andar = 0
        for andar in self.poligonos:
            i=0
            for poligono_, cor, nome_ambiente, dados_adicionais in self.poligonos[i_andar]:
                dados_adicionais["Ocupantes"] = 0
                dados_adicionais["Ocupantes_hora"] = []
                for i_ in range(25):
                    dados_adicionais["Ocupantes_hora"].append(0)
                self.poligonos[i_andar][i][3] = dados_adicionais 
                i+=1
            i_andar+=1

        #zera 
        for hora in range(25):


            for linha in tabela_arr:
                ambiente = linha[0]
                classe = linha[2]
                quantidade = int(linha[3])
                inicio = int(linha[6])
                fim = int(linha[7])
                andar = int(linha[4])
                if(classe == "Ocupantes" and hora>= inicio and hora<= fim):
                    i = 0
                    for poligono_, cor, nome_ambiente, dados_adicionais in self.poligonos[andar]:
                        if(ambiente == nome_ambiente):
                            dados_adicionais["Ocupantes_hora"][hora] += quantidade
                            self.poligonos[andar][i][3] = dados_adicionais 
                        i+=1
        i=0
        for poligono_, cor, nome_ambiente, dados_adicionais in self.poligonos[andar]:
            dados_adicionais["Ocupantes"] = max(dados_adicionais["Ocupantes_hora"])
            self.poligonos[andar][i][3] = dados_adicionais 
            i+=1 
        

if __name__ == "__main__":
    atividades = {
            "Atividade 1": {"inicio": 8 , "fim": 12},
            "Atividade 2": {"inicio": 13, "fim": 15},
            "Atividade 3": {"inicio": 13, "fim": 19}
            # Adicione mais atividades conforme necessário
        }
    app = Cronograma(atividades)
    app.mainloop()
