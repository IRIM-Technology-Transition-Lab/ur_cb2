"""A basic script to demonstrate usage of the cb2_receive module.

There are a few lines which are commented out. Uncomment these lines to see a
demonstration of the parallel nature of the cb2_receive module.

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
