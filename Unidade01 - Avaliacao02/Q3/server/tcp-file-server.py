import socket

# Definindo o IP e a porta que o servidor vai escutar
ip_server = "0.0.0.0"
port_server = 12345

# Neste trecho está sendo definido o protocolo de transporte (tcp) e o protocolo de rede (ipv4) do servidor
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Ligando o servidor e atribuindo ip e porta que foram definidos nas variaveis "ip_server" e "port_server"
server.bind((ip_server, port_server))

# Servidor está "Escutando"
server.listen()

print(f"Servidor esperando por conexões em {ip_server}:{port_server}")

try:
    while True:
        # Aceita conexões
        cliente, endereco = server.accept()  
        
        print(f"Conexão estabelecida com: {endereco}")
        
        # Envia mensagem
        cliente.sendall(b"Bem-vindo ao servidor!")

    # Recebe dados do cliente
        while True:
            # Recebe dados do cliente
            dados = cliente.recv(1024)

            # Se não houver dados, encerra a conexão
            if not dados:
                print("Não há dados a ser recebido 😴")
                break 
        
            elif dados:    
                # Exibe mensagem recebida
                print(f"Recebido do clientee: {dados.decode('utf-8')}")  
        
        # Fecha a conexão com o cliente
        cliente.close() 
        
except ConnectionResetError:
    print("="*30 + "\n ⚠ CLIENTE ENCERROU A CONEXÃO ⚠\n" + "="*30)
