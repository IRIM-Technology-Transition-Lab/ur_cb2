"""A basic script to demonstrate usage of the cb2_receive module.

There are a few lines which are commented out. Uncomment these lines to see a
demonstration of the parallel nature of the cb2_receive module.

Copyright (c) 2016 GTRC. All rights reserved.
"""

import socket
import time
from contextlib import closing
import cb2_receive


def main():
    host = "192.168.1.100"    # The remote host
    port = 30003              # The same port as used by the server

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
