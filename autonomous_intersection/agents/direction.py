import math
from collections import namedtuple
from enum import Enum, auto
from typing import Tuple


class Steer(Enum):
    Forward = auto()
    Left = auto()
    Right = auto()


DirectionData = namedtuple("DirectionData", ["angle", "velocity"])


class Direction(Enum):
    Up = DirectionData(angle=-math.pi / 2, velocity=(0, -1))
    Down = DirectionData(angle=math.pi / 2, velocity=(0, 1))
    Left = DirectionData(angle=math.pi, velocity=(-1, 0))
    Right = DirectionData(angle=0.0, velocity=(1, 0))

    @property
    def velocity(self) -> Tuple[int, int]:
        return self.value.velocity

    @property
    def angle(self) -> float:
        return self.value.angle

    @property
    def reverse(self):
        if self == Direction.Up: return Direction.Down
        if self == Direction.Down: return Direction.Up
        if self == Direction.Left: return Direction.Right
        return Direction.Left

    def turned(self, steer: Steer):
        if steer == Steer.Forward:
            return self
        if self == Direction.Down:
            return Direction.Left if steer == Steer.Right else Direction.Right
        if self == Direction.Up:
            return Direction.Right if steer == Steer.Right else Direction.Left
        if self == Direction.Left:
            return Direction.Up if steer == Steer.Right else Direction.Down
        if self == Direction.Right:
            return Direction.Down if steer == Steer.Right else Direction.Up
