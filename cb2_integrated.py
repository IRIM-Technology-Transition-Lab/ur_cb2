import cb2_send
import cb2_receive
import Queue
import time
import socket


class Goal(object):
    def __init__(self, pose, cartesian, move_type, velocity=0.3,
                 acceleration=1.3, radius=0.0):
        self.pose = pose
        self.cartesian = cartesian
        if move_type not in ('linear', 'joint', 'process'):
            raise ValueError('move_type must be: linear, joint or process')
        self.move_type = move_type
        self.velocity = velocity
        self.acceleration = acceleration
        self.radius = radius


class URRobot(object):
    """A class to roll up all communication with a UR robot

    """
    sleep_time = 0.05

    def __init__(self, ip, port):
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__socket.connect((ip, port))
        self.receiver = cb2_receive.URReceiver(self.__socket, False)
        self.sender = cb2_send.URSender(self.__socket, False)
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
            time.sleep(.1)
            while not all(v == 0 for v in
                          self.receiver.target_joint_velocities):
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
