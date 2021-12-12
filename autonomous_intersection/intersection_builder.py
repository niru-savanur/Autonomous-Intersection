from autonomous_intersection.agents.visualcell import VisualCell


class IntersectionBuilder:
    @staticmethod
    def generate(width: float, height: float, road_width: float, side_width: float, line_width: float, model):
        yield VisualCell((0, 0), (width, height), model, color="green")
        x_pos = width / 2 - road_width / 2 - side_width / 2
        x_pos = [x_pos, x_pos + road_width + side_width]
        y_pos = height / 2 - road_width / 2 - side_width / 2
        y_pos = [y_pos, y_pos + road_width + side_width]
        yield VisualCell((x_pos[0], 0), (side_width, height), model, color="black")
        yield VisualCell((x_pos[1], 0), (side_width, height), model, color="black")
        yield VisualCell((0, y_pos[0]), (width, side_width), model, color="black")
        yield VisualCell((0, y_pos[1]), (width, side_width), model, color="black")

        yield VisualCell((x_pos[0] + side_width, 0), (road_width, height), model, color="gray")
        yield VisualCell((0, y_pos[0] + side_width), (width, road_width), model, color="gray")
        yield VisualCell((x_pos[0] + side_width + road_width / 2 - line_width / 2, 0),
                         (line_width, y_pos[0] + side_width), model, color="white")
        yield VisualCell((x_pos[0] + side_width + road_width / 2 - line_width / 2, y_pos[1]),
                         (line_width, width - y_pos[1]), model, color="white")

        yield VisualCell((0, y_pos[0] + side_width + road_width / 2 - line_width / 2),
                         (x_pos[0] + side_width, line_width), model, color="white")
        yield VisualCell((x_pos[1], y_pos[0] + side_width + road_width / 2 - line_width / 2),
                         (width - x_pos[1], line_width), model, color="white")
