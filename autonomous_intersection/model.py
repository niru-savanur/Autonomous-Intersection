from typing import Any

from mesa import Model
from mesa.space import ContinuousSpace
from mesa.time import SimultaneousActivation

from autonomous_intersection.agents.car import Car
from autonomous_intersection.intersection_manager import IntersectionManager


class Intersection(Model):
    def __init__(self, height=1000, width=1000, spawn_rate=10, velocity: int = 10, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.schedule = SimultaneousActivation(self)
        self.space = ContinuousSpace(height, width, False)
        self.width = width
        self.height = height
        self.manager = IntersectionManager(self.width, self.height, 100, velocity)
        self.build_background()
        self.agent_id = 0
        self.running = True
        self.spawn_rate = spawn_rate / 100

    def get_agent_id(self):
        self.agent_id += 1
        return self.agent_id

    def build_background(self):
        for cell in self.manager.build_background():
            self.space.place_agent(cell, (cell.x, cell.y))
            self.schedule.add(cell)

    def spawn_car(self, entry, width, height):
        cell = self.manager.create_new_car(entry, width, height, self.get_agent_id(), self)
        self.space.place_agent(cell, (cell.x, cell.y))
        self.schedule.add(cell)

    def add_new_agents(self):
        for entry in (Car.LEFT, ):  # (Car.UP, Car.DOWN, Car.RIGHT, Car.LEFT):
            if not self.manager.is_entry_occupied(entry) and self.random.random() < self.spawn_rate:
                self.spawn_car(entry, 50, 30)

    def step(self):
        self.schedule.step()
        self.add_new_agents()
        self.manager.remove_cars(self.space)
        self.manager.control_cars()
