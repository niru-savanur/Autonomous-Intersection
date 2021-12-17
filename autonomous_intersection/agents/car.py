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

    def __init__(self, _id, pos, size, model, rotation=0, target: Tuple[int, int] = RIGHT, color=None,
                 velocity: int = 10):
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
        self.rotate_right_angle(rotation)
        self.velocity: int = velocity
        self.entry: Tuple[float, float] = self.direction
        self.target = target
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
        turn = self.rotation_speed * self.velocity
        new_rotation = self.rotation + turn
        if self.steer == Steer.Right and new_rotation > self.target_angle:
            new_rotation = self.target_angle
            turn = new_rotation - self.rotation
        elif self.steer == Steer.Left and new_rotation < self.target_angle:
            new_rotation = self.target_angle
            turn = new_rotation - self.rotation

        new_direction = self._get_new_direction(turn)
        new_x = self.x + new_direction[0] * self.velocity
        new_y = self.y + new_direction[1] * self.velocity
        return new_x, new_y, new_rotation

    def step(self):
        if self.can_move:
            self._new_x, self._new_y, rotation = self.new_position
            self.rotate(rotation - self.rotation)
            if rotation == self.target_angle:
                self.steer = Steer.Forward
                self.rotation_speed = 0.0

    def advance(self):
        self.x = self._new_x
        self.y = self._new_y

    @property
    def steer_direction(self) -> Steer:
        if (self.entry, self.target) in (
                (self.ANGLE_RIGHT, self.RIGHT), (self.ANGLE_UP, self.UP), (self.ANGLE_DOWN, self.DOWN),
                (self.ANGLE_LEFT, self.LEFT)):
            return Steer.Forward
        if (self.entry, self.target) in (
                (self.ANGLE_RIGHT, self.DOWN), (self.ANGLE_UP, self.RIGHT), (self.ANGLE_DOWN, self.LEFT),
                (self.ANGLE_LEFT, self.UP)):
            return Steer.Right
        return Steer.Left

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

    def rotate_right_angle(self, angle):
        self.direction = self._get_new_right_angle_direction(angle)
        self.rotation += angle

    def _get_new_direction(self, angle: float) -> Tuple[float, float]:
        new_x = self.direction[0] * cos(angle) - self.direction[1] * sin(angle)
        new_y = self.direction[0] * sin(angle) + self.direction[1] * cos(angle)
        return new_x, new_y

    def _get_new_right_angle_direction(self, angle: float) -> Tuple[float, float]:
        new_x = self.direction[0] * cos(angle) - self.direction[1] * sin(angle)
        new_y = self.direction[0] * sin(angle) + self.direction[1] * cos(angle)
        return round(new_x), round(new_y)
