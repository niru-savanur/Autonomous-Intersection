from mesa.visualization.UserParam import UserSettableParameter
from mesa.visualization.ModularVisualization import ModularServer

from .continuous_canvas import ContinuousCanvas
from .portrayal import portrayCell
from .model import Intersection

canvas_element = ContinuousCanvas(portrayCell, 1000, 1000)

model_params = {
    "spawn_rate": UserSettableParameter(
        "slider",
        "Spawn rate",
        10,
        0,
        100,
        1,
        description="Car spawn rate",
    ),
    "velocity": UserSettableParameter(
        "slider",
        "Car velocity",
        10,
        1,
        30,
        1,
        description="Car velocity",
    ),
}

server = ModularServer(
    Intersection, [canvas_element], "Autonomous Intersection", model_params
)
