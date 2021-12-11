from mesa import Agent


class VisualCell(Agent):
    def __init__(self, pos, size, model, color="black", layer=0, shape="simplerect"):
        super().__init__(pos, model)
        self.x, self.y = pos
        self.width, self.height = size
        self.color = color
        self.layer = layer
        self.shape = shape
        self.rotation = 0

    @property
    def neighbors(self):
        return self.model.grid.neighbor_iter((self.x, self.y), True)

    def step(self):
        """
        Purely visual, do nothing
        """
        pass

    def advance(self):
        """
        Purely visual, do nothing
        """
        pass
