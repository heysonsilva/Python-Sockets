import socket

DIRBASE = "files/"
INTERFACE = '127.0.0.1'
PORT = 12345
sock = socket.socket (socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((INTERFACE, PORT))

print ("Escutando em ...", (INTERFACE, PORT))
while True:
    # Recebe o nome do arquivo a servir
    data, source = sock.recvfrom (512)

    # Abre o arquivo a servir ao cliente
    fileName = data.decode('utf-8')

    print ("Recebi pedido para o arquivo ", fileName)
    fd = open (DIRBASE+fileName, 'rb')

    # Lê o conteúdo do arquivo a enviar ao cliente
    print ("Enviando arquivo ", fileName)
    fileData = fd.read(4096)
    while fileData != b'':
        sock.sendto(fileData, source)
        fileData = fd.read(4096)

    # Fecha o arquivo
    fd.close()
sock.close()