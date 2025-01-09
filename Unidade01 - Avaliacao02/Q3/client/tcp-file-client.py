import socket
import os

# Configurações do cliente
ip = 'localhost'
porta = 12345
DIRBASE = "files/"  # Diretório base para salvar arquivos

# Criação do socket do cliente
cliente_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Conecta ao servidor
cliente_socket.connect((ip, porta))

try:
    while True:
        # Solicita o nome do arquivo ou comando ao usuário
        dadoSolicitado = input("\n -- COMANDOS DISPONIVEIS --\n\n>> sget <nome_arquivo>: BAIXAR ARQUIVO\n>> list: LISTAR ARQUIVOS\n>> sair: ENCERRAR CONEXÃO\n ==> ")

        if dadoSolicitado.lower() == 'sair':
            print(">> Encerrando a conexão...")
            break

        # Envia o comando ao servidor
        cliente_socket.sendall(dadoSolicitado.encode('utf-8'))

        if dadoSolicitado.lower() == 'list':
            print("\n>>> Listando arquivos disponíveis no servidor:\n")
            while True:
                dados = cliente_socket.recv(8192).decode('utf-8')
                if dados == "EOF":
                    print("\n >>> Fim da listagem <<<")
                    break
                print(dados.strip())  # Exibe a lista de arquivos e tamanhos

        elif dadoSolicitado.lower().startswith('sget '):
            # Extrai o nome do arquivo solicitado
            arquivo_solicitado = dadoSolicitado[5:]
            caminho_arquivo = DIRBASE + arquivo_solicitado

            print(f"Solicitando o download do arquivo: {arquivo_solicitado}")

            # Recebe os dados do servidor e grava o arquivo
            with open(caminho_arquivo, 'wb') as arquivo:
                while True:
                    dados = cliente_socket.recv(8192)
                    if dados == b"EOF":  # Verifica o sinal de fim de transmissão
                        print(">>> Fim da transmissão <<<")
                        break
                    if dados:
                        arquivo.write(dados)

                print(f"✔ Arquivo '{arquivo_solicitado}' recebido e salvo em '{caminho_arquivo}' ✔")

        else:
            print("Comando inválido. Tente novamente.")

except KeyboardInterrupt:
    print("\n" + "="*30 + "\n ⚠ CONEXÃO ENCERRADA ⚠\n" + "="*30)

finally:
    cliente_socket.close()