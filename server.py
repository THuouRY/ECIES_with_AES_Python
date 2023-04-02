import pickle
import socket
import select

# Creer un objet socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# cet ligne permet la réutilisation de la meme addresse 
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# Adresse
host = "127.0.0.1"
# host = socket.gethostbyname(socket.gethostname())
port = 5000

# bind 
server_socket.bind((host, port))

# on limite le nombre de clients possibles à deux
server_socket.listen(2)

print('Attendant que les deux clients se connectent....')
print("Addrese {}:{}".format(host , port))

client_socket1, client_address1 = server_socket.accept()
print("Le premier client s'est connecté:", client_address1)

client_socket2, client_address2 = server_socket.accept()
print("Le deuxieme client s'est connecté:", client_address2)

# list de sockets connectées
sockets_list = [server_socket, client_socket1, client_socket2]

print('Commenceant le chat...' ,end ='\n\n')

while True:
    # Attendre que le socket contient quelque chose
    read_sockets, _, _ = select.select(sockets_list, [], [])
    
    for sock in read_sockets:
        # si c'est une nouvelle connexion
        if sock == server_socket:
            client_socket, client_address = server_socket.accept()
            sockets_list.append(client_socket)
            print('Biig Problem', client_address)
            exit()

        # sinon c'est le stdin (clavier)
        else:
            tmp=b''
            message = sock.recv(1024)
            tmp+=message
            if message:
                print('Received:')
                print(pickle.loads(tmp) , end='\n\n')
                # broadcast the message 
                for client_sock in sockets_list:
                    if client_sock != server_socket and client_sock != sock:
                        client_sock.send(message)
            # closed connections
            else:
                sockets_list.remove(sock)
                print('Client disconnected')

