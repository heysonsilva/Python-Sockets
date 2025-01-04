import socket

# Cliente

DIRBASE = "files/"
SERVER = '127.0.0.1'
PORT = 12345
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

while True:
    # Solicitando o arquivo ao usuário
    fileName = input("Digite o nome do arquivo a ser solicitado: ")

    # Enviando solicitação ao servidor
    print(f"Solicitando o arquivo {fileName} ao servidor {SERVER}:{PORT}")
    sock.sendto(fileName.encode('utf-8'), (SERVER, PORT))

    #-------------------------------------------------------
    # Recebendo o tamanho do arquivo
    tamanho_arquivo_bytes, source = sock.recvfrom(4096)
    tamanho_arquivo = int(tamanho_arquivo_bytes.decode())

    if tamanho_arquivo == 0:
        print(f"Arquivo {fileName} não encontrado no servidor.")
        continue

    print(f"Tamanho do arquivo {fileName} recebido: {tamanho_arquivo} bytes.")
    #-------------------------------------------------------

    # Gravando o arquivo localmente
    print(f"Gravando o arquivo {fileName}...")
    fd = open(DIRBASE + fileName, 'wb')

    bytes_recebidos = 0
    while bytes_recebidos < tamanho_arquivo:
        data, source = sock.recvfrom(4096)
        fd.write(data)
        bytes_recebidos += len(data)
        print(f"Recebidos {bytes_recebidos}/{tamanho_arquivo} bytes...")

    fd.close()
    print(f"Arquivo {fileName} recebido e salvo com sucesso!\n")

sock.close()
