"""A module to send commands to a UR robot

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


def deg_2_rad(x):
    """Converts from degrees to radians

    Args:
        x (float): The input in degrees

    Returns: A float of the value input converted to radians

    """
    return 3.14 * x / 180


def rad_2_deg(x):
    """Converts from radians to degrees

    Args:
        x (float): the input value in radians

    Returns: A float of the value input converted to degrees.

    """
    return (x / 3.14) * 180


def double_range(start, stop, step):
    """ Create a list from start to stop with interval step

    Args:
        start (float): The initial value
        stop (float): The ending value
        step (float): The step size

    Returns: A list from start to stop with interval step
    """
    r = start
    while r < stop:
        yield r
        r += step


def scale_path(origin, goal, multiplier=2):
    """Creates a new goal pose along a path.

    Takes the linear path from the origin to the goal and finds a pose on the
    path which is the length of the original path times multiplier from the
    origin.

    Args:
        origin (tuple or list of 6 floats): The origin pose
        goal (tuple or list of 6 floats): The goal pose
        multiplier (float): The multiplier which defines the new path's length

    Returns:
        tuple of 6 floats: the new pose along the path.
    """
    output = []
    for x, y in zip(origin, goal):
        output.append(x + (multiplier * (y - x)))

    return tuple(output)


def check_pose(pose):
    """Checks to make sure that a pose is valid.

    Checks that the pose is a 6 member tuple or list of floats. Does not return
    anything, simply raises exceptions if the pose is not valid.

    Args:
        pose: The pose to check

    Raises:
        TypeError: The pose was not valid.
    """
    if not isinstance(pose, (tuple, list)):
        raise TypeError("Expected tuple or list for pose")
    if not all([isinstance(x, float) for x in pose]):
        raise TypeError("Expected floats in pose")
    if not len(pose) == 6:
        raise TypeError("Expected 6 members in pose")


def check_xyz(pose):
    """Checks to make sure that a 3 tuple or list x,y,z is valid.

    Checks that the pose is a 3 member tuple or list of floats. Does not return
    anything, simply raises exceptions if the pose is not valid.

    Args:
        pose: The pose to check

    Raises:
        TypeError: The pose was not valid.
    """
    if not isinstance(pose, (tuple, list)):
        raise TypeError("Expected tuple or list for pose")
    if not all([isinstance(x, float) for x in pose]):
        raise TypeError("Expected floats in pose")
    if not len(pose) == 3:
        raise TypeError("Expected 3 members in pose")


def clean_list_tuple(input_data):
    """Return a string of the input without brackets or parentheses.

    Args:
        input_data (tuple or list): The tuple or list to convert to a string
            and strip of brackets or parentheses

    Raises:
        TypeError: input_data was not a tuple or list
    """

    if not isinstance(input_data, (tuple, list)):
        raise TypeError("Expected tuple for pose")
    return str(input_data)[1:-1]


class URSender(object):
    """A class to send commands to a UR CB2 Robot.

    Acceleration, velocity, and the blend radius are all stored and reused
    for each command. There is a separate values of acceleration and velocity
    for joint motions and cartesian motions. The user should adjust the
    values for acceleration and velocity as needed.

    Attributes:
        __socket: The Socket used to connect to the robot
        a_tool: Float, tool acceleration [m/s^2]
        v_tool: Float, tool speed [m/s]
        radius: Float, blend radius [m]. This allows the robots to miss
            points, so long as they are within the radius and continue
            moving. If you would like the robot to stop at every point,
            set this to zero. Because of the real time nature of this system,
            the value of the blend radius is low.
        a_joint: Float, joint acceleration of leading axis [rad/s^2]
        v_joint: Float, joint speed of leading axis [rad/s]
        tool_voltage_set: Boolean, whether the tool voltage has been set
        force_settings: Tuple of values to set force following settings on robot
        verbose: Boolean of whether to print info to the console
        sent: Integer of the number of commands sent
    """

    def __init__(self, open_socket, verbose=False):
        """Construct a UR Robot connection to send commands

        Args:
            open_socket (socket.socket): An already open and connected socket
            to a
                UR robot
            verbose (bool): Whether to print information to the terminal
        """

        self.__socket = open_socket
        self.a_tool = 1.2
        self.v_tool = 0.3
        self.radius = 0.0
        self.a_joint = 1.2
        self.v_joint = 0.3
        self.tool_voltage_set = False
        self.force_settings = None
        self.verbose = verbose
        self.sent = 0

    def __del__(self):
        """Destructor which prints the number of commands which were sent"""
        print 'Sent: {} commands'.format(self.sent)

    def send(self, message):
        """Sends the message over the IP pipe.

        Args:
            message (str): The message to be sent.
        """
        message += '\n'
        if self.verbose:
            print message
        self.__socket.send(message)
        self.sent += 1

    def set_force_mode(self, task_frame, selection_vector, wrench, frame_type,
                       limits):
        """Set robot to be controlled in force mode

        Args:
            task_frame (tuple or list of 6 floats): A pose vector that defines
                the force frame relative to the base frame.

            selection_vector (tuple or list of 6 binaries): A 6d vector that
                may only contain 0 or 1. 1 means that the robot will be
                compliant in the corresponding axis of the task frame,
                0 means the robot is not compliant along/about that axis.

            wrench (tuple or list of 6 floats): The forces/torques the robot
                is to apply to its environment. These values have different
                meanings whether they correspond to a compliant axis or not.
                Compliant axis: The robot will adjust its position along/about
                the axis in order to achieve the specified force/torque.
                Non-compliant axis: The robot follows the trajectory of the
                program but will account for an external force/torque of the
                specified value.

            frame_type (int): Specifies how the robot interprets the force
                frame. 1: The force frame is transformed in a way such that its
                y-axis is aligned with a vector pointing from the robot tcp
                towards the origin of the force frame. 2: The force frame is not
                transformed. 3: The force frame is transformed in a way such
                that its x-axis is the projection of the robot tcp velocity
                vector onto the x-y plane of the force frame. All other values
                of frame_type are invalid.

            limits (tuple or list of 6 floats): A 6d vector with float values
                that are interpreted differently for compliant/non-compliant
                axes: Compliant axes: The limit values for compliant axes
                are the maximum allowed tcp speed along/about the axis.
                Non-compliant axes: The limit values for non-compliant axes
                are the maximum allowed deviation along/about an axis between
                the actual tcp position and the one set by the program

        Raises:
            TypeError: The selection_vector was not a tuple, it did not
                have 6 members, or it was not filled with booleans; or
                frame_type was not an integer
            IndexError: frame_type was not in the set (1,2,3)
        """
        check_pose(task_frame)
        check_pose(wrench)
        check_pose(limits)
        if not isinstance(selection_vector, (tuple, list)):
            raise TypeError("Expected tuple or list for selection_vector")
        if not all([isinstance(x, bool) for x in selection_vector]):
            raise TypeError("Expected booleans in selection_vector")
        if not len(selection_vector) == 6:
            raise TypeError("Expected 6 members in selection_vector")
        if not isinstance(frame_type, int):
            raise TypeError("frame_type must be an integer")
        if frame_type not in (1, 2, 3):
            raise IndexError("frame_type must be in the set (1,2,3)")

        self.force_settings = (task_frame, selection_vector, wrench, frame_type,
                               limits)

    def force_mode_on(self):
        """Activates force mode.

        Requires that force mode settings have been passed in by
        set_force_mode()

        Raises:
            StandardError: Force settings have not been called.
        """
        if self.force_settings is None:
            raise StandardError('Force Settings have not been set with '
                                'set_force_mode')
        self.send('forcemode({},{},{},{},{})'.format(*self.force_settings))

    def force_mode_off(self):
        """Deactivates force mode"""

        self.send('end_force_mode()')

    def move_circular(self, pose_via, pose_to, cartesian=True):
        """Move to position, circular in tool-space.

        TCP moves on the circular arc segment from current pose, through pose
        via to pose to. Accelerates to and moves with constant tool speed
        self.v_tool.

        Args:
            pose_via (tuple or list of 6 floats): Path point through which to
                draw arc, only x,y,z are used
            pose_to (tuple or list of 6 floats): Destination point
            cartesian (bool): Whether supplied poses are cartesian or joint
                coordinates

        Raises:
            TypeError: cartesian was not a boolean
        """
        check_pose(pose_to)
        check_pose(pose_via)
        if not isinstance(cartesian, bool):
            raise TypeError('Cartesian must be a boolean')
        point = 'p' if cartesian else ''
        self.send('movec({}[{}],{}[{}],a={},v={},r={}'.format(
            point, clean_list_tuple(pose_via), point, clean_list_tuple(
                pose_to), self.a_tool, self.v_tool, self.radius))

    def move_joint(self, goal, time=None, cartesian=False):
        """
        Move to position (linear in joint-space).

        When using this command, the robot must be at standstill or come from a
        movej or movel with a blend. The speed and acceleration parameters
        controls the trapezoid speed profile of the move. The time parameter
        can be used in stead to set the time for this move. Time setting has
        priority over speed and acceleration settings. The blend radius can
        be set with the radius parameters, to avoid the robot stopping at the
        point. However, if the blend region of this mover overlaps with
        previous or following regions, this move will be skipped, and an
        'Overlapping Blends' warning message will be generated.

        Args:
            goal (tuple or list of 6 floats): Destination pose
            time (float): The time in which to complete the move, ignored if
                value is zero. Overrides speed and acceleration otherwise.
            cartesian (bool): Whether the goal point is in cartesian
                coordinates.

        Raises:
            TypeError: cartesian was not a boolean or time was not a float
            ValueError: time was not a positive value
        """
        check_pose(goal)
        if not isinstance(cartesian, bool):
            raise TypeError('Cartesian must be a boolean')
        if time is not None:
            if not isinstance(time, float):
                raise TypeError('time must be a float')
            if time <= 0:
                raise ValueError('time must be greater than zero')
            self.send('movej({}[{}],a={},v={},t={},r={})'.format(
                'p' if cartesian else '', clean_list_tuple(goal),
                self.a_joint, self.v_joint, time, self.radius))
        else:
            self.send('movej({}[{}],a={},v={},r={})'.format('p' if cartesian
                                                            else '',
                                                            clean_list_tuple(
                                                                goal),
                                                            self.a_joint,
                                                            self.v_joint,
                                                            self.radius))

    def move_line(self, goal, time=None, cartesian=True):
        """Move to position (linear in tool-space).

        When using this command, the robot must be at standstill or come from a
        movej or movel with a blend. The speed and acceleration parameters
        controls the trapezoid speed profile of the move. The time parameter
        can be used in stead to set the time for this move. Time setting has
        priority over speed and acceleration settings. The blend radius can
        be set with the radius parameters, to avoid the robot stopping at the
        point. However, if the blend region of this mover overlaps with
        previous or following regions, this move will be skipped, and an
        'Overlapping Blends' warning message will be generated.

        Args:
            goal (tuple or list of 6 floats): Destination pose
            time (float): The time in which to complete the move. Overrides
                speed and acceleration if set. Must be a positive value.
            cartesian (bool): Whether the goal point is in cartesian
                coordinates.

        Raises:
            TypeError: cartesian was not a boolean or time was not a float
            ValueError: time was not a positive value
        """
        check_pose(goal)
        if not isinstance(cartesian, bool):
            raise TypeError('Cartesian must be a boolean')
        if time is not None:
            if not isinstance(time, float):
                raise TypeError('time must be a float')
            if time <= 0:
                raise ValueError('time must be greater than zero')
            self.send('movel({}[{}],a={},v={},t={},r={})'.format(
                'p' if cartesian else '', clean_list_tuple(goal),
                self.a_tool, self.v_tool, time, self.radius))
        else:
            self.send('movel({}[{}],a={},v={},r={})'.format('p' if cartesian
                                                            else '',
                                                            clean_list_tuple(
                                                                goal),
                                                            self.a_tool,
                                                            self.v_tool,
                                                            self.radius))

    def move_process(self, goal, cartesian=True):
        """Move Process, guarantees that speed will be maintained.

        Blend circular (in tool-space) and move linear (in tool-space) to
        position. Accelerates to and moves with constant tool speed v.
        Failure to maintain tool speed leads to an error. Ideal for
        applications such as gluing

        Args:
            goal (tuple or list of 6 floats): Destination pose
            cartesian (bool): Whether the goal point is in cartesian
                coordinates.

        Raises:
            TypeError: cartesian was not a boolean
        """
        check_pose(goal)
        if not isinstance(cartesian, bool):
            raise TypeError('Cartesian must be a boolean')
        self.send('movep({}[{}],a={},v={},r={})'.format('p' if cartesian
                                                        else '',
                                                        clean_list_tuple(goal),
                                                        self.a_tool,
                                                        self.v_tool,
                                                        self.radius))

    def servo_circular(self, goal, cartesian=True):
        """Servo to position (circular in tool-space).

        Accelerates to and moves with constant tool speed v.

        Args:
            goal (tuple or list of 6 floats): Destination pose
            cartesian (bool): Whether the goal point is in cartesian
                coordinates.

        Raises:
            TypeError: cartesian was not a boolean
        """
        check_pose(goal)
        if not isinstance(cartesian, bool):
            raise TypeError('Cartesian must be a boolean')
        self.send('servoc({}[{}],a={},v={},r={})'.format('p' if cartesian
                                                         else '',
                                                         clean_list_tuple(
                                                             goal),
                                                         self.a_tool,
                                                         self.v_tool,
                                                         self.radius))

    def servo_joint(self, goal, time):
        """Servo to position (linear in joint-space).

        Args:
            goal (tuple or list of 6 floats): Destination pose
            time (float): The time in which to complete the move in seconds

        Raises:
            TypeError: time was not a float
            ValueError: time was non positive
        """

        check_pose(goal)

        if not isinstance(time, float):
            raise TypeError('Time must be a float')

        if time <= 0:
            raise ValueError('Time must be a positive value')

        self.send('servoj([{}],t={})'.format(clean_list_tuple(goal), time))

    def stop_joint(self):
        """Stop (linear in joint space)"""

        self.send('stopj({})'.format(self.a_joint))

    def stop_linear(self):
        """Stop (linear in tool space)"""

        self.send('stopl({})'.format(self.a_tool))

    def set_normal_gravity(self):
        """Sets a normal gravity for an upright mounted robot"""

        self.send('set_gravity([0,0,9.82])')

    def set_payload(self, mass, cog=None):
        """Set payload mass and center of gravity

        This function must be called, when the payload weight or weight
        distribution changes significantly - I.e when the robot picks up or puts
        down a heavy workpiece. The CoG argument is optional - If not provided,
        the Tool Center Point (TCP) will be used as the Center of Gravity (CoG).
        If the CoG argument is omitted, later calls to set tcp(pose) will change
        CoG to the new TCP. The CoG is specified as a Vector,
        [CoGx, CoGy, CoGz], displacement, from the tool mount.

        Args:
            mass (float): mass in kilograms
            cog (tuple or list of 3 floats): Center of Gravity: [CoGx, CoGy,
                CoGz] in meters.

        Raises:
            TypeError: mass was not a float
            ValueError: mass was negative
        """
        if not isinstance(mass, float):
            raise TypeError("Expected float for mass")
        if mass < 0:
            raise ValueError("Cannot have negative mass")
        if cog is not None:
            check_xyz(cog)
            self.send('set_payload(m={},[{}])'.format(mass,
                                                      clean_list_tuple(cog)))
        else:
            self.send('set_payload(m={})'.format(mass))

    def set_tcp(self, pose):
        """Set the TCP transformation.

        Set the transformation from the output flange coordinate system to the
        TCP as a pose.

        Args:
            pose (tuple or list of 6 floats): A pose describing the
            transformation.
        """

        check_pose(pose)
        self.send('set_tcp([{}])'.format(clean_list_tuple(pose)))

    def set_analog_input_range(self, port, input_range):
        """Set input_range of analog inputs

        Port 0 and 1 are in the control box, 2 and three are on the tool flange.

        Args:
            port (int): Port ID (0,1,2,3)
            input_range (int): On the controller: [0: 0-5V, 1: -5-5V, 2: 0-10V
                3: -10-10V] On the tool flange: [0: 0-5V, 1: 0-10V 2: 0-20mA]

        Raises:
            TypeError: Either port or input_range was not an integer
            IndexError: input_range was not a valid value for the selected port
        """
        if not isinstance(port, int):
            raise TypeError("port must be an integer")
        if not isinstance(input_range, int):
            raise TypeError("input_range must be an integer")
        if port in (0, 1):
            if input_range not in (0, 1, 2, 3):
                raise IndexError("input_range must be in the set (0,1,2,3) for"
                                 "the controller outputs.")
        elif port in (2, 3):
            raise IndexError("input_range must be in the set (0,1,2) for "
                             "the tool outputs.")
        else:
            raise IndexError("port must be in the set (0,1,2,3)")
        self.send('set_analog_inputrange({},{})'.format(port, input_range))

    def set_analog_out(self, ao_id, level):
        """Set analog output level

        Args:
            ao_id (int): The output ID#. AO 0 and 1 are in the control box.
                There is not analog output on the tool.
            level (float): The output signal level 0-1, corresponding to 4-20mA
                or 0-10V based on set_analog_output_domain.

        Raises:
            TypeError: Either ao_id was not an integer or level was not a float
            IndexError: ao_id was not a valid value (0,1)
        """
        if not isinstance(ao_id, int):
            raise TypeError("Expected int for ao_id")
        if not isinstance(level, float):
            raise TypeError("Expected int for domain")
        if ao_id not in (0, 1):
            raise IndexError('The Analog output ID must be either 0 or 1')
        if level > 1 or level < 0:
            raise ValueError("Level must be 0-1")
        self.send('set_analog_out({},{})'.format(ao_id, level))

    def set_analog_output_domain(self, ao_id, domain):
        """Sets the signal domain of the analog outputs.

        The analog outputs can be flexibly set to operate on a 4-20mA or 0-10V
        scale. There are two analog outputs on the controller and none on the
        tool.

        Args:
            ao_id (int): The port number (0 or 1).
            domain (int): 0 for 4-20mA and 1 for 0-10V

        Raises:
            TypeError: Either ao_id or domain was not an integer
            IndexError: ao_id or domain was not a valid value (0,1)
        """
        if not isinstance(ao_id, int):
            raise TypeError("Expected int for ao_id")
        if not isinstance(domain, int):
            raise TypeError("Expected int for domain")
        if ao_id not in (0, 1):
            raise IndexError('The Analog output ID must be either 0 or 1')
        if domain not in (0, 1):
            raise IndexError('The Analog domain must be either 0 or 1')
        self.send('set_analog_outputdomain({},{})'.format(
            ao_id, domain))

    def set_digital_out(self, do_id, level):
        """Set the value for DO[do_id]

        Args:
            do_id (int): The digital output #. Values 0-7 are on the control
                box. Values 8 and 9 are on the tool flange. You must set the
                tool voltage prior to attempting to modify the tool flange
                outputs.
            level (bool): High or low setting for output

        Raises:
            TypeError: do_id was not an integer or level was not a boolean
            StandardError: The tool voltage was not set prior to attempting
                this call
            IndexError: do_id was out of range (0-9)
        """
        if not isinstance(do_id, int):
            raise TypeError("Expected int for do_id")
        if do_id in (8, 9) and not self.tool_voltage_set:
            raise StandardError("The tool voltage must be set prior to "
                                "attempting to alter tool outputs")
        if do_id > 9 or do_id < 0:
            raise IndexError("The valid range for digital outputs is 0-9")
        if not isinstance(level, bool):
            raise TypeError("Expected boolean for level")

        self.send('set_digital_out({},{})'.format(do_id, 1 if level else 0))

    def set_tool_voltage(self, voltage):
        """Sets the voltage level for the power supply that delivers power to
        the connector plug in the tool flange of the robot. The voltage can
        be 0,
        12 or 24 volts.

        Args:
            voltage (int):The voltage to set at the tool connector

        Raises:
            TypeError: voltage was not an integer
            ValueError: voltage was not valued 0, 12, or 24
        """
        if not isinstance(voltage, int):
            raise TypeError("Expected int for voltage")
        if voltage not in (0, 12, 24):
            raise ValueError("Voltage must be 0, 12, or 24")
        self.send('set_tool_voltage({})'.format(voltage))
        self.tool_voltage_set = True
