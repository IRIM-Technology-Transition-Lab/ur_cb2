# Echo client program
import socket
import time
import math

def Deg2Rad(x):
    return 3.14 * x / 180

def Rad2Deg(x):
    return (x / 3.14) * 180

def drange(start, stop, step):
    r = start
    while r < stop:
        yield r
        r += step

# def moveTo(pose,vel,accel,update):
#     command = "movej(p"+str(thisMove)+", a=1.3962634015954636, v=1.0471975511965976)" + "\n"
#     print command
#     s.send (command)


HOST = "192.168.1.100"    # The remote host
PORT = 30002              # The same port as used by the server
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))
s.send ("set_analog_inputrange(0, 0)" + "\n")
data = s.recv(1024)
s.close()
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))
s.send ("set_analog_inputrange(1, 0)" + "\n")
data = s.recv(1024)
s.close()
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))
s.send ("set_analog_outputdomain(0, 0)" + "\n")
data = s.recv(1024)
s.close()
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))
s.send ("set_analog_outputdomain(1, 0)" + "\n")
data = s.recv(1024)
s.close()
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))
s.send ("set_tool_voltage(24)" + "\n")
data = s.recv(1024)
s.close()
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))
s.send ("set_runstate_outputs([])" + "\n")
data = s.recv(1024)
s.close()
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))
s.send ("set_payload(0.0)" + "\n")
data = s.recv(1024)
s.close()
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))
s.send ("set_gravity([0.0, 0.0, 9.82])" + "\n")
data = s.recv(1024)
s.close()
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))

center = [100.0/1000,-475.0/1000,425.0/1000,1.2,-1.2,1.2]
angleStart = [90,-95,90,0,90,90]
angleStart = map(Deg2Rad,angleStart)
radius = 100.0/1000

s.send ("movej("+str(angleStart)+", a=1.3962634015954636, v=1.0471975511965976)" + "\n")
time.sleep(3)

# time.sleep(2)
# thisMove = list(center)
# thisMove[0] = center[0]+(math.cos(0)*radius)
# thisMove[2] = center[2]+(math.sin(0)*radius)
# command = "movep(p"+str(thisMove)+", a=1.3962634015954636, v=1.0471975511965976)" + "\n"
# print command
# s.send (command)
# time.sleep(1)

# for theta in drange(0,2*math.pi,.01):
#     thisMove = list(center)
#     thisMove[0] = center[0]+(math.cos(theta)*radius)
#     thisMove[2] = center[2]+(math.sin(theta)*radius)
#     command = "movep(p"+str(thisMove)+", a=1.3962634015954636, v=1.0471975511965976)" + "\n"
#     print command
#     s.send (command)
#     # time.sleep(0.001)
for delayTime in drange(0,2,.25):
    thisMove = list(center)
    thisMove[0] = center[0] - .1
    thisMove[2] = center[2] - .1
    command = "movep(p"+str(thisMove)+", a=1.3, v=.3, r=.01)" + "\n"
    print command
    s.send (command)

    time.sleep(2)

    thisMove = list(center)
    thisMove[0] = center[0] + .1
    thisMove[2] = center[2] - .1
    command = "movep(p"+str(thisMove)+", a=.2, v=.1, r=.01)" + "\n"
    print command
    s.send (command)

    time.sleep(delayTime)

    thisMove = list(center)
    thisMove[0] = center[0] + .1
    thisMove[2] = center[2] + .1
    command = "movep(p"+str(thisMove)+", a=.2, v=.1, r=.01)" + "\n"
    print command
    s.send (command)

    time.sleep(3)

# data = ""
# for i in range(1,5):
#     s.send("get_actual_tcp_pose()\n")
#     data = data + (s.recv(1024))
#     print "Pose: "+ data+"\n"



time.sleep(3)

# data = s.recv(1024)
s.close()
print ("Received", repr(data))
