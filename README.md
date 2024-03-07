# online-voting-system-
This is an online voting system developed using socket programming.
This project uses concepts of socket programming using TCP, Secure Socket Layer(SSL), multithreading and image processing.

The image of the client is clicked through the client webcam, I have used the module 'opencv' in python to accomplish the same. The model captures the image, checks the number of people in the image and if it detects more than one user, it does not let the client vote. The image is sent to the server using TCP.

The votes and the login credentials of all users is sent to the server via TCP.

The concept of SSL has been implemented to ensure user security and try to minimise attacks on the network.

'server.py' -> server code
'app.py' -> client side code
'vid.py' -> handles the image processing 
