from dataclasses import dataclass
from enum import Enum, auto

from autonomous_intersection.rect import Rect


class Axis(Enum):
    Horizontal = auto()
    Vertical = auto()


@dataclass
class Line:
    position: int
    axis: Axis

    @staticmethod
    def H(pos: int): return Line(pos, Axis.Horizontal)

    @staticmethod
    def V(pos: int): return Line(pos, Axis.Vertical)

    @property
    def bounds(self):
        if self.axis == Axis.Horizontal:
            return Rect(0, self.position, 100000, 1)
        return Rect(self.position, 0, 1, 10000)
