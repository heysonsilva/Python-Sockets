import socket
import os
import glob
import hashlib

# Configurações do servidor
ip_server = "localhost"
port_server = 12345
DIRBASE = "files/"  # Diretório onde os arquivos estão armazenados

# Criação do socket do servidor (IPv4, TCP)
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Vincula o servidor ao IP e porta
server.bind((ip_server, port_server))

# Inicia o servidor em modo "escuta"
server.listen()

print(f"Servidor esperando por conexões em {ip_server}:{port_server}")

try:
    while True:
        # Aceita conexões de clientes
        cliente, endereco = server.accept()
        print(f"Conexão estabelecida com: {endereco}")

        try:
            while True:
                # Recebe o nome do arquivo ou comando solicitado
                dadoSolicitado = cliente.recv(1024).decode('utf-8')

                # Se não houver dados, encerra a conexão
                if not dadoSolicitado:
                    break

                # Comando para listar arquivos
                if dadoSolicitado.lower() == 'list':
                    print("Solicitação de listagem de arquivos recebida.")
                    arquivos = os.listdir(DIRBASE)

                    if arquivos:
                        for arquivo in arquivos:
                            caminho_arquivo = os.path.join(DIRBASE, arquivo)
                            if os.path.isfile(caminho_arquivo):
                                tamanho_arquivo = os.path.getsize(caminho_arquivo)
                                cliente.sendall(f"{arquivo} | {tamanho_arquivo} bytes\n".encode('utf-8'))
                    else:
                        cliente.sendall(b"Nenhum arquivo encontrado.\n")

                    cliente.sendall(b"EOF")

                # Comando para download de arquivo único
                elif "sget " in dadoSolicitado.lower():
                    arquivo_solicitado = dadoSolicitado[5:].strip()
                    caminho_arquivo = os.path.realpath(os.path.join(DIRBASE, arquivo_solicitado))

                    # Verifica se o arquivo está no diretório permitido
                    if os.path.commonpath([caminho_arquivo, os.path.realpath(DIRBASE)]) != os.path.realpath(DIRBASE):
                        cliente.sendall(b"Acesso negado. Arquivo fora da pasta permitida.\n")
                        cliente.sendall(b"EOF")
                        print(f"⚠ Tentativa de acesso a arquivo fora da pasta: {arquivo_solicitado}")
                        continue

                    if os.path.isfile(caminho_arquivo):
                        print(f"✔ Enviando arquivo: {arquivo_solicitado}")
                        try:
                            with open(caminho_arquivo, "rb") as arquivo:
                                while True:
                                    dados = arquivo.read(4095)
                                    if not dados:
                                        break
                                    cliente.sendall(dados)
                            cliente.sendall(b"EOF")
                            print(f"✔ Arquivo '{arquivo_solicitado}' enviado com sucesso!")
                        except Exception as e:
                            print(f"Erro ao ler o arquivo {arquivo_solicitado}: {e}")
                            cliente.sendall(b"Erro ao enviar o arquivo.\n")
                            cliente.sendall(b"EOF")
                    else:
                        cliente.sendall(f"Arquivo '{arquivo_solicitado}' não encontrado.\n".encode('utf-8'))
                        cliente.sendall(b"EOF")

                # Comando para download de múltiplos arquivos
                elif "mget " in dadoSolicitado.lower():
                    mascara = dadoSolicitado[5:].strip()
                    print(f"✔ Solicitação de mget com máscara: {mascara}")

                    # Obtém arquivos que correspondem à máscara
                    arquivos_correspondentes = glob.glob(os.path.join(DIRBASE, mascara))

                    if arquivos_correspondentes:
                        for caminho_arquivo in arquivos_correspondentes:
                            if os.path.isfile(caminho_arquivo):
                                nome_arquivo = os.path.basename(caminho_arquivo)
                                try:
                                    # Envia mensagem de início do envio de um arquivo
                                    cliente.sendall(f"START {nome_arquivo}\n".encode('utf-8'))

                                    # Envia o conteúdo do arquivo
                                    with open(caminho_arquivo, "rb") as arquivo:
                                        while True:
                                            dados = arquivo.read(4095)
                                            if not dados:
                                                cliente.sendall(b"EOF")
                                                break
                                            cliente.sendall(dados)

                                    print(f"✔ Arquivo '{nome_arquivo}' enviado com sucesso!")

                                except Exception as e:
                                    print(f"Erro ao enviar o arquivo {nome_arquivo}: {e}")
                                    cliente.sendall(f"Erro ao enviar o arquivo {nome_arquivo}.\n".encode('utf-8'))
                                    cliente.sendall(b"EOF")
                    else:
                        # Envia mensagem de erro se nenhum arquivo corresponder à máscara
                        cliente.sendall(b"Nenhum arquivo correspondente encontrado.\n")
                        cliente.sendall(b"EOF")

                    # Envia sinal de fim do comando `mget`
                    cliente.sendall(b"MGET EOF")

                # Comando para calcular o hash SHA1 até uma posição específica
                elif "sha1 " in dadoSolicitado.lower():
                    try:
                        partes = dadoSolicitado.split()
                        if len(partes) != 3:
                            cliente.sendall(b"Comando invalido. Use: sha1 <arquivo> <posicao>\n")
                            cliente.sendall(b"EOF")
                            continue

                        arquivo_solicitado, limite = partes[1], partes[2]

                        try:
                            limite = int(limite)
                        except ValueError:
                            cliente.sendall(b"Posicao invalida. Deve ser um numero inteiro.\n")
                            cliente.sendall(b"EOF")
                            continue

                        caminho_arquivo = os.path.realpath(os.path.join(DIRBASE, arquivo_solicitado))

                        # Verifica se o arquivo está na pasta files
                        if os.path.commonpath([caminho_arquivo, os.path.realpath(DIRBASE)]) != os.path.realpath(DIRBASE):
                            cliente.sendall(b"Acesso negado. Arquivo fora da pasta permitida.\n")
                            cliente.sendall(b"EOF")
                            continue

                        if os.path.isfile(caminho_arquivo):
                            print(f"✔ Calculando SHA1 do arquivo '{arquivo_solicitado}' até a posição {limite}.")
                            hash_sha1 = hashlib.sha1()

                            with open(caminho_arquivo, 'rb') as arquivo:
                                conteudo = arquivo.read(limite)
                                hash_sha1.update(conteudo)

                            cliente.sendall(f"SHA1 até a posição {limite}: {hash_sha1.hexdigest()}\n".encode('utf-8'))
                        else:
                            cliente.sendall(f"Arquivo '{arquivo_solicitado}' não encontrado.\n".encode('utf-8'))

                    except Exception as e:
                        cliente.sendall(f"Erro ao calcular o hash: {str(e)}\n".encode('utf-8'))

                    cliente.sendall(b"EOF")

        except Exception as e:
            print(f"⚠ Erro durante a comunicação com o cliente: {e}")

        finally:
            cliente.close()
            print(f"Conexão encerrada com: {endereco}")

except KeyboardInterrupt:
    print("\n ❗ Servidor encerrado pelo usuário.")

finally:
    server.close()
