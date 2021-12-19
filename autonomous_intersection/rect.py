import math
from typing import Tuple


class Rect:
    def __init__(self, x, y, w, h, rotation=0.0):
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
        r1 = self._bounding_box()
        r2 = r2._bounding_box()
        return not (r2.left > r1.right or r2.right < r1.left or r2.top > r1.bottom or r2.bottom < r1.top)

    def __eq__(self, other):
        return (self.width == other.width and self.height == other.height
                and self.left == other.top and self.right == other.right and self.rotation == other.rotation)

    @property
    def center(self) -> Tuple[float, float]:
        if self.rotation == 0:
            return self._center_without_rotation
        return self._bounding_box().center

    @property
    def _center_without_rotation(self):
        return self.left + self.width / 2, self.top + self.height / 2

    def __str__(self):
        return str(self._get_points())

    def __repr__(self):
        return self.__str__()

    def _get_points(self):
        points = [(self.left, self.top), (self.right, self.top), (self.right, self.bottom), (self.left, self.bottom)]
        return list(map(lambda x: self._rotate(self._center_without_rotation, x, self.rotation), points))

    def _bounding_box(self):
        if math.isclose(self.rotation, math.pi, abs_tol=0.01) or math.isclose(self.rotation, 0, abs_tol=0.01):
            return Rect(self.left, self.top, self.width, self.height, 0)
        if math.isclose(self.rotation % (math.pi / 2), 0, abs_tol=0.01):
            center = self._center_without_rotation
            return Rect(center[0] - self.height / 2, center[1] - self.width / 2, self.height, self.width)
        x_coordinates, y_coordinates = zip(*self._get_points())
        mx = min(x_coordinates)
        my = min(y_coordinates)
        return Rect(mx, my, max(x_coordinates) - mx, max(y_coordinates) - my, 0)

    @staticmethod
    def _rotate(origin, point, angle):
        ox, oy = origin
        px, py = point

        qx = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
        qy = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)
        return qx, qy
