import math
import random
from math import cos, sin

from mesa import Agent

from autonomous_intersection.rect import Rect


class Car(Agent):
    ANGLE_RIGHT = 0
    ANGLE_LEFT = math.pi
    ANGLE_UP = -math.pi / 2
    ANGLE_DOWN = math.pi / 2
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)

    def __init__(self, _id, pos, size, model, rotation=0, color=None):
        super().__init__(_id, model)
        self.x, self.y = pos
        self.width, self.height = size
        self._nextState = None
        self.state = None
        self.color = color if color is not None else self.random_color()
        self.rotation = rotation
        self.velocity = 10
        self.direction = (1, 0)
        self.rotate(self.rotation)
        self._new_x = self.x
        self._new_y = self.y
        self.layer = 1
        self.shape = "rect"
        self.entry = self.direction
        self.can_move = True

    @property
    def neighbors(self):
        return self.model.grid.neighbor_iter((self.x, self.y), True)

    @property
    def new_position(self):
        return self.x + self.direction[0] * self.velocity, self.y + self.direction[1] * self.velocity

    def step(self):
        if self.can_move:
            self._new_x, self._new_y = self.new_position

    def advance(self):
        self.x = self._new_x
        self.y = self._new_y

    @staticmethod
    def random_color():
        return random.choice(["magenta", "purple", "violet", "green", "red", "black", "yellow", "blue"])

    @property
    def rect(self) -> Rect:
        return Rect(self.x, self.y, self.width, self.height, self.rotation)

    @property
    def new_rect(self) -> Rect:
        next_ = self.new_position
        return Rect(next_[0], next_[1], self.width, self.height, self.rotation)

    def rotate(self, angle):
        new_x = self.direction[0] * cos(angle) - self.direction[1] * sin(angle)
        new_y = self.direction[0] * sin(angle) + self.direction[1] * cos(angle)
        self.direction = (round(new_x), round(new_y))
