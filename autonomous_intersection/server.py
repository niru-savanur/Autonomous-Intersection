from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.UserParam import UserSettableParameter

from .continuous_canvas import ContinuousCanvas
from .model import Intersection, Manager
from .portrayal import portrayCell
from .throughput_counter import ThroughputCounter

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
    ),
    "manager": UserSettableParameter(
        "choice",
        choices=[Manager.TrafficLight.name, Manager.BasicReservation.name, Manager.AdvancedReservation.name],
        value=Manager.TrafficLight.name
    )
}

server = ModularServer(
    Intersection, [canvas_element, ThroughputCounter()], "Autonomous Intersection", model_params
)
