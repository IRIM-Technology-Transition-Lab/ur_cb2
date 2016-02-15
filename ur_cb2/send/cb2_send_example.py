"""This basic script demonstrates usage of the cb2_send module.

The MIT License (MIT)

Copyright (c) 2016 GTRC.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import socket
import time

import cb2_send

HOST = "192.168.1.100"    # The remote host
PORT = 30003              # The same port as used by the server
robot_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
robot_socket.connect((HOST, PORT))

robot = cb2_send.URSender(robot_socket, True)

angle_start = [90, -95, 90, 0, 90, 90]
angle_start = map(cb2_send.deg_2_rad, angle_start)

robot.move_joint(angle_start)
time.sleep(2.5)  # Need to wait for move to complete

angle_finish = [70, -65, 90, 0, 90, 90]
angle_finish = map(cb2_send.deg_2_rad, angle_finish)

robot.move_joint(angle_finish)
