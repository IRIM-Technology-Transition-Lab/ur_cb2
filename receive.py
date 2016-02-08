import socket
import struct
import binascii
import array

class URreceiver:
    """A class to receive data from a UR Robot"""
    # Format spcifier:
    # ! : network (big endian)
    # I : unsigned int, message size
    # 101d : 101 doubles
    format = struct.Struct('! I 101d ')
    formatLength = struct.Struct('! I')
    def __init__(self,ip,port):
        self.ip = ip
        self.port = port
        self.cleanData = array.array('d',[0]*101)
        self.rawData = ''
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.ip, self.port))
        self.cleanPackets = 0
        self.stubPackets = 0
        self.received = 0
        self.waitingData =[]
        self.newData = False

    def __del__(self):
        print "closing ports"
        self.socket.close()
        print "Received: "+str(self.received)+" packets"
        print "Received: "+str(self.cleanPackets)+" clean packets"
        print "Received: "+str(self.stubPackets)+" stub packets"

    def decode(self):
        if self.newData:
            self.cleanData = self.format.unpack(self.rawData)
            self.newData = False

    def receive(self):
        incomingData = self.socket.recv(812) #expect to get 812 bytes
        binaryData = binascii.hexlify(incomingData)
        packetLengthData = binaryData
        if len(incomingData) == 812:
            self.cleanPackets += 1
        if self.formatLength.unpack(incomingData[0:4])[0] == 812 :
            self.waitingData = incomingData
        else:
            self.waitingData += incomingData
            self.stubPackets += 1

        if len(self.waitingData) == 812:
            self.rawData = self.waitingData
            self.received += 1
            self.newData = True

    def printRawData(self):
        print "Received (raw): "+self.rawData+"\n"

    def printData(self):
        print "Received (unpacked):\n "
        print self.cleanData
        print "\n"


HOST = "192.168.1.100"    # The remote host
PORT = 30003              # The same port as used by the server

myURReceiver = URreceiver(HOST,PORT)

while True:
    myURReceiver.receive()
    myURReceiver.decode()
    # myURReceiver.printData()

s.close()
