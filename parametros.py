# encoding: utf-8
# encoding: iso-8859-1
# encoding: win-1252
print("Carregando parâmetros iniciais...")

debug = False
pasta_debug = "config/interface.txt"

cores_paredes = {"branco":0.75, "preto":0.97} #pag 495 ashrae
#cores_paredes_list = ["Claro", "Medio", "Escuro", "branco", "preto"]
cores_paredes_list = ["Claro", "Medio", "Escuro"]
if pasta_debug:
    with open(pasta_debug, 'r') as file:
        text = file.read()
        linhas = text.split("\n")
        for linha in linhas:
            if("debug" in linha and "True" in linha):
                debug = True


def parametros_refrigeração_ambientes():
    dados = {}
    with open("bibliotecas/parametros_ventilação/parametros.txt", "r") as f:
        lines = f.readlines()
        for line in lines:
            if not line.startswith("#") and "=" in line and not line.startswith("@"):
                # Processar a linha
                tipo = line.strip().split("=")[0]
                valores = line.strip().split("=")[1].split(",")
                Rp = float(valores[0])
                Ra = float(valores[1])
                dados[tipo]=([Rp,Ra])

    return dados


def parametros_paredes():
    dicionario_inicial = {"paredes_internas":{}, "paredes_externas":{}, "divisorias":{}, "interfaces_horizontais":{}}


    with open("bibliotecas/paredes/paredes.txt", "r") as f:
        lines = f.readlines()
        classe = None
        for line in lines:

            if(line.startswith("@")):
                classe = line.replace("@","").replace("\n","")
            if not line.startswith("#") and "=" in line and not line.startswith("@"):
                # Processar a linha
                nome = line.strip().split("=")[0]
                valores = line.strip().split("=")[1].split(",")
                dicionario_parede = {"nome": nome, "espessura": valores[0], "k": valores[1], "cor": valores[2]}
                dicionario_inicial[classe][nome] = dicionario_parede
    dicionario_default = {}
    dicionario_default["paredes_internas"] = dicionario_inicial["paredes_internas"][list(dicionario_inicial["paredes_internas"].keys())[0]]
    dicionario_default["paredes_externas"]= dicionario_inicial["paredes_externas"][list(dicionario_inicial["paredes_externas"].keys())[0]]
    dicionario_default["divisorias"] = dicionario_inicial["divisorias"][list(dicionario_inicial["divisorias"].keys())[0]]
    dicionario_default["interfaces_horizontais"] = dicionario_inicial["interfaces_horizontais"][list(dicionario_inicial["interfaces_horizontais"].keys())[0]]
    

    return [dicionario_inicial, dicionario_default]


def linguagem ():
    with open("config/interface.txt", "r") as f:
        lines = f.readlines()
        for line in lines:
            chave = line.strip().split("=")[0]
            if "lang" in chave:
                # Processar a linha
                tipo = line.strip().split("=")[0]
                idioma = line.strip().split("=")[1]
                return idioma

