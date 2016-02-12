import cb2_robot
import cb2_send
import math
import time

HOST = "192.168.1.100"    # The remote host
PORT = 30003              # The same port as used by the server

try:
    robot = cb2_robot.URRobot(HOST, PORT)

    angleStart = [90, -95, 90, 0, 90, 90]
    angleStart = map(cb2_robot.cb2_send.deg_2_rad, angleStart)
    center = [100.0/1000, -475.0/1000, 425.0/1000, 1.2, -1.2, 1.2]

    robot.add_goal(cb2_robot.Goal(angleStart, False, 'joint'))

    thisMove = list(center)
    thisMove[0] = center[0] - .2
    thisMove[2] = center[2] - .1
    robot.add_goal(cb2_robot.Goal(thisMove, True, 'linear'))

    thisMove = list(center)
    thisMove[0] = center[0] + .1
    thisMove[2] = center[2] + .1
    robot.add_goal(cb2_robot.Goal(thisMove, True, 'linear'))

    # robot.move_now()
    while not robot.goals.empty():
        robot.move_on_stop()
    print 'complete loop 1'

    # while not (robot.is_stopped() and robot.at_goal()):
    #     time.sleep(.01)
    #
    # # for robot.error in (.001, .005, .1, .25, .5):
    # #     for theta in cb2_send.double_range(0, 2*math.pi, 2*math.pi/200):
    # #         thisMove = list(center)
    # #         thisMove[0] = center[0] + (.1 * math.cos(theta))
    # #         thisMove[2] = center[2] + (.1 * math.sin(theta))
    # #         robot.add_goal(cb2_robot.Goal(thisMove, True, 'linear'))
    # #
    # #     while not robot.goals.empty():
    # #         robot.move_on_error()
    # #     print 'complete loop 2 with error: {}'.format(robot.error)
    #
    # for theta in cb2_send.double_range(0, 2*math.pi, 2*math.pi/20):
    #     thisMove = list(center)
    #     thisMove[0] = center[0] + (.1 * math.cos(theta))
    #     thisMove[2] = center[2] + (.1 * math.sin(theta))
    #     robot.add_goal(cb2_robot.Goal(thisMove, True, 'process'))
    #
    # robot.error = .008
    # while not robot.goals.empty():
    #     robot.move_on_error(2)
    # print 'complete loop 3'.format(robot.error)
finally:
    robot.__del__()
    pass
