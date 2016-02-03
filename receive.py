import socket


HOST = "192.168.1.100"    # The remote host
PORT = 30002              # The same port as used by the server


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))

while True:
    data = s.recv(1024)
    print "Received (raw): "+data+"\n"
    print "Received (repr): "+repr(data)+"\n\n"

s.close()
