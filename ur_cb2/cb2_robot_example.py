"""A simple script demonstrating the basic usage of the cb2_robot class

Copyright (c) 2016 GTRC. All rights reserved.
"""

import cb2_robot
import time
import random

HOST = "192.168.1.100"    # The remote host
PORT = 30003              # The same port as used by the server

with cb2_robot.URRobot(HOST, PORT) as robot:
    angleStart = [90, -95, 90, 0, 90, 90]
    angleStart = map(cb2_robot.cb2_send.deg_2_rad, angleStart)
    center = [100.0/1000, -475.0/1000, 425.0/1000, 1.2, -1.2, 1.2]

    robot.add_goal(cb2_robot.Goal(angleStart, False, 'joint'))

    thisMove = list(center)
    thisMove[0] = center[0] - .2
    thisMove[2] = center[2] - .2
    robot.add_goal(cb2_robot.Goal(thisMove, True, 'linear'))

    thisMove = list(center)
    thisMove[0] = center[0] + .2
    thisMove[2] = center[2] - .2
    robot.add_goal(cb2_robot.Goal(thisMove, True, 'linear'))

    thisMove = list(center)
    thisMove[0] = center[0] + .2
    thisMove[2] = center[2] + .2
    robot.add_goal(cb2_robot.Goal(thisMove, True, 'linear'))

    thisMove = list(center)
    thisMove[0] = center[0] - .2
    thisMove[2] = center[2] + .2
    robot.add_goal(cb2_robot.Goal(thisMove, True, 'linear'))

    # robot.move_now()
    while not robot.goals.empty():
        robot.move_on_stop()
    print 'complete loop 1'

    while not (robot.is_stopped() and robot.at_goal()):
        time.sleep(.01)

    for i in range(0, 15):
        thisMove = list(center)
        thisMove[0] = center[0] + random.uniform(-.2, .2)
        thisMove[2] = center[2] + random.uniform(-.2, .2)
        robot.add_goal(cb2_robot.Goal(thisMove, True, 'linear'))

    while not robot.goals.empty():
        robot.move_on_stop()
    print 'complete loop 2'
