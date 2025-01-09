import socket
import os
import glob

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

                # Se o comando for 'list', envia a listagem de arquivos
                if dadoSolicitado.lower() == 'list':
                    print("Solicitação de listagem de arquivos recebida.")
                    arquivos = os.listdir(DIRBASE)

                    if arquivos:
                        for arquivo in arquivos:
                            caminho_arquivo = os.path.join(DIRBASE, arquivo)
                            if os.path.isfile(caminho_arquivo):
                                # Envia o nome e o tamanho do arquivo
                                tamanho_arquivo = os.path.getsize(caminho_arquivo)
                                cliente.sendall(f"{arquivo} | {tamanho_arquivo} bytes\n".encode('utf-8'))
                    else:
                        cliente.sendall(b"Nenhum arquivo encontrado.\n")

                    # Envia o sinal de fim da listagem
                    cliente.sendall(b"EOF")

                # Verificação para o comando de download
                elif "sget " in dadoSolicitado.lower():
                    arquivo_solicitado = dadoSolicitado[5:]  # Nome do arquivo solicitado
                    caminho_arquivo = os.path.realpath(os.path.join(DIRBASE, arquivo_solicitado))

                    # Verifica se o arquivo está dentro do diretório permitido
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
                                    dados = arquivo.read(8192)
                                    if not dados:
                                        break
                                    cliente.sendall(dados)
                            cliente.sendall(b"EOF")  # Sinal de fim do arquivo
                            print(f"✔ Arquivo '{arquivo_solicitado}' enviado com sucesso!")
                        except Exception as e:
                            print(f"Erro ao ler o arquivo {arquivo_solicitado}: {e}")
                            cliente.sendall(b"Erro ao enviar o arquivo.\n")
                            cliente.sendall(b"EOF")
                    else:
                        mensagemDeErro = f"❌ Arquivo '{arquivo_solicitado}' não encontrado.\n"
                        cliente.sendall(mensagemDeErro.encode('utf-8'))
                        cliente.sendall(b"EOF")
                        print(mensagemDeErro.strip())

                # Verificação para o comando de download múltiplo (mget)
                elif "mget " in dadoSolicitado.lower():
                    mascara = dadoSolicitado[5:].strip()  # Obtém a máscara
                    print(f"✔ Solicitação de mget com máscara: {mascara}")

                    # Obtém os arquivos correspondentes à máscara
                    arquivos_correspondentes = glob.glob(os.path.join(DIRBASE, mascara))

                    if arquivos_correspondentes:
                        for caminho_arquivo in arquivos_correspondentes:
                            if os.path.isfile(caminho_arquivo):
                                nome_arquivo = os.path.basename(caminho_arquivo)
                                try:
                                    cliente.sendall(f"START {nome_arquivo}\n".encode('utf-8'))
                                    with open(caminho_arquivo, "rb") as arquivo:
                                        while True:
                                            dados = arquivo.read(8192)
                                            if not dados:
                                                break
                                            cliente.sendall(dados)
                                    cliente.sendall(b"EOF")  # Sinal de fim de arquivo
                                    print(f"✔ Arquivo '{nome_arquivo}' enviado com sucesso!")
                                except Exception as e:
                                    print(f"Erro ao enviar o arquivo {nome_arquivo}: {e}")
                                    cliente.sendall(f"Erro ao enviar o arquivo {nome_arquivo}.\n".encode('utf-8'))
                                    cliente.sendall(b"EOF")
                    else:
                        cliente.sendall(b"Nenhum arquivo correspondente encontrado.\n")
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
