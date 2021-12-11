import random

from mesa import Agent


class Car(Agent):
    def __init__(self, _id, pos, size, model, rotation=0, direction=(1, 0), color=None):
        super().__init__(_id, model)
        self.x, self.y = pos
        self.width, self.height = size
        self._nextState = None
        self.state = None
        self.color = color if color is not None else self.random_color()
        self.rotation = rotation
        self.velocity = 10
        self.dir = direction
        self._new_x = None
        self._new_y = None
        self.layer = 1
        self.shape = "rect"
        self.entry = direction

    @property
    def neighbors(self):
        return self.model.grid.neighbor_iter((self.x, self.y), True)

    def step(self):
        self._new_x = self.x + self.dir[0] * self.velocity
        self._new_y = self.y + self.dir[1] * self.velocity

    def advance(self):
        self.x = self._new_x
        self.y = self._new_y

    @staticmethod
    def random_color():
        return random.choice(["magenta", "purple", "violet", "green", "red", "black", "yellow", "blue"])
