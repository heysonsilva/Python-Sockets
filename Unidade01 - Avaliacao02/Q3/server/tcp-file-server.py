import socket
import os
import glob
import hashlib

#  essa função define os protocolos de rede e transporte do algoritmo, e com os
# metodos bind() e listen() liga o servidor e deixa ele em estado de escuta, respectivamente 
def configurar_servidor(host, porta, diretorio_base):
    os.makedirs(diretorio_base, exist_ok=True)
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.bind((host, porta))
    servidor.listen()
    print(f"Servidor rodando em {host}:{porta}")
    return servidor

# Validar se o caminho pertence à pasta permitida.
def validar_caminho(diretorio_base, nome_arquivo):
    caminho_absoluto = os.path.realpath(os.path.join(diretorio_base, nome_arquivo))
    if not caminho_absoluto.startswith(os.path.realpath(diretorio_base)):
        return None
    return caminho_absoluto

# Listagem de Arquivos
def listar_arquivos(conexao, diretorio_base): 
    arquivos = os.listdir(diretorio_base)
    lista_arquivos = [
        f"{arquivo} - {os.path.getsize(os.path.join(diretorio_base, arquivo))} bytes"
        for arquivo in arquivos if os.path.isfile(os.path.join(diretorio_base, arquivo))
    ]
    resposta = "\n".join(lista_arquivos) if lista_arquivos else "Nenhum arquivo encontrado."
    conexao.send(resposta.encode('utf-8'))
# Função de envio de arquivos
def enviar_arquivo(conexao, diretorio_base, nome_arquivo):
    caminho_arquivo = validar_caminho(diretorio_base, nome_arquivo)
    if caminho_arquivo and os.path.exists(caminho_arquivo):
        conexao.send(b"OK")
        tamanho_arquivo = os.path.getsize(caminho_arquivo)
        conexao.send(tamanho_arquivo.to_bytes(8, 'big'))
        with open(caminho_arquivo, 'rb') as arquivo:
            while chunk := arquivo.read(4096):
                conexao.send(chunk)
    else:
        conexao.send(b"NAO_ENCONTRADO")

def enviar_multiplos_arquivos(conexao, diretorio_base, mascara):
    # Ajuste para garantir que a máscara é aplicada dentro do diretório permitido
    caminho_mascara = os.path.join(diretorio_base, mascara)
    arquivos_correspondentes = glob.glob(caminho_mascara)
    arquivos = [os.path.basename(f) for f in arquivos_correspondentes if os.path.isfile(f)]

    if arquivos:
        conexao.send(b"OK")
        conexao.send(len(arquivos).to_bytes(4, 'big'))
        for arquivo in arquivos:
            caminho_arquivo = os.path.join(diretorio_base, arquivo)
            conexao.send(arquivo.strip().encode('utf-8'))  # Remove espaços e caracteres extras
            tamanho_arquivo = os.path.getsize(caminho_arquivo)
            conexao.send(tamanho_arquivo.to_bytes(8, 'big'))
            with open(caminho_arquivo, 'rb') as f:
                while chunk := f.read(4096):
                    conexao.send(chunk)
    else:
        conexao.send(b"NAO_ENCONTRADO")

def calcular_hash(conexao, diretorio_base, nome_arquivo, quantidade_bytes):
    caminho_arquivo = validar_caminho(diretorio_base, nome_arquivo)
    if caminho_arquivo and os.path.isfile(caminho_arquivo):
        with open(caminho_arquivo, 'rb') as arquivo:
            dados = arquivo.read(quantidade_bytes)
            hash_arquivo = hashlib.sha1(dados).hexdigest()
        conexao.send(hash_arquivo.encode('utf-8'))
    else:
        conexao.send(b"NAO_ENCONTRADO")

def continuar_download(conexao, diretorio_base, nome_arquivo, hash_parte_cliente):
    caminho_arquivo = validar_caminho(diretorio_base, nome_arquivo)
    if not caminho_arquivo or not os.path.exists(caminho_arquivo):
        conexao.send(b"NAO_ENCONTRADO")
        return

    with open(caminho_arquivo, 'rb') as arquivo:
        dados = arquivo.read()
        hash_servidor = hashlib.sha1(dados).hexdigest()

    if hash_parte_cliente != hash_servidor[:len(hash_parte_cliente)]:
        conexao.send(b"HASH_INCORRETO")
        return

    conexao.send(b"OK")
    tamanho_enviar = len(dados) - len(hash_parte_cliente)
    conexao.send(tamanho_enviar.to_bytes(8, 'big'))

    with open(caminho_arquivo, 'rb') as arquivo:
        arquivo.seek(len(hash_parte_cliente))
        while chunk := arquivo.read(4096):
            conexao.send(chunk)
# Funcao responsavel por determinar qual resposta será enviado para o cliente
def tratar_conexao(conexao, endereco, diretorio_base):
    print(f"Conexão estabelecida com {endereco}")
    try:
        while True:
            comando = conexao.recv(4096).decode('utf-8')
            if not comando:
                break

            if comando.startswith('list'):
                listar_arquivos(conexao, diretorio_base)
            elif comando.startswith('sget'):
                _, nome_arquivo = comando.split(maxsplit=1)
                enviar_arquivo(conexao, diretorio_base, nome_arquivo)
            elif comando.startswith('mget'):
                _, mascara = comando.split(maxsplit=1)
                enviar_multiplos_arquivos(conexao, diretorio_base, mascara)
            elif comando.startswith('hash'):
                _, nome_arquivo, quantidade_bytes = comando.split(maxsplit=2)
                calcular_hash(conexao, diretorio_base, nome_arquivo, int(quantidade_bytes))
            elif comando.startswith('cget'):
                _, nome_arquivo, hash_parte = comando.split(maxsplit=2)
                continuar_download(conexao, diretorio_base, nome_arquivo, hash_parte)
            else:
                conexao.send(b"COMANDO_INVALIDO")
    finally:
        conexao.close()

# essa é a função principal do algoritmo
def iniciar_servidor():
    HOST = '127.0.0.1'
    PORTA = 12345
    DIRETORIO_BASE = 'files'
    servidor = configurar_servidor(HOST, PORTA, DIRETORIO_BASE)
    while True:
        conexao, endereco = servidor.accept()
        tratar_conexao(conexao, endereco, DIRETORIO_BASE)

iniciar_servidor()
