import math
import random
from enum import Enum, auto
from math import cos, sin
from typing import Tuple

from mesa import Agent

from autonomous_intersection.rect import Rect


class Steer(Enum):
    Forward = auto()
    Left = auto()
    Right = auto()


class Car(Agent):
    ANGLE_RIGHT = 0
    ANGLE_LEFT = math.pi
    ANGLE_UP = -math.pi / 2
    ANGLE_DOWN = math.pi / 2
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)

    def __init__(self, _id, pos, size, model, rotation=0, color=None, velocity: int = 10):
        super().__init__(_id, model)
        self.x, self.y = pos
        self._new_x, self._new_y = pos
        self.width, self.height = size
        self._nextState = None
        self.state = None
        self.color = color if color is not None else self.random_color()
        self.shape = "rect"
        self.layer: int = 1

        self.direction: Tuple[float, float] = (1.0, 0.0)  # x and y parts of velocity, summed to 1
        self.rotation: float = 0.0  # angle in radians
        self.can_move: bool = True
        self.rotate(rotation)
        self.velocity: int = velocity
        self.entry: Tuple[float, float] = self.direction
        self.steer: Steer = Steer.Forward
        self.target_angle: float = self.rotation
        self.rotation_speed: float = 0.0

    def turn(self, steer: Steer, turn_length: int) -> None:
        """
        :param steer: left or right
        :param turn_length: distance between x or y coordinates at the start and the end of turn
        :return:
        """
        self.steer = steer
        arc_length = 0.5 * math.pi * turn_length
        if self.steer == Steer.Left:
            self.rotation_speed = -(math.pi / 2) / arc_length
            self.target_angle = self.rotation - math.pi / 2
        elif self.steer == Steer.Right:
            self.rotation_speed = (math.pi / 2) / arc_length
            self.target_angle = self.rotation + math.pi / 2
        elif self.steer == Steer.Forward:
            self.target_angle = self.rotation
            self.rotation_speed = 0

    @property
    def new_position(self):
        new_x = self.x + self.direction[0] * self.velocity
        new_y = self.y + self.direction[1] * self.velocity
        new_rotation = self.rotation + self.rotation_speed
        return new_x, new_y, new_rotation

    def step(self):
        if self.can_move:
            self._new_x, self._new_y, _ = self.new_position

    def advance(self):
        self.x = self._new_x
        self.y = self._new_y

    @staticmethod
    def random_color():
        return random.choice(
            ["magenta", "cyan", "lime", "purple", "violet", "green", "red", "black", "yellow", "blue", "white",
             "brown"])

    @property
    def rect(self) -> Rect:
        return Rect(self.x, self.y, self.width, self.height, self.rotation)

    @property
    def new_rect(self) -> Rect:
        next_ = self.new_position
        return Rect(next_[0], next_[1], self.width, self.height, next_[2])

    def rotate(self, angle):
        self.direction = self._get_new_direction(angle)
        self.rotation += angle

    def _get_new_direction(self, angle: float) -> Tuple[float, float]:
        new_x = self.direction[0] * cos(angle) - self.direction[1] * sin(angle)
        new_y = self.direction[0] * sin(angle) + self.direction[1] * cos(angle)
        return round(new_x), round(new_y)
