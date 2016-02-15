"""Control sending and receiving of basic motion commands with a UR robot.

The module is designed to work with a CB2 robot running SW 1.8. This module
only gives access to higher level commands. Lower level commands can be
accessed through the cb2_send and cb2_receive modules.

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

import Queue
import socket
import time

import send.cb2_send as cb2_send
import receive.cb2_receive as cb2_receive


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
        radius: Float, the blend radius in m for bending moves. Note, a radius
            will result in inaccurate positioning and so the robot will never
            reach its goal.
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
    need to access those classes directly. The URRobot supports use by the
    with statement, and should be used as such, ex:
            with URRobot(host, port) as robot:
                Do stuff...

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
        """Destructor for the ur_cb2 class

        Specifically, this stops the threads in the receiver.
        """
        self.receiver.stop()
        self.__socket.close()

    def move_on_error(self, multiplier=None):
        """Moves the robot once the robot is within error of the next move.

        Args:
            multiplier (float): Defines how far the path should be set to
                overshoot, this can be useful for preventing deceleration
                between moves.
        Raises:
            ValueError: The error value is not valid.
        """
        if self.error <= self.current_goal.radius:
            raise ValueError('The error value must be greater than the radius')
        if (not self.goals.empty()) and (self.current_goal is not None):
                while not self.receiver.at_goal(
                        self.current_goal.pose,
                        self.current_goal.cartesian,
                        self.error):
                    time.sleep(self.sleep_time)
                if multiplier is None:
                    self.move_now()
                else:
                    self.move_now(multiplier)

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
        """Adds a goal to the robots movement queue

        Args:
            goal (Goal): The goal to add to the queue

        Raises:
            TypeError: A Goal was not passed in
        """
        if not isinstance(goal, Goal):
            raise TypeError('Requires the goal be of type Goal')
        self.goals.put(goal)

    def clear_goals(self):
        """Clears the goal queue.

        Allows a user to directly specify the next move.
        """
        with self.goals.mutex:
            self.goals.queue.clear()

    def at_goal(self):
        """Return whether the robot is at the goal

        Returns: Boolean, whether the robot is at its goal point
        """
        return self.receiver.at_goal(self.current_goal.pose,
                                     self.current_goal.cartesian)

    def is_stopped(self):
        """Return whether the robot is stopped.

        Returns: Boolean, whether the robot is stopped.
        """
        return self.receiver.is_stopped()

    def move_now(self, multiplier=None):
        """Moves the robot.

        Will immediately move the robot when called, cancelling out any other
        motions that may be in progress. The only caveat is that there is a
        time cost to this call in so far as that the TCP system can only send
        125 packets per second. If you call move_now too often, it will queue up
        calls and not move now.

        Args:
            multiplier (float): An optional multiplier on the path goal which
                will make the robot move past the goal to allow better
                blending of moves. It is ignored if None.
        """
        self.current_goal = self.goals.get()
        if multiplier is not None:
            with self.receiver.lock:
                current_position = tuple(
                    self.receiver.position if
                    self.current_goal.cartesian else
                    self.receiver.actual_joint_positions)
            move_goal = cb2_send.scale_path(current_position,
                                            self.current_goal.pose, multiplier)
        else:
            move_goal = self.current_goal.pose
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

    def __enter__(self):
        """Enters the URRobot from a with statement"""
        return self

    def __exit__(self, *_):
        """Exits at the end of a context manager statement by destructing."""
        self.__del__()
