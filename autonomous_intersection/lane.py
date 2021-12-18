from autonomous_intersection.line import Axis, Line
from autonomous_intersection.rect import Rect


class Lane:
    def __init__(self, bounds: Rect):
        self.bounds = bounds
        if bounds.width > bounds.height:
            self.axis = Axis.Horizontal
            self.line = Line.H(round(bounds.center[1]))
        else:
            self.axis = Axis.Vertical
            self.line = Line.V(round(bounds.center[0]))
