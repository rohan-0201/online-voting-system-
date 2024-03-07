from flask import *
import cv2
import socket
import pickle
import ssl

class CamDisabled(Exception):
    pass
class ImageErr(Exception):
    pass


Host= "127.0.0.1" 
crtpath=r"/Users/rohan/Documents/Programming/CN/server.crt"
imgpath=r"/Users/rohan/Documents/Programming/CN/captured_image.jpg"

app = Flask(__name__)

@app.route('/' , methods=['GET','POST'])
def hello_world():
    if request.method=='GET':
        return render_template('login.html')
    elif request.method=='POST':
        try:
            v_name= request.form['Vname']
            v_id= request.form['id_value']
        except:return render_template("error.html",Err="Couldnt get values , try again")
        try:
                lst= get_val(v_name,v_id)
                if type(lst)==type([]):
                    return render_template("vote.html",lst=lst,consti=lst[2])
                elif type(lst.decode())==type(""): return render_template("voted.html",vot="You have already voted")
        except CamDisabled:return render_template("error.html",Err="Couldnt open camera, try again")
        except ImageErr:return render_template("error.html",Err="No person or multiple people detected , try again")
        except ConnectionError:return render_template("error.html",Err="Couldnt connect to server, try again")
        except :return render_template("error.html",Err="Invalid Inputs, try again ")

@app.route('/voted',methods=['GET','POST'])
def voted():
    votes=request.form['vote']
    consti=request.form['consti']
    vote(votes)
    return render_template('voted.html',vot="You Have Successfully Voted "+ votes)

def get_val(vn,vid):
    global vot_vid 
    vot_vid= cv2.VideoCapture(0)

    if not vot_vid.isOpened():
        raise CamDisabled
    else:
        capture_and_send() 
    return start_client(pickle.dumps([vn,vid]))
    
def start_client(message):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)       # Create a socket object

    # Connect to the server
    port = 12345
    try:client_socket.connect((Host, port))
    except: raise ConnectionError

    client_ssl = ssl.wrap_socket(client_socket,ca_certs=crtpath)#add server ssl certificate in ca_certs
    try:
        client_ssl.send(message)
        print(f"Sent to server: {message}")

        echoed_message = client_ssl.recv(1024)           # Receive and print the echoed message from the server
        echoed_message = pickle.loads(echoed_message)
        # print(f"Received from server: {echoed_message}")
        client_ssl.close()               # Close the client socket
        return echoed_message
    except: raise()
    finally: client_ssl.close()


def vote(vote):
    print(start_client(vote.encode()).decode())

def capture_and_send():
    ret, frame = vot_vid.read()
    if ret:
        inverted_frame = cv2.flip(frame, 1)
        cv2.imwrite(imgpath, inverted_frame)
        print("Image captured!")

        # Encode the image as bytes
        with open(imgpath, 'rb') as file:
            image_bytes = file.read()

        # Create a socket connection to the server
        try:
            client_socket =socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((Host, 12346))  # Replace 'server_ip_address' with the server's IP address
        except: raise ConnectionError    
            # Send the image size first
        client_ssl = ssl.wrap_socket(client_socket,ca_certs=crtpath)#add server ssl certificate in ca_certs
        client_ssl.sendall(len(image_bytes).to_bytes(4, byteorder='big'))
        
        # Send the image data
        client_ssl.sendall(image_bytes)
        print("Image sent successfully!")
    
        data=client_ssl.recv(1024)
        if data.decode()=='Error':
            vot_vid.release() 
            cv2.destroyAllWindows()
            raise ImageErr

        
    vot_vid.release() 
    cv2.destroyAllWindows()


if __name__=='__main__':
    app.debug=True
    app.run()