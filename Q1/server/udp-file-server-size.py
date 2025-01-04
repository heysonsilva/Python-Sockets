import os
import socket

# Servidor

DIRBASE = "files/"
INTERFACE = '127.0.0.1'
PORT = 12345
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((INTERFACE, PORT))

print("Servidor iniciado. Escutando em ...", (INTERFACE, PORT))
while True:
    # Recebe o nome do arquivo a servir
    data, source = sock.recvfrom(512)
    fileName = data.decode('utf-8')

    print(f"Recebi pedido do cliente {source} para o arquivo: {fileName}")

    try:
        # Abrindo o arquivo solicitado
        fd = open(DIRBASE + fileName, 'rb')
        
        #-------------------------------------------------------
        # Obtendo o tamanho do arquivo
        tamanho_arquivo = os.path.getsize(DIRBASE + fileName)
        print(f"Tamanho do arquivo {fileName}: {tamanho_arquivo} bytes")

        # Enviando o tamanho do arquivo ao cliente
        sock.sendto(str(tamanho_arquivo).encode(), source)
        print(f"Tamanho do arquivo {tamanho_arquivo} enviado para o cliente {source}")
        #-------------------------------------------------------

        # Enviando o conteúdo do arquivo
        print(f"Iniciando envio do arquivo {fileName}...")
        fileData = fd.read(4096)
        while fileData != b'':
            sock.sendto(fileData, source)
            fileData = fd.read(4096)

        print(f"Arquivo {fileName} enviado com sucesso para o cliente {source}")
        fd.close()

    except FileNotFoundError:
        #-------------------------------------------------------
        # Enviando mensagem de erro
        print(f"Arquivo {fileName} não encontrado.")
        sock.sendto(b'0', source)
        #-------------------------------------------------------
sock.close()
