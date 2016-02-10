import cb2_integrated

HOST = "192.168.1.100"    # The remote host
PORT = 30003              # The same port as used by the server

robot = cb2_integrated.URRobot(HOST, PORT)

angleStart = [90, -95, 90, 0, 90, 90]
angleStart = map(cb2_integrated.cb2_send.deg_2_rad, angleStart)
center = [100.0/1000, -475.0/1000, 425.0/1000, 1.2, -1.2, 1.2]

robot.add_goal(cb2_integrated.Goal(angleStart, False, 'joint'))

thisMove = list(center)
thisMove[0] = center[0] - .1
thisMove[2] = center[2] - .1
robot.add_goal(cb2_integrated.Goal(thisMove, True, 'linear'))

thisMove = list(center)
thisMove[0] = center[0] + .1
thisMove[2] = center[2] + .1
robot.add_goal(cb2_integrated.Goal(thisMove, True, 'linear'))

robot.move_now()
while not robot.goals.empty():
    robot.move_on_stop()

robot.__del__()
