import os
import socket

# Definindo o IP do servidor e a porta de comunicação
ip_servidor = '127.0.0.1'  # Endereço IP do servidor (usando o local para exemplo)
porta_servidor = 12048    # Porta que o servidor está ouvindo

# Criando o socket UDP
cliente = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Pedindo o nome do arquivo ao usuário
nome_arquivo = input("Digite o nome do arquivo que deseja receber: ")

#Enviando o nome do arquivo para o servidor
cliente.sendto(nome_arquivo.encode(), (ip_servidor, porta_servidor))

# Recebendo o tamanho do arquivo do servidor
tamanho_arquivo, _ = cliente.recvfrom(4096)
tamanho_arquivo = int(tamanho_arquivo.decode())  # Converte para inteiro

# Exibindo o tamanho do arquivo
print(f"O tamanho do arquivo solicitado é {tamanho_arquivo} bytes.")

#Verificando se o arquivo existe no servidor
if tamanho_arquivo > 0:
    #Preparando para salvar o arquivo recebido
    arquivo_local = open(nome_arquivo, 'wb')

    #Contagem de bytes recebidos
    bytes_recebidos = 0

    #Recebendo o arquivo em pedaços
    while bytes_recebidos < tamanho_arquivo:
        dados, _ = cliente.recvfrom(4096)
        arquivo_local.write(dados)
        bytes_recebidos += len(dados)

    #Fechando o arquivo local depois de receber tudo
    arquivo_local.close()
    print(f"Arquivo {nome_arquivo} recebido com sucesso!")

else:
    print(f"O arquivo {nome_arquivo} não foi encontrado no servidor.")


cliente.close()
