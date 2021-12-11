from mesa.visualization.UserParam import UserSettableParameter
from mesa.visualization.ModularVisualization import ModularServer

from .continuous_canvas import ContinuousCanvas
from .portrayal import portrayCell
from .model import Intersection

canvas_element = ContinuousCanvas(portrayCell, 1000, 1000)

model_params = {
    "height": UserSettableParameter(
        "slider",
        "Height",
        1000,
        100,
        1000,
        1,
        description="Simulation height",
    ),
    "width": UserSettableParameter(
        "slider",
        "Width",
        1000,
        100,
        1000,
        1,
        description="Simulation width",
    ),
    "spawn_rate": UserSettableParameter(
        "slider",
        "Spawn rate",
        10,
        0,
        100,
        1,
        description="Car spawn rate",
    )
}

server = ModularServer(
    Intersection, [canvas_element], "Autonomous Intersection", model_params
)