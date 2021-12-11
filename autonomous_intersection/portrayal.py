from autonomous_intersection.agents.car import Car


def portrayCell(cell):
    assert cell is not None
    return get_json(cell.x, cell.y, cell.width, cell.height, color=cell.color, layer=cell.layer, shape=cell.shape, rotation=cell.rotation)


def get_json(x: int, y: int, w: int = 1, h: int = 1, color: str = "white", filled: bool = True, shape: str = "rect",
             layer: int = 0, rotation = 0):
    return {
        "Shape": shape,
        "w": w,
        "h": h,
        "Filled": filled,
        "Layer": layer,
        "x": x,
        "y": y,
        "Color": color,
        "rotation": rotation
    }
