import math
import random
from dataclasses import dataclass
from math import cos, sin
from typing import Tuple

from mesa import Agent

from autonomous_intersection.agents.direction import Direction, Steer
from autonomous_intersection.line import Line
from autonomous_intersection.rect import Rect


class Car(Agent):
    @dataclass
    class State:
        x: int
        y: int
        rotation: float
        velocity: int
        direction: Tuple[float, float]
        rotation_speed: float
        can_move: bool
        steer: Steer
        target_angle: float

    def __init__(self, _id, model, start_line: Line, target_line: Line, position, size,
                 initial_direction: Direction = Direction.Left, target: Direction = Direction.Right, color=None,
                 velocity: int = 10):
        super().__init__(_id, model)
        self.width, self.height = size
        self.color = color if color is not None else self.random_color()
        self.shape = "rect"
        self.layer: int = 1
        self.filled = True

        self.start_line: Line = start_line
        self.target_line = target_line
        direction, rotation = self.rotate_right_angle(0.0, initial_direction.angle, Direction.Right.velocity)
        self.state = Car.State(
            *position,
            rotation=rotation,
            velocity=velocity,
            direction=direction,
            rotation_speed=0.0,
            can_move=True,
            steer=Steer.Forward,
            target_angle=rotation,
        )
        self.initial_direction: Direction = initial_direction
        self.target: Direction = target

    def turn(self, steer: Steer, turn_length: int) -> None:
        """
        :param steer: left or right
        :param turn_length: distance between x or y coordinates at the start and the end of turn
        :return:
        """
        self.state.steer = steer
        arc_length = 0.5 * math.pi * turn_length
        if self.state.steer == Steer.Left:
            self.state.rotation_speed = -(math.pi / 2) / arc_length
            self.state.target_angle = self.state.rotation - math.pi / 2
        elif self.state.steer == Steer.Right:
            self.state.rotation_speed = (math.pi / 2) / arc_length
            self.state.target_angle = self.state.rotation + math.pi / 2
        elif self.state.steer == Steer.Forward:
            self.state.target_angle = self.state.rotation
            self.state.rotation_speed = 0

    def new_position(self):
        turn = self.state.rotation_speed * self.state.velocity
        new_rotation = self.state.rotation + turn
        if self.state.steer == Steer.Right and new_rotation > self.state.target_angle:
            new_rotation = self.state.target_angle
            turn = new_rotation - self.state.rotation
        elif self.state.steer == Steer.Left and new_rotation < self.state.target_angle:
            new_rotation = self.state.target_angle
            turn = new_rotation - self.state.rotation

        if turn == 0:
            new_x = self.state.x + self.state.direction[0] * self.state.velocity
            new_y = self.state.y + self.state.direction[1] * self.state.velocity
            return new_x, new_y, self.state.rotation

        new_x = self.state.x
        new_y = self.state.y
        new_direction = self.state.direction
        for step in range(self.state.velocity):
            new_direction = self._get_new_direction(new_direction, turn / self.state.velocity)
            new_x += new_direction[0]
            new_y += new_direction[1]
        return new_x, new_y, new_rotation

    def step(self):
        if self.state.can_move:
            self.state.x, self.state.y, rotation = self.new_position()
            self.rotate(rotation - self.state.rotation)
            if rotation == self.state.target_angle:
                self.state.steer = Steer.Forward
                self.state.rotation_speed = 0.0

    @staticmethod
    def random_color():
        return random.choice(["magenta", "cyan", "lime", "purple", "violet", "green", "red", "black", "yellow",
                              "blue", "white", "brown"])

    def rotate(self, angle):
        self.state.direction = self._get_new_direction(self.state.direction, angle)
        self.state.rotation += angle

    def rotate_right_angle(self, rotation: float, angle: float, direction: Tuple[float, float]
                           ) -> Tuple[Tuple[float, float], float]:
        """
        :return: new direction and rotation
        """
        return self._get_new_right_angle_direction(direction, angle), rotation + angle

    @staticmethod
    def _get_new_direction(current: Tuple[float, float], angle: float) -> Tuple[float, float]:
        new_x = current[0] * cos(angle) - current[1] * sin(angle)
        new_y = current[0] * sin(angle) + current[1] * cos(angle)
        return new_x, new_y

    @staticmethod
    def _get_new_right_angle_direction(direction: Tuple[float, float], angle: float) -> Tuple[float, float]:
        new_x = direction[0] * cos(angle) - direction[1] * sin(angle)
        new_y = direction[0] * sin(angle) + direction[1] * cos(angle)
        return round(new_x), round(new_y)

    @property
    def x(self):
        return self.state.x

    @property
    def y(self):
        return self.state.y

    @property
    def rotation(self):
        return self.state.rotation

    @property
    def rect(self) -> Rect:
        return Rect(self.state.x - self.width // 2, self.state.y - self.height // 2, self.width, self.height,
                    self.state.rotation)

    @property
    def new_rect(self) -> Rect:
        next_ = self.new_position()
        return Rect(next_[0] - self.width // 2, next_[1] - self.height // 2, self.width, self.height, next_[2])

    @property
    def steer_direction(self) -> Steer:
        if self.initial_direction == self.target:
            return Steer.Forward
        if (self.initial_direction, self.target) in (
                (Direction.Right, Direction.Down), (Direction.Up, Direction.Right), (Direction.Down, Direction.Left),
                (Direction.Left, Direction.Up)):
            return Steer.Right
        return Steer.Left
