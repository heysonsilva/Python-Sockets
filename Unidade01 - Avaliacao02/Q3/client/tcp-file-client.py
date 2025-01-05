import socket

ip = '127.0.0.1'
porta = 12345

# Criação do socket do cliente
cliente_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Conecta ao servidor
cliente_socket.connect((ip, porta))


try:
    while True:
        # Envia dados ao servidor
        mensagem = input(">> ")
        cliente_socket.sendall(mensagem.encode('utf-8'))
        
        dados = cliente_socket.recv(1024)
        
        
    
    cliente_socket.close()

except KeyboardInterrupt:
    print("="*30 + "\n ⚠ CONEXÃO ENCERRADA ⚠\n" + "="*30)  



