import cb2_send
import time
HOST = "192.168.1.100"    # The remote host
PORT = 30003              # The same port as used by the server

robot = cb2_send.URSender(HOST, PORT, True)

angleStart = [90, -95, 90, 0, 90, 90]
angleStart = map(cb2_send.deg_2_rad, angleStart)

robot.move_joint(angleStart)

time.sleep(1)
