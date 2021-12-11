import math
from typing import Tuple


class Rect:
    def __init__(self, x, y, w, h, rotation):
        self.left = x
        self.top = y
        self.width = w
        self.height = h
        self.rotation = rotation

    @property
    def bottom(self):
        return self.top + self.height

    @property
    def right(self):
        return self.left + self.width

    def __contains__(self, r2: "Rect") -> bool:
        r1 = self.apply_rotation()
        r2 = r2.apply_rotation()
        return not (r2.left > r1.right or r2.right < r1.left or r2.top > r1.bottom or r2.bottom < r1.top)

    def apply_rotation(self) -> "Rect":
        if self.rotation == math.pi / 2:
            return Rect(self.center[0] - self.height / 2, self.center[1] - self.width / 2, self.height, self.width, 0)
        return Rect(self.left, self.top, self.width, self.height, self.rotation)

    def __eq__(self, other):
        return (self.width == other.width and self.height == other.height
                and self.left == other.top and self.right == other.right and self.rotation == other.rotation)

    @property
    def center(self) -> Tuple[float, float]:
        return self.left + self.width / 2, self.top + self.height / 2

    def __str__(self):
        rect = self.apply_rotation()
        return f"({rect.left}, {rect.top}, {rect.right}, {rect.bottom})"

    def __repr__(self):
        return self.__str__()
