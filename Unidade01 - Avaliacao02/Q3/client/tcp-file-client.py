import socket
import os
import hashlib

HOST = '127.0.0.1'
PORT = 12345
DIRETORIO_BASE = 'files'
os.makedirs(DIRETORIO_BASE, exist_ok=True)

def calcular_hash_parcial(caminho_arquivo):
    # Calcula o hash SHA1 de um arquivo parcial.
    with open(caminho_arquivo, 'rb') as arquivo:
        dados = arquivo.read()
        return hashlib.sha1(dados).hexdigest()

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.connect((HOST, PORT))
    print(f"Conectado ao servidor {HOST}:{PORT}")
    
    while True:
        print("\n==== Comandos disponíveis ====\n")
        print(">> list - Listar arquivos")
        print(">> sget - Baixar um arquivo")
        print(">> mget - Baixar múltiplos arquivos por máscara")
        print(">> hash - Calcular hash de um arquivo")
        print(">> cget - Continuar download de um arquivo")
        print(">> sair - Encerrar conexão")
        
        comando = input("\nDigite o comando: ").lower()
        if comando == "sair":
            break

        if comando == "list":
            sock.send(comando.encode('utf-8'))
            resposta = sock.recv(4096).decode('utf-8')
            print(resposta)

        elif comando == "sget":
            nome_arquivo = input("Digite o nome do arquivo para download: ")
            caminho_arquivo = os.path.join(DIRETORIO_BASE, nome_arquivo)

            # Verifica se o arquivo já existe
            if os.path.exists(caminho_arquivo):
                overwrite = input(f"O arquivo '{nome_arquivo}' já existe. Deseja sobrescrever? (s/n): ").lower()
                if overwrite != 's':
                    print("Download cancelado pelo usuário.")
                    continue

            sock.send(f"{comando} {nome_arquivo}".encode('utf-8'))
            status = sock.recv(4096).decode('utf-8')

            if status == "OK":
                tamanho_arquivo = int.from_bytes(sock.recv(8), 'big')
                with open(caminho_arquivo, 'wb') as arquivo:
                    recebido = 0
                    while recebido < tamanho_arquivo:
                        dados = sock.recv(4096)
                        arquivo.write(dados)
                        recebido += len(dados)
                print(f"Download do arquivo '{nome_arquivo}' concluído.")
            elif status == "NAO_ENCONTRADO":
                print("Arquivo não encontrado no servidor.")
            else:
                print("Erro desconhecido do servidor.")

        elif comando == "mget":
            mascara = input("Digite a máscara (ex: *.txt): ")
            sock.send(f"{comando} {mascara}".encode('utf-8'))
            status = sock.recv(4096)
            if status == b"OK":
                num_arquivos = int.from_bytes(sock.recv(4), 'big')
                print(f"{num_arquivos} arquivos encontrados.")
                for _ in range(num_arquivos):
                    nome_arquivo = sock.recv(4096).decode('utf-8')
                    tamanho_arquivo = int.from_bytes(sock.recv(8), 'big')
                    caminho_arquivo = os.path.join(DIRETORIO_BASE, nome_arquivo)
                    if os.path.exists(caminho_arquivo):
                        overwrite = input(f"O arquivo '{nome_arquivo}' já existe. Sobrescrever? (s/n): ").lower()
                        if overwrite != 's':
                            print(f"Arquivo '{nome_arquivo}' ignorado.")
                            sock.recv(tamanho_arquivo)  # Ignora os dados do arquivo
                            continue
                    with open(caminho_arquivo, 'wb') as arquivo:
                        recebido = 0
                        while recebido < tamanho_arquivo:
                            dados = sock.recv(4096)
                            arquivo.write(dados)
                            recebido += len(dados)
                    print(f"Download do arquivo '{nome_arquivo}' concluído.")
            elif status == b"NAO_ENCONTRADO":
                print("Nenhum arquivo correspondente encontrado no servidor.")
            else:
                print("Erro desconhecido do servidor.")

        elif comando == "hash":
            nome_arquivo = input("Digite o nome do arquivo: ")
            num_bytes = input("Quantos bytes iniciais para hash? ").strip()
            sock.send(f"{comando} {nome_arquivo} {num_bytes}".encode('utf-8'))
            resposta = sock.recv(4096).decode('utf-8')
            print(resposta)

        elif comando == "cget":
            nome_arquivo = input("Digite o nome do arquivo para continuar o download: ")
            caminho_arquivo = os.path.join(DIRETORIO_BASE, nome_arquivo)

            if not os.path.exists(caminho_arquivo):
                print(f"O arquivo '{nome_arquivo}' não existe no cliente.")
                continue

            hash_parte = calcular_hash_parcial(caminho_arquivo)
            sock.send(f"{comando} {nome_arquivo} {hash_parte}".encode('utf-8'))
            status = sock.recv(4096).decode('utf-8')

            if status == "NAO_ENCONTRADO":
                print("Arquivo não encontrado no servidor.")
            elif status == "HASH_INCORRETO":
                print("Hash do cliente não corresponde ao hash do servidor.")
            elif status == "OK":
                tamanho_enviar = int.from_bytes(sock.recv(8), 'big')
                with open(caminho_arquivo, 'ab') as arquivo:
                    recebido = 0
                    while recebido < tamanho_enviar:
                        dados = sock.recv(4096)
                        arquivo.write(dados)
                        recebido += len(dados)
                print(f"Download do arquivo '{nome_arquivo}' continuado com sucesso.")
            else:
                print("Erro desconhecido.")

        else:
            print("Comando inválido.")
