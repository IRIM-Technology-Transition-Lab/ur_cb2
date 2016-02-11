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
    """

    def __init__(self, pose, cartesian, move_type, velocity=0.3,
                 acceleration=1.3):
        """Creates an instance fo the cb2_robot class

        Args:
            pose:
            cartesian:
            move_type:
            velocity:
            acceleration:

        Returns:

        """
        self.pose = pose
        self.cartesian = cartesian
        if move_type not in ('linear', 'joint', 'process'):
            raise ValueError('move_type must be: linear, joint or process')
        self.move_type = move_type
        self.velocity = velocity
        self.acceleration = acceleration


class URRobot(object):
    """A class to roll up all communication with a UR robot

    Attributes:
        ip_address: String representing the IPv4 address of the target robot
        port: Integer of the port to connect to on the robot (
            3001:primary client,
            3002:secondary client,
            3003: real time client)

    """
    sleep_time = 0.05

    def __init__(self, ip, port, verbose=False):
        """Construct a UR Robot connection to send commands

        Args:
            ip (str): The IP address to find the Robot
            port (int): The port to connect to on the robot (
                3001:primary client, 3002:secondary client,
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
        self.receiver.stop()

    def move_on_error(self):
        if not self.current_goal.cartesian:
            raise StandardError('Must be dealing with cartesian coordinates '
                                'to do a move on error')
        if not self.goals.empty():
            if self.current_goal is not None:
                error = True
                while error:
                    error = False
                    current_pos = list(self.receiver.position)
                    for i in range(0, 3):
                        error = (True if abs(self.current_goal[i] -
                                             current_pos[i]) > self.error else
                                 error)
                    time.sleep(self.sleep_time)
            self.move_now()

    def move_on_stop(self):
        if not self.goals.empty():
            while not (self.receiver.is_stopped() and self.receiver.at_goal(
                    self.current_goal.pose,self.current_goal.cartesian)):
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
