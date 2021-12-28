from typing import Any, Tuple

from mesa import Model
from mesa.datacollection import DataCollector
from mesa.space import ContinuousSpace
from mesa.time import SimultaneousActivation

from autonomous_intersection.agents.direction import Direction
from autonomous_intersection.agents.visualcell import VisualCell
from autonomous_intersection.constants import PIXEL_PER_METER, STEPS_PER_SECOND
from autonomous_intersection.managers.reservation_manager import ReservationBasedManager
from autonomous_intersection.rect import Rect


class Intersection(Model):
    def __init__(self, height=1000, width=1000, spawn_rate=10, *args: Any, **parameters: Any):
        super().__init__(*args, **parameters)
        self.schedule = SimultaneousActivation(self)
        self.space = ContinuousSpace(height, width, False)
        self.width = width
        self.height = height
        self.road_width = 7 * PIXEL_PER_METER
        self.manager = ReservationBasedManager(self.width, self.height, self.road_width, parameters, self)
        self.build_background()
        self.agent_id = 0
        self.running = True
        self.spawn_rate = spawn_rate / 100
        self.car_height = int(1.5 * PIXEL_PER_METER)
        self.data_collector = DataCollector(model_reporters={"Throughput [cars / min]": self.get_agent_rate})

    def get_agent_id(self):
        self.agent_id += 1
        return self.agent_id

    def build_background(self):
        for cell in self.manager.build_background():
            self.space.place_agent(cell, (cell.x, cell.y))
            self.schedule.add(cell)

    def spawn_car(self, entry, width, height):
        cell = self.manager.create_new_car(entry, (width, height), self.get_agent_id())
        self.space.place_agent(cell, (cell.x, cell.y))
        self.schedule.add(cell)

    def add_new_agents(self):
        for entry in Direction:
            if not self.manager.is_entry_occupied(entry) and self.random.random() < self.spawn_rate:
                self.spawn_car(entry, *self.random_car_size(self.car_height))

    def random_car_size(self, height) -> Tuple[int, int]:
        return self.random.randint(round(height * 1.3), height * 2), height

    def step(self):
        self.add_new_agents()
        self.manager.remove_cars(self.space)
        self.manager.control_cars()
        self.schedule.step()
        self.data_collector.collect(self)

    def draw_debug_object(self, rect: Rect, color: str) -> VisualCell:
        cell = VisualCell((rect.left, rect.top), (rect.width, rect.height), self, color, 2)
        self.space.place_agent(cell, (cell.x, cell.y))
        self.schedule.add(cell)
        return cell

    def delete_debug_object(self, cell: VisualCell) -> None:
        self.space.remove_agent(cell)
        self.schedule.remove(cell)

    def get_agent_rate(self):
        if self.manager.first_step is None: return 0
        steps = self.manager.steps - self.manager.first_step + 1
        if steps < 50: return 0
        return ((STEPS_PER_SECOND * 60) * self.manager.agent_count) / steps
