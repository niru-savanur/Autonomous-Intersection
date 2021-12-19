import math
import random
from dataclasses import dataclass, replace
from math import cos, sin
from typing import Tuple

from mesa import Agent

from autonomous_intersection.agents.direction import Direction, Steer
from autonomous_intersection.line import Line, Axis
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
        needs_turn: bool

        def copy(self): return replace(self)

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
        direction, rotation = self.rotate_by_right_angle(0.0, initial_direction.angle, Direction.Right.velocity)
        self.state = Car.State(
            *position,
            rotation=rotation,
            velocity=velocity,
            direction=direction,
            rotation_speed=0.0,
            can_move=True,
            steer=Steer.Forward,
            target_angle=rotation,
            needs_turn=initial_direction != target
        )
        self.initial_direction: Direction = initial_direction
        self.target: Direction = target

    @staticmethod
    def turn(state: State, steer: Steer, turn_length: int) -> State:
        """
        :param state: state to modify
        :param steer: left or right
        :param turn_length: distance between x or y coordinates at the start and the end of turn
        :return: updated state
        """
        state.steer = steer
        arc_length = 0.5 * math.pi * turn_length
        if state.steer == Steer.Left:
            state.rotation_speed = -(math.pi / 2) / arc_length
            state.target_angle = state.rotation - math.pi / 2
        elif state.steer == Steer.Right:
            state.rotation_speed = (math.pi / 2) / arc_length
            state.target_angle = state.rotation + math.pi / 2
        elif state.steer == Steer.Forward:
            state.target_angle = state.rotation
            state.rotation_speed = 0
        state.needs_turn = False
        return state

    def should_turn(self, next_state: State) -> bool:
        if not next_state.needs_turn: return False
        distance = self.distance_from_target_line(next_state)
        return 2 * self.width > distance

    def next_step(self, state: State = None) -> State:
        state = state.copy() if state is not None else self.state.copy()
        turn = state.rotation_speed * state.velocity
        if turn == 0:
            state.x += state.direction[0] * state.velocity
            state.y += state.direction[1] * state.velocity
            return state

        new_rotation = state.rotation + turn

        if (state.steer == Steer.Right and new_rotation > state.target_angle) or (
                state.steer == Steer.Left and new_rotation < state.target_angle):
            new_rotation = state.target_angle
            turn = new_rotation - state.rotation
            state.rotation_speed = 0
            state.steer = Steer.Forward

        new_x, new_y = state.x, state.y
        new_direction = state.direction
        for step in range(state.velocity):
            new_direction = self._get_new_direction(new_direction, turn / state.velocity)
            new_x += new_direction[0]
            new_y += new_direction[1]
        self.rotate(state, turn)
        state.x, state.y = new_x, new_y
        return state

    def step(self):
        if self.state.can_move:
            new_state = self.next_step()
            if self.should_turn(new_state):
                self.turn(new_state, self.steer_direction, self.distance_from_target_line(new_state))
            self.state = new_state

    def rotate(self, state: State, angle: float):
        state.direction = self._get_new_direction(state.direction, angle)
        state.rotation += angle

    def distance_from_target_line(self, state: State):
        if self.start_line.axis == Axis.Horizontal:
            return abs(state.x - self.target_line.position)
        return abs(state.y - self.target_line.position)

    def rotate_by_right_angle(self, rotation: float, angle: float, direction: Tuple[float, float]
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
        new_x, new_y = Car._get_new_direction(direction, angle)
        return round(new_x), round(new_y)

    @staticmethod
    def random_color():
        return random.choice(["magenta", "cyan", "lime", "purple", "violet", "green", "red", "black", "yellow",
                              "blue", "white", "brown"])

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
        next_ = self.next_step()
        return Rect(next_.x - self.width // 2, next_.y - self.height // 2, self.width, self.height, next_.rotation)

    @property
    def steer_direction(self) -> Steer:
        if self.initial_direction == self.target:
            return Steer.Forward
        if (self.initial_direction, self.target) in (
                (Direction.Right, Direction.Down), (Direction.Up, Direction.Right), (Direction.Down, Direction.Left),
                (Direction.Left, Direction.Up)):
            return Steer.Right
        return Steer.Left
