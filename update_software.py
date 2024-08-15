import sys
import requests
import zipfile

def download_file_from_google_drive(file_id, destination):
    URL = "https://docs.google.com/uc?export=download&confirm=1"

    session = requests.Session()

    response = session.get(URL, params={"id": file_id}, stream=True)
    token = get_confirm_token(response)

    if token:
        params = {"id": file_id, "confirm": token}
        response = session.get(URL, params=params, stream=True)

    save_response_content(response, destination)


def get_confirm_token(response):
    for key, value in response.cookies.items():
        if key.startswith("download_warning"):
            return value

    return None


def save_response_content(response, destination):
    CHUNK_SIZE = 32768

    with open(destination, "wb") as f:
        for chunk in response.iter_content(CHUNK_SIZE):
            if chunk:  # filter out keep-alive new chunks
                f.write(chunk)



def obter_id():
    

    # URL do link que contém o texto cru
    url = "https://pastebin.com/raw/umfXvF2C"

    # Fazendo a requisição HTTP para obter o conteúdo do link
    response = requests.get(url)

    # Verificando se a requisição foi bem-sucedida (código de status 200)
    if response.status_code == 200:
        # Salvando o conteúdo do texto na variável 'texto'
        texto = response.text
    else:
        print(f"Falha ao acessar o link. Status code: {response.status_code}")
    linhas = texto.splitlines()
    id = linhas[0]
    data = linhas[1]
    dia = int(data.split("/")[0])*1 + int(data.split("/")[1])*1000 + int(data.split("/")[2])*1000000
    return id, dia


import os

def extrair_arquivo_zip():
    caminho_arquivo_zip = 'update.zip'
    diretorio_destino = 'lib_RS'
    # Verifica se o arquivo zip existe
    if not os.path.exists(caminho_arquivo_zip):
        raise FileNotFoundError(f"O arquivo {caminho_arquivo_zip} não foi encontrado.")

    # Cria o diretório de destino se ele não existir
    if not os.path.exists(diretorio_destino):
        os.makedirs(diretorio_destino)

    # Abre o arquivo zip
    with zipfile.ZipFile(caminho_arquivo_zip, 'r') as zip_ref:
        # Extrai todos os arquivos para o diretório destino
        zip_ref.extractall(diretorio_destino)

    print(f"Arquivos extraídos para: {diretorio_destino}")
    print("Atualização Completa!")
    # Exemplo de uso

def iniciarRefrigerationStudio():
    import subprocess

    # Caminho para o executável que você deseja iniciar
    caminho_executavel = '/lib_RS/RefrigerationStudio.exe'

    # Executa o programa
    caminho_atual = os.getcwd()
    
    caminho_completo = caminho_atual+caminho_executavel
    print(caminho_completo)
    print("RefrigerationStudio Iniciando...")
    subprocess.call([caminho_completo])


    # Encerra o programa chamador

    exit()

def atualizar_ou_nao(dia_novo):
    # Caminho do arquivo .txt
    caminho_arquivo = "lib_RS/vr"
    dia_instalado = None
    # Abrir e ler o conteúdo do arquivo
    with open(caminho_arquivo, 'r', encoding='utf-8') as arquivo:
        conteudo = arquivo.read()
        dia_instalado = int(conteudo)
    # Aqui você pode modificar o conteúdo, se necessário
    # Exemplo: adicionar uma linha ao conteúdo

    if(dia_novo > dia_instalado):
        return True

    return False



def registra_nova_versao(dia_novo):
    novo_conteudo = dia_novo
    caminho_arquivo = "lib_RS/vr"
    # Reescrever o conteúdo no mesmo arquivo
    with open(caminho_arquivo, 'w', encoding='utf-8') as arquivo:
        arquivo.write(str(dia_novo))

    print(str(dia_novo))

def main():
    id, dia_novo = obter_id()

    if(atualizar_ou_nao(dia_novo) == True):
        if len(sys.argv) >= 3:
            file_id = sys.argv[1]
            destination = sys.argv[2]
        else:
            file_id = id
            destination = "update.zip"
        print(f"dowload {file_id} to {destination}")
        download_file_from_google_drive(file_id, destination)
        extrair_arquivo_zip()
        registra_nova_versao(dia_novo)

    else:
        print("ultima versão instalada")
    iniciarRefrigerationStudio()

if __name__ == "__main__":
    main()