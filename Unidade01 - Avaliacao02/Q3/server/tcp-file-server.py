import socket 

# Definindo o IP e a porta que o servidor vai escutar
ip_server = '0.0.0.0'
port_server = 12345

# Neste trecho está sendo definido o protocolo de transporte (tcp) e o tipo de ip (ipv4) do servidor
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Atribuindo o socket ao IP e à porta
server.bind((ip_server, port_server))

# Servidor está "Escutando"
server.listen(5)

print(f"Servidor esperando por conexões em {ip_server}:{12048}")


while True:
    client, endereco = server.accept() # Aceita conexões
    print(f"Conexão estabelecida com: {endereco}")
    client.sendall(b"Bem-vindo ao servidor!") # Envia mensagem
    client.close() # Fechar Conexão                      
    



