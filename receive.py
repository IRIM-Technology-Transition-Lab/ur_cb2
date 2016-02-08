"""A module to talk to UR CB2 robots"""

# pylint: disable=line-too-long
# everyone has a modern editor, no need to worry about line length, wrap as you see fit.

import socket
import struct
import array

class URReceiver(object):
    """A class to receive and process data from a UR Robot"""
    # pylint: disable=too-many-instance-attributes

    # Format spcifier:
    # ! : network (big endian)
    # I : unsigned int, message size
    # 101d : 101 doubles
    format = struct.Struct('! I 101d ') #: The format spec for a complete data packet
    formatLength = struct.Struct('! I') #: The format spec for the packet length field

    def __init__(self, ip, port):
        """Construct a UR Robot connection given connection paramaters

        Args:
            ip (int): The IP address to find the Robot
            port (int): The port to connect to on the robot (3001:primary client, 3002:secondary client, 3003: realtime client)
        """

        self.ip_addr = ip #: The IP address of the robot
        self.port = port #: The IP Port on which which to talk to robot
        self.clean_data = array.array('d', [0]*101) #: Storage location for all of the data returned by the robot
        self.raw_data = '' #: Storage location for complete raw data packet
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #: The socket for communications
        self.socket.connect((self.ip_addr, self.port)) #Connect to robot
        self.clean_packets = 0 #: The number of packets which have been received cleanly
        self.stub_packets = 0 #: The number of packets which have been received as stubs
        self.received = 0 #: The total number of complete datagrams which have been received
        self.waiting_data = [] #: Storage location for incomplete datasets
        self.new_data = False #: Whether new data is available for processing
        self.time = 0.0 #: Time elapsed since the controller was started
        self.target_joint_positions = [0.0]*6
        self.target_joint_velocities = [0.0]*6
        self.target_joint_accelerations = [0.0]*6
        self.target_joint_currents = [0.0]*6
        self.target_joint_moments = [0.0]*6 #:The target joint moments as torques
        self.actual_joint_positions = [0.0]*6
        self.actual_joint_velocities = [0.0]*6
        self.actual_joint_currents = [0.0]*6
        self.tool_accelartion = [0.0]*6 #:Tool x,y and z accelerometer values (software version 1.7)
        self.force_tcp = [0.0]*6 #:Generalised forces in the TCP
        self.position = [0.0]*6 #: Cartesian coordinates of the tool: (x,y,z,rx,ry,rz), where rx, ry and rz is a rotation vector representation of the tool orientation
        self.tool_speed = [0.0]*6 #:Speed of the tool given in cartesian coordinates
        self.digital_inputs = 0.0 #:Current state of the digital inputs. NOTE: these are bits encoded as int64_t, e.g. a value of 5 corresponds to bit 0 and bit 2 set high
        self.joint_temperature = [0.0]*6 #: Temperature of each joint in degrees celcius
        self.controller_period = 0.0 #:Controller realtime thread execution time
        self.robot_control_mode = 0.0 #: Robot control mode (see PolyScopeProgramServer on the "How to" page
        self.joint_control_modes = [0.0]*6 #: Joint control modes (see PolyScopeProgramServer on the "How to" page) (only from software version 1.8 and on)

    def __del__(self):
        """Shutdown connection and print aggregated connection stats"""

        print "closing ports"
        self.socket.close()
        print "Received: "+str(self.received)+" packets"
        print "Received: "+str(self.clean_packets)+" clean packets"
        print "Received: "+str(self.stub_packets)+" stub packets"

    def decode(self):
        """Decode the data stored in the class's rawData field.

        Only process the data if there is new data available. Unset the self.newData flag upon completion.
        """

        if self.new_data:
            self.clean_data = self.format.unpack(self.raw_data)
            self.time = self.clean_data[1]
            self.new_data = False

    def receive(self):
        """Receive data from the UR Robot.

        If an entire data set is not received, then store the data in a temporary location (self.waitingData). Once a complete packet is received, place the complete packet into self.rawData and set the newData flag
        """

        incoming_data = self.socket.recv(812) #expect to get 812 bytes
        if len(incoming_data) == 812:
            self.clean_packets += 1
        if self.formatLength.unpack(incoming_data[0:4])[0] == 812:
            self.waiting_data = incoming_data
        else:
            self.waiting_data += incoming_data
            self.stub_packets += 1

        if len(self.waiting_data) == 812:
            self.raw_data = self.waiting_data
            self.received += 1
            self.new_data = True

    def print_raw_data(self):
        """Print the raw data which is stored in self.raw_data"""

        print "Received (raw): "+self.raw_data+"\n"

    def print_data(self):
        """Print the processed data stored in self.clean_data"""
        print "Received (unpacked):\n "
        print self.clean_data
        print "\n"


HOST = "192.168.1.100"    # The remote host
PORT = 30003              # The same port as used by the server

MY_UR_RECEIVER = URReceiver(HOST, PORT)

while True:
    MY_UR_RECEIVER.receive()
    MY_UR_RECEIVER.decode()
    # myURReceiver.printData()
