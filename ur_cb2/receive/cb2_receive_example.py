"""A basic script to demonstrate usage of the cb2_receive module.

There are a few lines which are commented out. Uncomment these lines to see a
demonstration of the parallel nature of the cb2_receive module.

Copyright (c) 2016 GTRC. All rights reserved.
"""

import socket
import time
from contextlib import closing
import cb2_receive
import argparse


def main():
    # Parse in arguments
    parser = argparse.ArgumentParser(
        description='Save Points',
        epilog="This software is designed to show the status of a UR CB2 Robot."
               " Simply run the program with appropriate arguments and it will"
               " print useful information about the robot to the terminal."
               " If information is not printed nicely, make your terminal "
               "larger")

    parser.add_argument("--ip", metavar="ip", type=str,
                        help='IP address of the robot', default="192.168.1.100")

    parser.add_argument("--port", metavar="port", type=int,
                        help='IP port on the robot', default=30003)

    args = parser.parse_args()
    host = args.ip    # The remote host
    port = args.port  # The same port as used by the server

    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM))\
            as robot_socket:
        robot_socket.connect((host, port))
        with cb2_receive.URReceiver(robot_socket, True) as my_ur_receiver:
            my_ur_receiver.start()
            # some_num = 0
            while True:
                # print "\n\n" + str(some_num) + "\n\n"
                # some_num += 1
                time.sleep(.25)

if __name__ == "__main__":
    main()
