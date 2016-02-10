import socket


def deg_2_rad(x):
    return 3.14 * x / 180


def rad_2_deg(x):
    return (x / 3.14) * 180


def double_range(start, stop, step):
    r = start
    while r < stop:
        yield r
        r += step

def scale_path(origin,goal,mult=2):
    """Creates a new goal pose along a path.

    Takes the linear path from the origin to the goal and finds a pose on the
    path which is the length of the original path times mult from the origin.

    Args:
        origin (tuple or list of 6 floats): The origin pose
        goal (tuple or list of 6 floats): The goal pose
        mult (float): The multiplier which defines the new path's length

    Returns:
        tuple of 6 floats: the new pose along the path.
    """


class URSender(object):
    """A class to send commands to a UR CB2 Robot"""

    def __init__(self, ip, port):
        """Construct a UR Robot connection to send commands

        Args:
            ip (str): The IP address to find the Robot
            port (int): The port to connect to on the robot (
                3001:primary client, 3002:secondary client,
                3003: real time client)
        """

        self.ip_address = ip
        self.port = port
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.a_tool = 1.2 # tool acceleration [m/sˆ2]
        self.v_tool = 0.3 # tool speed [m/s]
        self.radius = 0.0 # blend radius [m]
        self.a_joint = 1.2 # joint acceleration of leading axis [rad/sˆ2]
        self.v_joint = 0.3 # joint speed of leading axis [rad/s]
        self.tool_voltage_set = False

    def __del__(self):
        """Shutdown IP port"""

        print 'closing ports'
        self.__socket.shutdown(socket.SHUT_RDWR)
        self.__socket.close()
        print 'shutdown and closed socket'

    def send(self,message):
        """Sends the message over the IP pipe.

        Args:
            message (str): The message to be sent.
        """

    def set_force_mode(self, task_frame, selection_vector, wrench, type,
                       limits):
        """Set robot to be controlled in force mode

        Args:
            task frame (tuple or list of 6 floats): A pose vector that defines
                the force frame relative to the base frame.

            selection vector (tuple or list of 6 binaries): A 6d vector that
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

            type (int): An integer specifying how the robot interprets the force
                frame. 1: The force frame is transformed in a way such that its
                y-axis is aligned with a vector pointing from the robot tcp
                towards the origin of the force frame. 2: The force frame is not
                transformed. 3: The force frame is transformed in a way such
                that its x-axis is the projection of the robot tcp velocity
                vector onto the x-y plane of the force frame. All other values
                of type are invalid.

            limits (tuple or list of 6 floats): A 6d vector with float values
                that are interpreted differently for compliant/non-compliant
                axes: Compliant axes: The limit values for compliant axes
                are the maximum allowed tcp speed along/about the axis.
                Non-compliant axes: The limit values for non-compliant axes
                are the maximum allowed deviation along/about an axis between
                the actual tcp position and the one set by the program
        """
        self.var = 0

    def force_mode_on(self):
        """Activates force mode.

        Requires that force mode settings have been passed in by
        set_force_mode()
        """

        self.send('forcemode(taskframe=,selection_vector=,wrench=,type=,limits=)')

    def force_mode_off(self):
        """Deactivates force mode"""

        self.send('end_force_mode()')

    def move_circular(self, pose_via, pose_to, cartesian=True):
        """Move to position, circular in tool-space.

        TCP moves on the circular arc segment from current pose, through pose
        via to pose to. Accelerates to and moves with constant tool speed
        self.v_tool.

        Args:
            pose_via (tuple or lsit of 3 floats): Path point through which to
                draw arc
            pose_to (tuple or list of 6 floats): Destination point
            cartesian (bool): Whether supplied poses are cartesian or joint
                coordinates
        """

        self.send('movec(pose_via=,pose_to=,a=self.tool_accel,v=self.tool_vel,r=self.bend)')

    def move_joint(self, goal, time=0, cartesian=False):
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
        """
        self.send('movej(q=goal,a=self.joint_accel,v=self.joint_vel,t=time,r=self.blend)')

    def move_line(self, goal, time=0, cartesian=True):
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
            time (float): The time in which to complete the move, ignored if
                value is zero. Overrides speed and acceleration otherwise.
            cartesian (bool): Whether the goal point is in cartesian
                coordinates.
        """

        self.send('movel(pose=goal,a=self.tool_accel,v=self.tool_vel,t=time,r=self.tool_blend)')

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
        """

        self.send('movep(pose=goal,a=self.tool_accel,v=self.tool_vel,r=self.tool_blend)')

    def servo_circular(self, goal, cartesian=True):
        """Servo to position (circular in tool-space).

        Accelerates to and moves with constant tool speed v.

        Args:
            goal (tuple or list of 6 floats): Destination pose
            cartesian (bool): Whether the goal point is in cartesian
                coordinates.
        """
        check_pose(goal)

        if not isinstance(cartesian, bool):
            raise TypeError('Cartesian must be a boolean')

        if cartesian:
            self.send('servoc(pose=goal,a,v,r)'.format(clean_list_tuple(goal)))
        else:


    def servo_joint(self, goal, time):
        """Servo to position (linear in joint-space).

        Args:
            goal (tuple or list of 6 floats): Destination pose
            time (float): The time in which to complete the move in seconds
        """

        check_pose(goal)

        if not isinstance(time, float):
            raise TypeError('Time must be a float')

        if time <= 0:
            raise ValueError('Time must be a positive value')

        self.send('servoj(q=[{}],t={})'.format(clean_list_tuple(goal), time))

    def stop_joint(self):
        """Stop (linear in joint space)"""

        self.send('stopj(a={})'.format(self.a_joint))

    def stop_linear(self):
        """Stop (linear in tool space)"""

        self.send('stopl(a={})'.format(self.a_tool))

    def set_normal_gravity(self):
        """Sets a normal gravity for an upright mounted robot"""

        self.send('set_gravity([0,0,9.82])')

    def set_payload(self,mass,cog=None):
        """Set payload mass and center of gravity

        This function must be called, when the payload weight or weight
        distribution changes significantly - I.e when the robot picks up or puts
        down a heavy workpiece. The CoG argument is optional - If not provided,
        the Tool Center Point (TCP) will be used as the Center of Gravity (CoG).
        If the CoG argument is omitted, later calls to set tcp(pose) will change
        CoG to the new TCP. The CoG is specified as a Vector,
        [CoGx, CoGy, CoGz], displacement, from the toolmount.

        Args:
            mass (float): mass in kilograms
            cog (tuple or list of 3 floats): Center of Gravity: [CoGx, CoGy,
                CoGz] in meters.
        """
        if not isinstance(mass, float):
            raise TypeError("Expected float for mass")

        if cog is not None:
            check_xyz(cog)

        if mass < 0:
            raise ValueError("Cannot have negative mass")

        if cog is not None:
            self.send('set_payload(m={},CoG=[{}])'.format(mass,
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

    def set_analog_input_range(self, port, range):
        """Set range of analog inputs

        Port 0 and 1 are in the control box, 2 and three are on the tool flange.

        Args:
            port (int): Port ID (0,1,2,3)
            range (int): On the controller: [0: 0-5V, 1: -5-5V, 2: 0-10V 3: -10-10V] On the tool flange: [0: 0-5V, 1: 0-10V 2: 0-20mA]
        """

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
        the connector plug in the tool flange of the robot. The votage can be 0,
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

def check_pose(pose):
    """Checks to make sure that a pose is valid.

    Checks that the pose is a 6 member tuple or list of floats. Does not return
    anything, simply raises exceptions if the pose is not valid.

    Args:
        pose: The pose to check

    Raises:
        TypeError: The pose was not valid.
    """
    if not isinstance(pose, (tuple,list)):
        raise TypeError("Expected tuple for pose")

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
    if not isinstance(pose, (tuple,list)):
        raise TypeError("Expected tuple for pose")

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