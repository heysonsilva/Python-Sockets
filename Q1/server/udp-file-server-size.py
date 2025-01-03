import os
import socket

# Definindo o IP e a porta que o servidor vai escutar
ip_servidor = '0.0.0.0'  # O servidor escuta em todas as interfaces
porta_servidor = 12048    # Porta que o servidor vai escutar

# Criação do socket UDP
servidor = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Vinculando o socket ao IP e à porta
servidor.bind((ip_servidor, porta_servidor))

print(f"Servidor iniciado em {ip_servidor}:{porta_servidor}")

# Esperando por requisições do cliente
while True:
    # Recebe o nome do arquivo solicitado
    nome_arquivo_bytes, endereco_cliente = servidor.recvfrom(4096)
    nome_arquivo = nome_arquivo_bytes.decode()

    print(f"Cliente solicitou o arquivo: {nome_arquivo}")

    # Verificando se o arquivo existe
    if os.path.exists(nome_arquivo):
        # Obtendo o tamanho do arquivo em bytes
        tamanho_arquivo = os.path.getsize(nome_arquivo)
        servidor.sendto(str(tamanho_arquivo).encode(), endereco_cliente)  # Envia o tamanho do arquivo
        print(f"Tamanho do arquivo {nome_arquivo} enviado para o cliente.")

        # Abrindo o arquivo para enviar por partes
        arquivo = open(nome_arquivo, 'rb')  # Abrindo o arquivo em modo de leitura binária
        conteudo_arquivo = arquivo.read(4096)  # Lê o primeiro pedaço do arquivo

        while conteudo_arquivo:
            # Enviando por partes
            servidor.sendto(conteudo_arquivo, endereco_cliente)
            conteudo_arquivo = arquivo.read(4096)

        arquivo.close()  # Fechando o arquivo corretamente após o envio
        print(f"Arquivo {nome_arquivo} enviado com sucesso para o cliente.")
    
    else:
        # Mensagem de erro caso o arquivo não exista
        mensagem_erro = "Arquivo não encontrado."
        servidor.sendto(mensagem_erro.encode(), endereco_cliente)
        print(f"O arquivo {nome_arquivo} não foi encontrado.")
