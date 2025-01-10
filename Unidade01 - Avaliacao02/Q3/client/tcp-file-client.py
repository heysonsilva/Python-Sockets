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
        dadoSolicitado = input(
            "\n -- COMANDOS DISPONÍVEIS --\n\n"
            ">> sget <nome_arquivo>: BAIXAR ARQUIVO\n"
            ">> mget <máscara>: BAIXAR ARQUIVOS COM MÁSCARA\n"
            ">> list: LISTAR ARQUIVOS\n"
            ">> sha1 <nome_do_arquivo> <posicao>: CALCULAR HASH SHA1\n"
            ">> sair: ENCERRAR CONEXÃO\n ==> "
        )

        if dadoSolicitado.lower() == 'sair':
            print(">> Encerrando a conexão...")
            break

        # Envia o comando ao servidor
        cliente_socket.sendall(dadoSolicitado.encode('utf-8'))

        if dadoSolicitado.lower() == 'list':
            print("\n>>> Listando arquivos disponíveis no servidor:\n")
            while True:
                dados = cliente_socket.recv(4096).decode('utf-8')
                if dados == "EOF":
                    print("\n >>> Fim da listagem <<<")
                    break
                print(dados.strip())

        elif 'sget ' in dadoSolicitado.lower():
            arquivo_solicitado = dadoSolicitado[5:]
            caminho_arquivo = os.path.join(DIRBASE, arquivo_solicitado)

            print(f"Solicitando o download do arquivo: {arquivo_solicitado}")

            if not os.path.exists(DIRBASE):
                os.makedirs(DIRBASE)

            with open(caminho_arquivo, 'wb') as arquivo:
                while True:
                    dados = cliente_socket.recv(4096)
                    if dados == b"EOF":
                        print(">>> Fim da transmissão <<<")
                        break
                    if dados:
                        arquivo.write(dados)

            print(f"\u2714 Arquivo '{arquivo_solicitado}' recebido e salvo em '{caminho_arquivo}' \u2714")

        elif 'mget ' in dadoSolicitado.lower():
            mascara = dadoSolicitado[5:].strip()
            print(f"Solicitando download de arquivos com máscara: {mascara}")

            # Certifique-se de que o diretório base existe
            if not os.path.exists(DIRBASE):
                os.makedirs(DIRBASE)

            while True:
                # Recebe mensagem do servidor
                dados = cliente_socket.recv(4096).decode('utf-8')

                # Verifica se é o início de um novo arquivo
                if dados.startswith("START "):
                    nome_arquivo = dados[6:].strip()  # Obtém o nome do arquivo
                    caminho_arquivo = os.path.join(DIRBASE, nome_arquivo)

                    # Verifica se o arquivo já existe no cliente
                    if os.path.exists(caminho_arquivo):
                        sobrescrever = input(f"Arquivo '{nome_arquivo}' já existe. Deseja sobrescrever? (s/n): ").lower()
                        if sobrescrever != 's':
                            print(f"\u26a0 Arquivo '{nome_arquivo}' ignorado.")
                            # Continua para o próximo arquivo
                            continue

                    # Recebe e grava o arquivo
                    print(f"Recebendo arquivo: {nome_arquivo}")
                    with open(caminho_arquivo, 'wb') as arquivo:
                        while True:
                            dados = cliente_socket.recv(4096)
                            if dados == b"EOF":  # Sinal de fim do arquivo
                                print(f"\u2714 Arquivo '{nome_arquivo}' recebido com sucesso!\n")
                                break
                            arquivo.write(dados)

                # Verifica se é o fim do processo de mget
                elif dados == "MGET EOF":  # Sinal específico para o fim de `mget`
                    print("\n>>> Fim do download dos arquivos <<<")
                    break

                # Exibe mensagens de erro ou alertas
                elif "Erro" in dados or "nenhum arquivo" in dados.lower():
                    print(dados.strip())
                    break

        elif 'sha1 ' in dadoSolicitado.lower():
            try:
                cliente_socket.sendall(dadoSolicitado.encode('utf-8'))
                print(f"Solicitando SHA1 para o arquivo especificado...")

                while True:
                    dados = cliente_socket.recv(4096).decode('utf-8')
                    if dados == "EOF":
                        break
                    print(dados.strip())

            except Exception as e:
                print(f"Erro ao solicitar o SHA1: {e}")

        else:
            print("Comando inválido. Tente novamente.")

except KeyboardInterrupt:
    print("\n" + "=" * 30 + "\n \u26a0 CONEXÃO ENCERRADA \u26a0\n" + "=" * 30)

finally:
    cliente_socket.close()
