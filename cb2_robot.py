"""Control sending and receiving of basic motion commands with a UR robot.

The module is designed to work with a CB2 robot running SW 1.8. This module
only gives access to higher level commands. Lower level commands can be
accessed through the cb2_send and cb2_receive modules.
"""

import cb2_send
import cb2_receive
import Queue
import time
import socket


class Goal(object):
    """Holds movement goals

    Attributes:
        pose: A 6 float tuple or list describing the desired robot pose in
            either joint or cartesian coordinates
        cartesian: A boolean describing whether the pose is in joint (False) or
            cartesian (True) space
        move_type: A string describing the movement type. Valid values are:
            'linear', 'joint', 'process'
        velocity: Float, the desired velocity for the specified move. For
            linear and process this is in m/s, for joint this is in rad/s
        acceleration: Float, the desired velocity for the specified move. For
            linear and process this is in m/s^2, for joint this is in rad/s^2
        radius: Float, the blend radius in m for moves. Appears to only have
            an effect on process moves
    """

    def __init__(self, pose, cartesian, move_type, velocity=0.3,
                 acceleration=1.3, radius=0.0):
        """Create a goal object.

        Args:
            pose (6 float tuple or list): Describe the desired robot pose in
                either joint or cartesian coordinates
            cartesian (boolean): Describe whether the pose is in joint (False)
                or cartesian (True) space
            move_type (string): Describe the movement type. Valid values are:
                'linear', 'joint', 'process'
            velocity (float): The desired velocity for the specified move. For
                linear and process this is in m/s, for joint this is in rad/s
            acceleration (float): The desired velocity for the specified move.
                For linear and process this is in m/s^2, for joint this is in
                rad/s^2
            radius (float): The radius to use for bends. Note, a radius will
                result in inaccurate positioning and so the robot will never
                reach its goal.

        Raises:
            ValueError: The move type was not a valid value ('linear', 'joint',
                'process')
        """
        self.pose = pose
        self.cartesian = cartesian
        if move_type not in ('linear', 'joint', 'process'):
            raise ValueError('move_type must be: linear, joint or process')
        self.move_type = move_type
        self.velocity = velocity
        self.acceleration = acceleration
        self.radius = radius


class URRobot(object):
    """A class to roll up all communication with a UR robot.

    Exposes some of the most commonly used commands made available by
    cb2_send and cb2_receive. To get full access to all commands, you will
    need to access those classes directly.

    Attributes:
        __socket: socket.socket which is used to communicate with the robot
        receiver: cb2_receive.URReceiver which receives data from the robot
            on a separate thread
        sender: cb2_send.URSender which sends commands to the robot
        error: Float which defines the error around a point from which it is
            acceptable to move to the next point.
        goals: Queue.Queue of Goal objects defining movement goals
        current_goal: Goal, the current movement goal.
    """
    sleep_time = 0.001

    def __init__(self, ip, port, verbose=False):
        """Construct a UR Robot connection to send commands

        Args:
            ip (str): The IP address to find the Robot
            port (int): The port to connect to on the robot (
                3001:primary client,
                3002:secondary client,
                3003: real time client)
            verbose (bool): Whether to print information to the terminal
        """
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__socket.connect((ip, port))
        self.receiver = cb2_receive.URReceiver(self.__socket, verbose)
        self.sender = cb2_send.URSender(self.__socket, verbose)
        self.error = 0.0
        self.goals = Queue.Queue()
        self.receiver.start()
        self.current_goal = None

    def __del__(self):
        """Destructor for the cb2_robot class

        Specifically, this stops the threads in the receiver.
        """
        self.receiver.stop()

    def move_on_error(self, multiplier=None):
        if self.error <= 0.0:
            raise ValueError('The error value must be greater than zero')
        if (not self.goals.empty()) and (self.current_goal is not None):
                while not self.receiver.at_goal(
                        self.current_goal.pose,
                        self.current_goal.cartesian,
                        self.error):
                    time.sleep(self.sleep_time)
                if multiplier is None:
                    self.move_now()
                else:
                    self.move_multiple(multiplier)

    def move_on_stop(self):
        """Moves once the robot stops.

        Note, the robot can be stopped both at the beginning and end of its
        path, therefore, this function also checks whether the robot is at
        its current goal.
        """
        if not self.goals.empty():
            while not (self.receiver.is_stopped() and (
                       self.current_goal is None or
                       self.receiver.at_goal(self.current_goal.pose,
                                              self.current_goal.cartesian,
                                             0.01))):
                time.sleep(self.sleep_time)
            self.move_now()

    def add_goal(self, goal):
        if not isinstance(goal, Goal):
            raise TypeError('Requires the goal be of type Goal')
        self.goals.put(goal)

    def clear_goals(self):
        with self.goals.mutex:
            self.goals.queue.clear()

    def move_now(self):
        self.current_goal = self.goals.get()
        self.sender.radius = self.current_goal.radius

        if self.current_goal.move_type == 'joint':
            self.sender.a_joint = self.current_goal.acceleration
            self.sender.v_joint = self.current_goal.velocity
        else:
            self.sender.a_tool = self.current_goal.acceleration
            self.sender.v_tool = self.current_goal.velocity

        if self.current_goal.move_type == 'joint':
            self.sender.move_joint(self.current_goal.pose,
                                   cartesian=self.current_goal.cartesian)
        if self.current_goal.move_type == 'linear':
            self.sender.move_line(self.current_goal.pose,
                                  cartesian=self.current_goal.cartesian)
        if self.current_goal.move_type == 'process':
            self.sender.move_process(self.current_goal.pose,
                                     cartesian=self.current_goal.cartesian)

    def at_goal(self):
        return self.receiver.at_goal(self.current_goal.pose,
                                     self.current_goal.cartesian)

    def is_stopped(self):
        return self.receiver.is_stopped()

    def move_multiple(self, multiplier=2):
        self.current_goal = self.goals.get()
        with self.receiver.lock:
            current_position = (
                self.receiver.position if
                self.current_goal.cartesian else
                self.receiver.actual_joint_positions)
        move_goal = cb2_send.scale_path(current_position,
                                        self.current_goal.pose, multiplier)
        self.sender.radius = self.current_goal.radius

        if self.current_goal.move_type == 'joint':
            self.sender.a_joint = self.current_goal.acceleration
            self.sender.v_joint = self.current_goal.velocity
        else:
            self.sender.a_tool = self.current_goal.acceleration
            self.sender.v_tool = self.current_goal.velocity

        if self.current_goal.move_type == 'joint':
            self.sender.move_joint(move_goal,
                                   cartesian=self.current_goal.cartesian)
        if self.current_goal.move_type == 'linear':
            self.sender.move_line(move_goal,
                                  cartesian=self.current_goal.cartesian)
        if self.current_goal.move_type == 'process':
            self.sender.move_process(move_goal,
                                     cartesian=self.current_goal.cartesian)