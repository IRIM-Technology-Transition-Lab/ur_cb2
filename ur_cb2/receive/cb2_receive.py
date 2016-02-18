"""A module to receive data from UR CB2 robots.

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
import struct
import array
import threading


class URReceiver(object):
    """A class to receive and process data from a UR Robot

    The receiving and processing can be run in a separate thread by calling
    start(). The stop() command must be called before exiting to halt the
    additional thread. Alternatively, receive(), decode(), and
    print_parsed_data() can be called in sequence in order to receive,
    decode, and print data. One should not call receive(), decode(), or any
    of the print methods, if a separate thread is being used. You should
    never write to any of the data fields externally, however you can read
    from them. Python's atomic read/write architecture should prevent you
    from getting any half baked results from basic types, for all lists and
    tuples, you must lock using lock (recommend that you use `with lock:`
    paradigm.

    Attributes:
        clean_data: Double array of length 101 for all of the data returned by
            the robot
        raw_data = '' #: String of complete raw data packet
        __socket: The socket for communications
        clean_packets: The Integer number of packets which have been received
            cleanly
        stub_packets: The Integer number of packets which have been received
            as stubs
        received: The total Integer number of complete data sets which have
            been received
        waiting_data: String to hold incomplete data sets
        new_data: Boolean whether new data is available for processing
        time: Double of time elapsed since the controller was started
        target_joint_positions: 6 member Double list of target joint positions
        target_joint_velocities: 6 member Double list of target joint velocities
        target_joint_accelerations: 6 member Double list of target joint
            accelerations
        target_joint_currents: 6 member Double list of target joint currents
        target_joint_moments: 6 member Double list of target joint moments as
            torques
        actual_joint_positions: 6 member Double list of actual joint positions
        actual_joint_velocities: 6 member Double list of actual joint velocities
        actual_joint_currents: 6 member Double list of actual joint currents
        tool_accelerometer: 3 member Double list of ool x,y and z accelerometer
            values (software version 1.7)
        force_tcp: 6 member Double list of generalised forces in the TCP
        position: 6 member Double list of cartesian coordinates of the tool:
            (x,y,z,rx,ry,rz), where rx, ry and rz is a rotation vector
            representation of the tool orientation
        tool_speed: 6 member Double list of speed of the tool given in cartesian
            coordinates
        digital_inputs: Current state of the digital inputs. NOTE: these are
            bits encoded as int64_t, e.g. a value of 5 corresponds to bit 0 and
            bit 2 set high
        joint_temperature: 6 member Double list of temperature of each joint in
            degrees celsius
        controller_period: Double of controller real time thread execution time
        robot_control_mode: Double of robot control mode (see
            PolyScopeProgramServer on the "How to" page
        joint_control_modes: 6 member Double list of joint control modes (see
            PolyScopeProgramServer on the "How to" page) (only from software
            version 1.8 and on)
        run: Boolean on whether to run or not
        __receiving_thread: Thread object for running the receiving and parsing
            loops
        verbose: Boolean defining whether or not to print data
        lock: A threading lock which is used to protect data from race
            conditions
        _is_stopped: A boolean specifying whether the robot is stopped
    """

    # Format specifier:
    # ! : network (big endian)
    # I : unsigned int, message size
    # 85d : 85 doubles
    # q : int64_t for digital inputs
    # 15d : 15 doubles

    #: Format spec for complete data packet
    format = struct.Struct('! I 85d q 15d')
    #: The format spec for the packet length field
    formatLength = struct.Struct('! I')
    #: The width to be given to name items when printing out
    name_width = 30
    #: The precision for printing data
    precision = 7
    double_format_string = "{:+0"+str(precision+4)+"."+str(precision)+"f}"

    def __init__(self, open_socket, verbose=False):
        """Construct a UR Robot connection given connection parameters

        Args:
            open_socket (socket.socket): The socket to use for communications.
            verbose (bool): Whether to print received data in main loop
        """
        self.clean_data = array.array('d', [0] * 101)
        self.raw_data = ''
        self.__socket = open_socket
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
        self.run = False
        self.__receiving_thread = None
        self.verbose = verbose
        self.lock = threading.Lock()
        self._is_stopped = False
        if verbose:
            print "\033[2J"  # Clear screen

    def __del__(self):
        """Shutdown side thread and print aggregated connection stats"""
        self.stop()

        print "Received: "+str(self.received) + " data sets"
        print "Received: "+str(self.clean_packets) + " clean packets"
        print "Received: "+str(self.stub_packets) + " stub packets"

    def decode(self):
        """Decode the data stored in the class's rawData field.

        Only process the data if there is new data available. Unset the
        self.newData flag upon completion. Note, this will lock the data set
        and block execution in a number of other functions
        """
        with self.lock:
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
                # test value = self.clean_data[94]
                self.robot_control_mode = self.clean_data[95]
                self.joint_control_modes = self.clean_data[96:102]
                self.new_data = False
        self._is_stopped = self.is_stopped()

    def receive(self):
        """Receive data from the UR Robot.

        If an entire data set is not received, then store the data in a
        temporary location (self.waitingData). Once a complete packet is
        received, place the complete packet into self.rawData and set the
        newData flag. Note, this will lock the data set and block execution in a
        number of other functions once a full data set is built.
        """
        incoming_data = self.__socket.recv(812)  # expect to get 812 bytes
        if len(incoming_data) == 812:
            self.clean_packets += 1
        else:
            self.stub_packets += 1
        if self.formatLength.unpack(incoming_data[0:4])[0] == 812:
            self.waiting_data = incoming_data
        else:
            self.waiting_data += incoming_data

        if len(self.waiting_data) == 812:
            with self.lock:
                self.raw_data = self.waiting_data
            self.received += 1
            self.new_data = True

    def print_raw_data(self):
        """Print the raw data which is stored in self.raw_data.

        Note, this will lock the data set and block execution in a number of
        other functions
        """
        with self.lock:
            print "Received (raw): "+self.raw_data + "\n"

    def print_data(self):
        """Print the processed data stored in self.clean_data

        Note, this will lock the data set and block execution in a number of
        other functions
        """
        with self.lock:
            print "Received (unpacked):\n "
            print self.clean_data
            print "\n"

    def output_data_item(self, name, values):
        """Output item with name and values.

        Formatting is specified by self.name_width and self.precision.

        Args:
            name (str): The name of the value
            values (float, int, tuple of float, list of float): The list of
                values
        """
        to_print = ("%-"+str(self.name_width)+"s") % name
        if isinstance(values, (list, tuple)):
            to_print += ": [%s]" % ', '.join(self.double_format_string.format(x)
                                             for x in values)
        elif isinstance(values, (int, bool)):
            to_print += ": [%s]" % str(values)
        elif isinstance(values, float):
            to_print += ": [%s]" % self.double_format_string.format(values)
        else:
            print "I don't know that data type: " + str(type(values))
        print to_print

    def print_parsed_data(self):
        """Print the parsed data

        Note, this will lock the data set and block execution in a number of
        other functions
        """
        with self.lock:
            print "\033[H"
            self.output_data_item("Time since controller turn on",
                                  self.time)
            self.output_data_item("Target joint positions",
                                  self.target_joint_positions)
            self.output_data_item("Target joint velocities",
                                  self.target_joint_velocities)
            self.output_data_item("Target joint accelerations",
                                  self.target_joint_accelerations)
            self.output_data_item("Target joint currents",
                                  self.target_joint_currents)
            self.output_data_item("Target joint moments (torque)",
                                  self.target_joint_moments)
            self.output_data_item("Actual joint positions",
                                  self.actual_joint_positions)
            self.output_data_item("Actual joint velocities",
                                  self.actual_joint_velocities)
            self.output_data_item("Actual joint currents",
                                  self.actual_joint_currents)
            self.output_data_item("Tool accelerometer values",
                                  self.tool_accelerometer)
            self.output_data_item("Generalised forces in the TCP",
                                  self.force_tcp)
            self.output_data_item("Cartesian tool position",
                                  self.position)
            self.output_data_item("Cartesian tool speed",
                                  self.tool_speed)
            self.output_data_item("Joint temperatures (deg C)",
                                  self.joint_temperature)
            self.output_data_item("Controller period",
                                  self.controller_period)
            self.output_data_item("Robot control mode",
                                  self.robot_control_mode)
            self.output_data_item("Joint control modes",
                                  self.joint_control_modes)
            print ((("%-"+str(self.name_width)+"s") % "Digital Input Number") +
                   ": " + '|'.join('{:^2d}'.format(x) for x in range(0, 18)))
            print ((("%-"+str(self.name_width)+"s") % "Digital Input Value: ") +
                   ": " + '|'.join('{:^2s}'.format(x) for x in '{:018b}'.format(
                    self.digital_inputs)[::-1]))
            self.output_data_item("Is Stopped:",
                                  self._is_stopped)

    def start(self):
        """Spawn a new thread for receiving and run it"""
        if (self.__receiving_thread is None or
                not self.__receiving_thread.is_alive()):
            self.run = True
            self.__receiving_thread = threading.Thread(group=None,
                                                       target=self.loop,
                                                       name='receiving_thread',
                                                       args=(),
                                                       kwargs={})
            self.__receiving_thread.start()

    def loop(self):
        """The main loop which receives, decodes, and optionally prints data"""
        while self.run:
            self.receive()
            self.decode()
            if self.verbose:
                self.print_parsed_data()

    def stop(self):
        """Stops execution of the auxiliary receiving thread"""
        if self.__receiving_thread is not None:
            if self.__receiving_thread.is_alive():
                self.verbose_print('attempting to shutdown auxiliary thread',
                                   '*')
                self.run = False  # Python writes like this are atomic
                self.__receiving_thread.join()
                self.verbose_print('\033[500D')
                self.verbose_print('\033[500C')
                self.verbose_print('-', '-', 40)
                if self.__receiving_thread.is_alive():
                    self.verbose_print('failed to shutdown auxiliary thread',
                                       '*')
                else:
                    self.verbose_print('shutdown auxiliary thread', '*')
            else:
                self.verbose_print('auxiliary thread already shutdown', '*')
        else:
            self.verbose_print('no auxiliary threads exist', '*')

    def verbose_print(self, string_input, emphasis='', count=5):
        """Print input if verbose is set

        Args:
            string_input (str): The input string to be printed.
            emphasis (str): Emphasis character to be placed around input.
            count (int): Number of emphasis characters to use.
        """

        if self.verbose:
            if emphasis == '':
                print string_input
            else:
                print (emphasis*count + " " + string_input + " " +
                       emphasis * count)

    def is_stopped(self, error=0.005):
        """Check whether the robot is stopped.

        Check whether the joint velocities are all below some error. Note, this
        will lock the data set and block execution in a number of other
        functions

        Args:
            error (float): The error range to define "stopped"

        Returns: Boolean, whether the robot is stopped.
        """
        with self.lock:
            to_return = (
                all(v == 0 for v in self.target_joint_velocities) and
                all(v < error for v in self.actual_joint_velocities))
        return to_return

    def at_goal(self, goal, cartesian, error=0.005):
        """Check whether the robot is at a goal point.

        Check whether the differences between the joint or cartesian
        coordinates are all below some error. This can be used to
        determine if a move has been completed. It can also be used to
        create blends by beginning the next move prior to the current one
        reaching its goal. Note, this will lock the data set and block execution
        in a number of other functions.

        Args:
            goal (6 member tuple or list of floats): The goal to check against
            cartesian (bool): Whether the goal is in cartesian coordinates or
                not (in which case joint coordinates)
            error (float): The error range in which to consider an object at
                its goal, in meters for cartesian space and radians for axis
                space.

        Returns: Boolean, whether the current position is within the error
            range of the goal.
        """
        with self.lock:
            to_return = (
                all(abs(g-a) < error for g, a in zip(self.position, goal))
                if cartesian else
                all(abs(g-a) < error for g, a in
                    zip(self.actual_joint_positions, goal)))
        return to_return

    def __enter__(self):
        """Enters the URRobot receiver from a with statement"""
        return self

    def __exit__(self, *_):
        """Exits at the end of a context manager statement by destructing."""
        self.stop()
