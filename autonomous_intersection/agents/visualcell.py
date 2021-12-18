from mesa import Agent


class VisualCell(Agent):
    def __init__(self, pos, size, model, color="black", layer=-1, shape="simplerect"):
        super().__init__(self, model)
        self.x, self.y = pos
        self.width, self.height = size
        self.color = color
        self.layer = layer
        self.shape = shape
        self.rotation = 0

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
