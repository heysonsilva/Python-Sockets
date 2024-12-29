import socket

DIRBASE = "files/"
SERVER = '127.0.0.1'
PORT   = 12345
sock = socket.socket (socket.AF_INET, socket.SOCK_DGRAM)
sock.settimeout(2)

while True:
    # Lê do usuário o nome do arquivo a pedir ao servidor
    fileName = input("Arquivo a pedir ao servidor: ")

    # Envia ao servidor do nome do arquivo desejado pelo usuário
    print ("Enviando pedido a", (SERVER, PORT), "para", fileName)
    sock.sendto (fileName.encode('utf-8'), (SERVER, PORT))

    # Grava o arquivo localmente
    print ("\nGravando arquivo localmente")
    fd = open (DIRBASE+fileName, 'wb')

    # Recebe o conteúdo do arquivo vindo do servidor
    while True:
        try:
            data, source = sock.recvfrom (4096)
            fd.write (data)
        except:
            print ("Saiu com timeout ...")
            break

    fd.close()

sock.close()