from mesa.visualization.UserParam import UserSettableParameter
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import ChartModule

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
        "Car velocity [km/h]",
        40,
        10,
        60,
        1,
        description="Car maximum velocity",
    ),
    "acceleration": UserSettableParameter(
        "slider",
        "Car acceleration [km/h per second]",
        30,
        10,
        60,
        1,
        description="Car acceleration",
    )
}

chart = ChartModule([{"Label": "Throughput [cars / min]",
                      "Color": "Black"}],
                    data_collector_name='data_collector')

server = ModularServer(
    Intersection, [canvas_element, chart], "Autonomous Intersection", model_params
)
