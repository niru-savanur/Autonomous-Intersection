from mesa.visualization.UserParam import UserSettableParameter
from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer

from .portrayal import portrayCell
from .model import ConwaysGameOfLife

# Make a world that is 50x50, on a 250x250 display.
canvas_element = CanvasGrid(portrayCell, grid_width=200, grid_height=200, canvas_width=1000, canvas_height=1000)

model_params = {
    "height": UserSettableParameter(
        "slider",
        "Height",
        10,
        10,
        100,
        1,
        description="Simulation height",
    ),
    "width": UserSettableParameter(
        "slider",
        "Width",
        10,
        10,
        200,
        1,
        description="Simulation width",
    )
}

server = ModularServer(
    ConwaysGameOfLife, [canvas_element], "Game of Life", model_params
)
