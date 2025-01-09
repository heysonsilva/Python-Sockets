import socket
import os

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
                elif dadoSolicitado.lower().startswith("sget "):
                    # Extrai o nome do arquivo solicitado após "sget "
                    arquivo_solicitado = dadoSolicitado[5:]

                    # Caminho completo do arquivo solicitado
                    caminho_arquivo = os.path.realpath(os.path.join(DIRBASE, arquivo_solicitado))

                    # Verifica se o caminho real do arquivo está dentro da pasta 'files/'
                    if os.path.commonpath([caminho_arquivo, os.path.realpath(DIRBASE)]) != os.path.realpath(DIRBASE):
                        cliente.sendall(b" Acesso negado O arquivo esta fora da pasta permitida.\n")
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
                                    cliente.sendall(dados)  # Envia os dados ao cliente
                            # Envia o sinal de fim de arquivo depois de toda a transmissão
                            cliente.sendall(b"EOF")
                            print(f"✔ Arquivo '{arquivo_solicitado}' enviado com sucesso!")
                        except Exception as e:
                            print(f"Erro ao ler o arquivo {arquivo_solicitado}: {e}")
                            cliente.sendall(b"Erro ao enviar o arquivo.")
                            cliente.sendall(b"EOF")
                    else:
                        # Arquivo não encontrado
                        mensagemDeErro = f"❌ Arquivo '{arquivo_solicitado}' não encontrado.\n"
                        cliente.sendall(mensagemDeErro.encode('utf-8'))
                        cliente.sendall(b"EOF")
                        print(mensagemDeErro.strip())

        except Exception as e:
            print(f"⚠ Erro durante a comunicação com o cliente: {e}")

        finally:
            # Encerra a conexão com o cliente
            cliente.close()
            print(f"Conexão encerrada com: {endereco}")

except KeyboardInterrupt:
    print("\n  ❗ Servidor encerrado pelo usuário.")

finally:
    server.close()