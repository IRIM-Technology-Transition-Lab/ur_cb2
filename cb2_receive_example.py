import cb2_receive
import time

HOST = "192.168.1.100"    # The remote host
PORT = 30003              # The same port as used by the server

my_ur_receiver = cb2_receive.URReceiver(HOST, PORT, True)

my_ur_receiver.start()

some_num = 0

try:
    while True:
        print "\n\n" + str(some_num) + "\n\n"
        some_num += 1
        time.sleep(.25)
except KeyboardInterrupt:
    my_ur_receiver.stop()
    pass
