import socket

# Configurações do cliente
host = '127.0.0.1'
porta = 12345

# Criação do socket do cliente
cliente_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Conecta ao servidor
cliente_socket.connect((host, porta))

while True:
    # Envia dados ao servidor
    mensagem = "Olá, servidor!"
    cliente_socket.sendall(mensagem.encode('utf-8'))
    # Encerra a conexão
    cliente_socket.close()


