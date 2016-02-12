"""Test the buffering nature of a UR 5.

This script is designed to test the buffering nature of a UR 5, the result
is that the UR5 does not buffer motions, but the communication protocol can
get overrun. Therefore it is critical to not send more than 125 commands
per second

Copyright (c) 2016 GTRC. All rights reserved.
"""


import socket
import time


def deg_2_rad(x):
    return 3.14 * x / 180


def rad_2_deg(x):
    return (x / 3.14) * 180


def double_range(start, stop, step):
    r = start
    while r < stop:
        yield r
        r += step

HOST = "192.168.1.100"    # The remote host
PORT = 30003              # The same port as used by the server

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))
s.send("set_payload(0.0)" + "\n")
s.close()
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))
s.send("set_gravity([0.0, 0.0, 9.82])" + "\n")
s.close()
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))

center = [100.0/1000, -475.0/1000, 425.0/1000, 1.2, -1.2, 1.2]
angleStart = [90, -95, 90, 0, 90, 90]
angleStart = map(deg_2_rad, angleStart)
blend = .005

s.send(
    "movej("+str(angleStart)+", a=1.3962634015954636, v=1.0471975511965976)" +
    "\n")
time.sleep(3)

for delayTime in double_range(0, 2, .25):
    thisMove = list(center)
    thisMove[0] = center[0] - .1
    thisMove[2] = center[2] - .1
    command = "movep(p"+str(thisMove)+", a=1.3, v=.3, r="+str(blend)+")" + "\n"
    print command
    s.send(command)

    time.sleep(2)

    thisMove = list(center)
    thisMove[0] = center[0] + .1
    thisMove[2] = center[2] - .1
    command = "movep(p"+str(thisMove)+", a=.2, v=.1, r="+str(blend)+")" + "\n"
    print command
    s.send(command)

    time.sleep(delayTime)

    thisMove = list(center)
    thisMove[0] = center[0] + .1
    thisMove[2] = center[2] + .1
    command = "movep(p"+str(thisMove)+", a=.2, v=.1, r="+str(blend)+")" + "\n"
    print command
    s.send(command)

    time.sleep(3)

for delayTime in double_range(0, 2, .25):
    thisMove = list(center)
    thisMove[0] = center[0] - .1
    thisMove[2] = center[2] - .1
    command = "movel(p"+str(thisMove)+", a=1.3, v=.3, r="+str(blend)+")" + "\n"
    print command
    s.send(command)

    time.sleep(2)

    thisMove = list(center)
    thisMove[0] = center[0] + .1
    thisMove[2] = center[2] - .1
    command = "movel(p"+str(thisMove)+", a=.2, v=.1, r="+str(blend)+")" + "\n"
    print command
    s.send(command)

    time.sleep(delayTime)

    thisMove = list(center)
    thisMove[0] = center[0] + .1
    thisMove[2] = center[2] + .1
    command = "movel(p"+str(thisMove)+", a=.2, v=.1, r="+str(blend)+")" + "\n"
    print command
    s.send(command)

    time.sleep(3)

for delayTime in double_range(0, 1.5, .25):
    thisMove = list(center)
    thisMove[0] = center[0] - .1
    thisMove[2] = center[2] - .1
    command = "movel(p"+str(thisMove)+", a=1.3, v=.3, r="+str(blend)+")" + "\n"
    print command
    s.send(command)

    time.sleep(2)

    thisMove = list(center)
    thisMove[0] = center[0] + .1
    thisMove[2] = center[2] - .1
    command = "movel(p"+str(thisMove)+", a=.2, v=.1, r="+str(blend)+")" + "\n"
    print command
    s.send(command)

    time.sleep(delayTime)

    command = "stopl(a=.2)" + "\n"
    print command
    s.send(command)

    time.sleep(3)

s.close()
