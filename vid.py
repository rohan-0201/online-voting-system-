import socket
import cv2
import threading 

import ssl

i=0
host ="127.0.0.1" # socket.gethostbyname(socket.gethostname())
certfile=r"/Users/rohan/Documents/Programming/CN/server.crt"
keyfile= r"/Users/rohan/Documents/Programming/CN/server.key"

def handle_client(client_socket,client_address):

    print(f"Connection from {client_address} established.")
    try: 
        while True:
            # Receive the image size
            sslContext=ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            sslContext.load_cert_chain(certfile=certfile,keyfile=keyfile)
            server_ssl = sslContext.wrap_socket(client_socket,server_side = True)
            while server_ssl:
                image_size_bytes = server_ssl.recv(4)
                image_size = int.from_bytes(image_size_bytes, byteorder='big')

                # Receive the image data
                image_data = b''
                while len(image_data) < image_size:
                    packet = server_ssl.recv(image_size - len(image_data))
                    if not packet:
                        break
                    image_data += packet

                # Decode the image data
                path="received_image"+str(i)+".jpg"
                with open(path, 'wb') as file:
                    file.write(image_data)
                print("Image received and saved.")
                gray_frame = cv2.cvtColor(cv2.imread(path), cv2.COLOR_BGR2GRAY)
                
                # Load the pre-trained face cascade classifier
                face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
                
                # Detect faces in the grayscale image
                faces = face_cascade.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=2, minSize=(30, 30))
                
                if len(faces) > 1:
                    print("Multiple people detected in the image!")
                    server_ssl.send("Error".encode())
                    #raise()
                elif len(faces)==0:
                    print("No person detected in the image!")
                    server_ssl.send("Error".encode())
                    #raise()
                else:
                    print("Single person detected in the image.")
                server_ssl.close()
    except OSError: pass
        



def receive_image():
    img_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)       # Create a socket object

    # Bind the socket to a specific address and port
    port = 12346
    img_socket.bind((host, port))
    img_socket.listen(5)       
    print("Waiting for connections...")

    while True:
        client_socket, client_address = img_socket.accept()
        global i
        i+=1
        thread = threading.Thread(target=handle_client, args= (client_socket,client_address))
        thread.start()
    img_socket.close()
    

if __name__ == '__main__':
    receive_image()