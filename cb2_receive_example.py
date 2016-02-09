import cb2_receive
import time

HOST = "192.168.1.100"    # The remote host
PORT = 30003              # The same port as used by the server

MY_UR_RECEIVER = cb2_receive.URReceiver(HOST, PORT)

MY_UR_RECEIVER.start()

some_num = 0

try:
    while True:
        print "\n\n" + str(some_num) + "\n\n"
        some_num += 1
        time.sleep(.25)
except KeyboardInterrupt:
    MY_UR_RECEIVER.stop()
    pass
