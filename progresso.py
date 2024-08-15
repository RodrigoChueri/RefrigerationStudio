import tkinter as tk
from tkinter import ttk
from tkinter import *
from tkinter.ttk import *
import time
import sys
from threading import Thread
import threading

class Progresso:
    def __init__(self):
        with open("temp/progresso.txt", "w") as arquivo:
            valor = "0"
            arquivo.write(valor)
            arquivo.close()
        self.root = tk.Tk()
        self.root.title("Progresso")
        self.root.geometry("300x200")
        self.bar = Progressbar(self.root,orient=HORIZONTAL, length=370, maximum=370)
        self.bar.pack(pady=50)
        self.perncentagem_carregado = tk.Label(self.root, text = "simulando",width=50)
        self.perncentagem_carregado.pack()
        self.atualizar()
        self.root.mainloop()

    def atualizar(self):
        continuar_loop = True
        valor = ""
        with open("temp/progresso.txt", "r") as arquivo:
            valor = arquivo.readline().strip().split(";;;")[-1]
            if("FimSimulação" in valor):
                self.perncentagem_carregado.config(text="Simulação Concluída!")
                return 0
            elif("999999" in valor):
                #sys.exit()
                self.perncentagem_carregado.config(text="Simulação Concluída!")
                self.relatorio_btn = Button(self.root, text="Fechar")
                self.relatorio_btn.pack()
                return 0
            elif(valor == ''):
                self.perncentagem_carregado.config(text="simulando")
                valor = '0'
            else:
                self.perncentagem_carregado.config(text="simulando")
            self.bar['value'] = int(valor)
            self.perncentagem_carregado.config(text=str(valor) + "/370", width=100)
            self.root.update_idletasks()
            self.perncentagem_carregado.update_idletasks()
            self.root.after(5, self.atualizar)

            


class ProgressoDia:
    def __init__(self, id, stop):
        with open("temp/progresso2.txt", "w") as arquivo:
            valor = "0"
            arquivo.write(valor)
            arquivo.close()

        self.stop = stop
        self.root = tk.Tk()
        self.root.title("Progresso")
        self.root.geometry("300x200")
        self.perncentagem_carregado = tk.Label(self.root, text = "simulando o dia",width=50)
        self.perncentagem_carregado.pack()
        self.atualizar()
        self.root.mainloop()

    def atualizar(self):
        continuar_loop = True
        valor = ""
        with open("temp/progresso2.txt", "r") as arquivo:
            valor = arquivo.readline().strip().split(";;;")[-1]
            if("Fim" in valor):
                continuar_loop = False
                self.perncentagem_carregado.config(text="Simulação Concluída!")
                return 0

        if(continuar_loop == True):
            # Chama o método atualizar novamente após 10 segundos
            self.root.after(2, self.atualizar)
            

def IniciarBarra():
    stop_threads = False
    id = 0
    thread_progresso = threading.Thread(target=ProgressoDia, args=(id, lambda: stop_threads))
    thread_progresso.start()
    time.sleep(6)
    stop_threads = True
    


if __name__ == '__main__':
    IniciarBarra()
