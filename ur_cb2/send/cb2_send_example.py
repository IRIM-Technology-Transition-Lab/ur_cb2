"""This basic script demonstrates usage of the cb2_send module.

Copyright (c) 2016 GTRC. All rights reserved.
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
