import socket
import pickle
import threading 
import ssl

host = "127.0.0.1"
certfile=r"/Users/rohan/Documents/Programming/CN/server.crt"
keyfile= r"/Users/rohan/Documents/Programming/CN/server.key"
votercsv=r"/Users/rohan/Documents/Programming/CN/voter.csv"
candidatecsv=r"/Users/rohan/Documents/Programming/CN/candidate.csv"

voted=[] 

def handle_client(client_socket,client_address):
    print(f"Connection established with {client_address}")
    connected=True
    try:
        while connected:
            sslContext=ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            sslContext.load_cert_chain(certfile=certfile,keyfile=keyfile)
            server_ssl = sslContext.wrap_socket(client_socket,server_side = True)
            while server_ssl:
                data = server_ssl.recv(1024)         # Receive and echo back data
                if not data:
                    break

                try: data = pickle.loads(data)
                except:data = data.decode() 
                print(f"Received from client: {data}")

                if type(data)==type([]):
                    global id
                    id=data[1]
                    lst=get_val(data[0],data[1])
                    server_ssl.send(pickle.dumps(lst))
                else: 
                    server_ssl.send(pickle.dumps("received".encode()))
                    global voted
                    voted.append(id)
                server_ssl.close()

    except OSError: pass



def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)       # Create a socket object

    # Bind the socket to a specific address and port
    #socket.gethostbyname(socket.gethostname())  # localhost
    port = 12345
    server_socket.bind((host, port))

    server_socket.listen(5)         # Listen for incoming connections

    print(f"Server listening on {host}:{port}")

    while True:
        client_socket, client_address = server_socket.accept()
        thread = threading.Thread(target=handle_client, args= (client_socket,client_address))
        thread.start()
        
                      # Accept a connection from a client
    server_socket.close()

def get_val(vn,vid):
    fv= open(votercsv,'r')
    x = fv.readlines()
    fv.close()
    lst=[]
    try:
        if(x[int(vid)].split(',')[1]==vn):
            consti=x[int(vid)].split(',')[2]
            fc=open(candidatecsv,'r')
            x=fc.readlines()
            for i in x:
                temp=i.split(',')
                if temp[2].strip()==consti.strip():
                    lst.append(temp)
            if len(lst)==0:return
        else: return
    except:return
    if vid in voted:
        return "Voted".encode()
    return lst


if __name__ == "__main__":
    start_server()
