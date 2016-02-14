"""A basic script to move to stored points for a cb2 robot.

Basic Usage: Store points using cb2_store_points.py (cb2-record from the
terminal). Run this script, with commandline args.

Copyright (c) 2016 GTRC. All rights reserved.
"""

import argparse
import cb2_robot
import json
import time


def main():
    # Parse in arguments
    parser = argparse.ArgumentParser(
        description='Save Points',
        epilog="This software is designed to move a cb2 robot to points which "
               "have been previously saved.")

    parser.add_argument("-f", "--file", metavar="file", type=str,
                        help='The file to read data from.',
                        default="cb2points.json")

    parser.add_argument("--ip", metavar="ip", type=str,
                        help='IP address of the robot', default="192.168.1.100")

    parser.add_argument("--port", metavar="port", type=int,
                        help='IP port on the robot', default=30003)

    args = parser.parse_args()
    host = args.ip    # The remote host
    port = args.port  # The same port as used by the server

    with open(args.file, 'r') as f:
        data = json.load(f)
    write_time = data['time']
    points = data['points']
    print 'read in {} points, written at: {}'.format(len(points.keys()),
                                                     write_time)
    with cb2_robot.URRobot(host, port) as robot:
        for number in sorted([int(x) for x in points.keys()]):
            robot.add_goal(cb2_robot.Goal(points[str(number)]['joint'], False,
                                          'joint'))
            # TODO: this appears to skip the first point!
            robot.move_on_stop()
            print 'Beginning move: {}'.format(number)

if __name__ == "__main__":
    main()
