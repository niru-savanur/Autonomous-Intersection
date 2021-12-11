from typing import Union

from autonomous_intersection.agents.car import Car
from autonomous_intersection.agents.visualcell import VisualCell


def portrayCell(cell: Union[Car, VisualCell]):
    assert cell is not None
    return {
        "Shape": cell.shape,
        "w": cell.width,
        "h": cell.height,
        "Filled": True,
        "Layer": cell.layer,
        "x": cell.x,
        "y": cell.y,
        "Color": cell.color,
        "rotation": cell.rotation
    }
