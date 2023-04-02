import sys , socket , select # pour la communication Client/Serveur
from fastecdsa import keys, curve ,point # Pour les paramètres de la courbe elliptique et les opération sur cette courbe
import pickle # pour garder les informations des objets envoyé par sockets
from Crypto.Cipher import AES
from Crypto import Random
from Crypto.Util.number import long_to_bytes , bytes_to_long
import base64



# definir les deux fonctions pad et unpad pour le rembourrage
BS = 32
pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS)
unpad = lambda s : s[:-ord(s[len(s)-1:])]


# la fonction encrypt en utilisant le clé commun et lemode CBC de AES
def encrypt( key, raw ):
        raw = pad(raw)
        iv = Random.new().read( AES.block_size )
        cipher = AES.new( key, AES.MODE_CBC, iv )
        return base64.b64encode( iv + cipher.encrypt( raw.encode() ) ) # encoder le résultat (bytes) sur la base 64

# la fonction decrypt en utilisant le clé commun et lemode CBC de AES
def decrypt( key, enc ):
        enc = base64.b64decode(enc)
        iv = enc[:16]
        cipher = AES.new(key, AES.MODE_CBC, iv )
        return unpad(cipher.decrypt( enc[16:] ))# deoceder le résultat (bytes) de la base 64






#generator de notre courbe curve.P256
G = point.Point(curve.P256.gx, curve.P256.gy, curve=curve.P256) 
# generer un nembre aleatoire
r = keys.gen_private_key(curve.P256)
R=r*G # le multiplier par le generator 




HOST = "127.0.0.1"  
# HOST = socket.gethostbyname(socket.gethostname())
PORT = 5000  



with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    try:
        s.connect((HOST, PORT))
    except:
        print("Erreur de connection.")
        exit()
    try:
        # Reception du clé public de l'appart de l'autre client
        pbk=b""
        pbk+=s.recv(2048)
        pbk=pickle.loads(pbk)
        s.sendall(pickle.dumps(R))
        #S = r*pbk 
        #  = r*Q
        #  = r*prk*G
        S=r*pbk
        print("############################################" , end='\n\n')
        print("L'échange de clé s'est effectué avec succeés ...")
        print("############################################", end='\n\n')
        print("le point en commun est: ")
        print(f"{S=}" , end='\n\n')
        print("############################################", end='\n\n')
    except:
        print("Erreur dans l'echange de clés")
        exit()





    # on prend l'abscisse comme clé de AES
    AES_KEY=S.x
    sockets_list = [sys.stdin, s]

    print("############################################" , end='\n\n')
    print("Commenceant l'échange securisé de messaages", end='\n\n')
    print("############################################", end='\n\n')
    while True:
        read_sockets, _, _ = select.select(sockets_list, [], [])
        
        for sock in read_sockets:

            if sock == s:
                data=b""
                data+=s.recv(2048)
                data=pickle.loads(data)
                data=decrypt(long_to_bytes(AES_KEY) , data.decode())# Réception + décryptions
                if data.decode().lower()=="quit":
                    print("Bslama")
                    s.close()
                    exit()
                print("<<:  "+ data.decode())
            else:
                msg = sys.stdin.readline()
                enc_msg=encrypt(long_to_bytes(AES_KEY) , msg)# encryptage de message à envoyé
                enc_msg_pickled=pickle.dumps(enc_msg)
                s.sendall(enc_msg_pickled)
                if msg.lower() == "quit":
                    s.close()
                    exit()
                sys.stdout.flush()
