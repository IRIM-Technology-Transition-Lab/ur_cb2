"""A module to receive data from UR CB2 robots"""

# pylint: disable=line-too-long
# everyone has a modern editor, no need to worry about line length, wrap as you see fit.

import socket
import struct
import array

class URReceiver(object):
    """A class to receive and process data from a UR Robot

    Attributes:
        ip_addr: Integer of IP address of the robot
        port: Integer of the IP Port on which which to talk to robot
        clean_data: Double array of length 101 for all of the data returned by the robot
        raw_data = '' #: String of complete raw data packet
        socket: The socket for communications
        clean_packets: The Integer number of packets which have been received cleanly
        stub_packets: The Integer number of packets which have been received as stubs
        received: The total Integer number of complete datagrams which have been received
        waiting_data: String to hold incomplete datasets
        new_data: Boolean whether new data is available for processing
        time: Double of time elapsed since the controller was started
        target_joint_positions: 6 member Double list of target joint positions
        target_joint_velocities: 6 member Double list of target joint velocities
        target_joint_accelerations: 6 member Double list of target joint accelerations
        target_joint_currents: 6 member Double list of target joint currents
        target_joint_moments: 6 member Double list of target joint moments as torques
        actual_joint_positions: 6 member Double list of actual joint positions
        actual_joint_velocities: 6 member Double list of actual joint velocities
        actual_joint_currents: 6 member Double list of actual joint currents
        tool_acceleromete: 3 member Double list of ool x,y and z accelerometer values (software version 1.7)
        force_tcp: 6 member Double list of generalised forces in the TCP
        position: 6 member Double list of cartesian coordinates of the tool: (x,y,z,rx,ry,rz), where rx, ry and rz is a rotation vector representation of the tool orientation
        tool_speed: 6 member Double list of speed of the tool given in cartesian coordinates
        digital_inputs: Current state of the digital inputs. NOTE: these are bits encoded as int64_t, e.g. a value of 5 corresponds to bit 0 and bit 2 set high
        joint_temperature: 6 member Double list of temperature of each joint in degrees celcius
        controller_period: Double of controller realtime thread execution time
        robot_control_mode: Double of robot control mode (see PolyScopeProgramServer on the "How to" page
        joint_control_modes: 6 member Double list of joint control modes (see PolyScopeProgramServer on the "How to" page) (only from software version 1.8 and on)

        self.socket.connect((self.ip_addr, self.port)) #Connect to robot
        print "\033[2J" #Clear screen
    """
    # pylint: disable=too-many-instance-attributes

    # Format spcifier:
    # ! : network (big endian)
    # I : unsigned int, message size
    # 85d : 85 doubles
    # q : int64_t for digital inputs
    # 15d : 15 doubles
    format = struct.Struct('! I 85d q 15d') #: The format spec for a complete data packet
    formatLength = struct.Struct('! I') #: The format spec for the packet length field
    name_width = 30 #: The width to be given to name items when printing out
    precision = 4 #: The precision for printing data
    double_format_string = "{:+0"+str(precision+7)+"."+str(precision)+"f}"

    def __init__(self, ip, port):
        """Construct a UR Robot connection given connection paramaters

        Args:
            ip (int): The IP address to find the Robot
            port (int): The port to connect to on the robot (3001:primary client, 3002:secondary client, 3003: realtime client)
        """

        self.ip_addr = ip
        self.port = port
        self.clean_data = array.array('d', [0]*101)
        self.raw_data = ''
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clean_packets = 0
        self.stub_packets = 0
        self.received = 0
        self.waiting_data = ''
        self.new_data = False
        self.time = 0.0
        self.target_joint_positions = [0.0]*6
        self.target_joint_velocities = [0.0]*6
        self.target_joint_accelerations = [0.0]*6
        self.target_joint_currents = [0.0]*6
        self.target_joint_moments = [0.0]*6
        self.actual_joint_positions = [0.0]*6
        self.actual_joint_velocities = [0.0]*6
        self.actual_joint_currents = [0.0]*6
        self.tool_accelerometer = [0.0]*3
        self.force_tcp = [0.0]*6
        self.position = [0.0]*6
        self.tool_speed = [0.0]*6
        self.digital_inputs = 0
        self.joint_temperature = [0.0]*6
        self.controller_period = 0.0
        self.robot_control_mode = 0.0
        self.joint_control_modes = [0.0]*6

        self.socket.connect((self.ip_addr, self.port)) #Connect to robot
        print "\033[2J" #Clear screen

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
            self.target_joint_positions = self.clean_data[2:8]
            self.target_joint_velocities = self.clean_data[8:14]
            self.target_joint_accelerations = self.clean_data[14:20]
            self.target_joint_currents = self.clean_data[20:26]
            self.target_joint_moments = self.clean_data[26:32]
            self.actual_joint_positions = self.clean_data[32:38]
            self.actual_joint_velocities = self.clean_data[38:44]
            self.actual_joint_currents = self.clean_data[44:50]
            self.tool_accelerometer = self.clean_data[50:53]
            # unused = self.clean_data[53:68]
            self.force_tcp = self.clean_data[68:74]
            self.position = self.clean_data[74:80]
            self.tool_speed = self.clean_data[80:86]
            self.digital_inputs = self.clean_data[86]
            self.joint_temperature = self.clean_data[87:93]
            self.controller_period = self.clean_data[93]
            # testvalue = self.clean_data[94]
            self.robot_control_mode = self.clean_data[95]
            self.joint_control_modes = self.clean_data[96:102]
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

    def output_data_item(self, name, values):
        """Output item with name and values, specified by self.name_width and self.precision.

        Args:
            name (str): The name of the value
            values (float, int, tuple of float, list of float): The list of values
        """

        to_print = ("%-"+str(self.name_width)+"s") % name
        if isinstance(values, (list, tuple)):
            to_print += ": [%s]" % ', '.join(self.double_format_string.format(x) for x in values)
        elif isinstance(values, int):
            to_print += ": [%s]" % str(int)
        elif isinstance(values, float):
            to_print += ": [%s]" % self.double_format_string.format(values)
        else:
            print "I don't know that data type: " + str(type(values))
        print to_print

    def print_parsed_data(self):
        """Print the parsed data"""

        print "\033[H"
        self.output_data_item("Time since controller turn on", self.time)
        self.output_data_item("Target joint positions", self.target_joint_positions)
        self.output_data_item("Target joint velocities", self.target_joint_velocities)
        self.output_data_item("Target joint accelerations", self.target_joint_accelerations)
        self.output_data_item("Target joint currents", self.target_joint_currents)
        self.output_data_item("Target joint moments (torque)", self.target_joint_moments)
        self.output_data_item("Actual joint positions", self.actual_joint_positions)
        self.output_data_item("Target joint velocities", self.actual_joint_velocities)
        self.output_data_item("Target joint currents", self.actual_joint_currents)
        self.output_data_item("Tool accelerometer values", self.tool_accelerometer)
        self.output_data_item("Generalised forces in the TCP", self.force_tcp)
        self.output_data_item("Cartesian tool position", self.position)
        self.output_data_item("Cartesian tool speed", self.tool_speed)
        self.output_data_item("Joint temperatures (deg C)", self.joint_temperature)
        self.output_data_item("Controller period", self.controller_period)
        self.output_data_item("Robot control mode", self.robot_control_mode)
        self.output_data_item("Joint control modes", self.joint_control_modes)
        print (("%-"+str(self.name_width)+"s") %"Digital Input Number") + ": " + '|'.join('{:^2d}'.format(x) for x in range(0, 18))
        print (("%-"+str(self.name_width)+"s") %"Digital Input Value: ") + ": " + '|'.join('{:^2s}'.format(x) for x in '{:018b}'.format(self.digital_inputs)[::-1])


HOST = "192.168.1.100"    # The remote host
PORT = 30003              # The same port as used by the server

MY_UR_RECEIVER = URReceiver(HOST, PORT)

while True:
    MY_UR_RECEIVER.receive()
    MY_UR_RECEIVER.decode()
    MY_UR_RECEIVER.print_parsed_data()
