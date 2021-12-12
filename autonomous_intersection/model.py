from typing import Any

from mesa import Model
from mesa.space import ContinuousSpace
from mesa.time import SimultaneousActivation

from autonomous_intersection.agents.car import Car
from autonomous_intersection.intersection_builder import IntersectionBuilder
from autonomous_intersection.rect import Rect


class Intersection(Model):
    def __init__(self, height=1000, width=1000, spawn_rate=10, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.schedule = SimultaneousActivation(self)
        self.space = ContinuousSpace(height, width, False)
        self.width = width
        self.height = height
        self.road_width = 100
        self.cars = {}

        self.build_background()
        self.agent_id = 0

        self.running = True
        self.spawn_rate = spawn_rate / 100
        self.intersection = self.get_intersection_rect()

    def get_intersection_rect(self) -> Rect:
        return Rect(self.width / 2 - self.road_width / 2, self.height / 2 - self.road_width / 2, self.road_width,
                    self.road_width, 0)

    def get_agent_id(self):
        self.agent_id += 1
        return self.agent_id

    def build_background(self):
        for cell in IntersectionBuilder.generate(self.width, self.height, self.road_width, 10, 4, self):
            self.space.place_agent(cell, (cell.x, cell.y))
            self.schedule.add(cell)

    def spawn_car(self, entry, width, height):
        if entry == Car.UP:
            cell = Car(self.get_agent_id(),
                       (self.width / 2 + self.road_width / 4 - height / 2, self.height - width),
                       (width, height), self, Car.ANGLE_UP)
        elif entry == Car.DOWN:
            cell = Car(self.get_agent_id(),
                       (self.width / 2 - self.road_width / 4 - height / 2, 0),
                       (width, height), self, Car.ANGLE_DOWN)
        elif entry == Car.LEFT:
            cell = Car(self.get_agent_id(),
                       (self.width - width, self.height / 2 - self.road_width / 4 - height / 2),
                       (width, height), self, Car.ANGLE_LEFT)
        elif entry == Car.RIGHT:
            cell = Car(self.get_agent_id(),
                       (0, self.height / 2 + self.road_width / 4 - height / 2),
                       (width, height), self, Car.ANGLE_RIGHT)

        self.space.place_agent(cell, (cell.x, cell.y))
        self.schedule.add(cell)
        self.cars[cell.unique_id] = cell

    def is_car_out_of_bounds(self, car: Car):
        if car.x + car.width < 0:
            return True
        if car.x > self.width:
            return True
        if car.y + car.height < 0:
            return True
        if car.y > self.height:
            return True
        return False

    def remove_cars(self):
        to_delete = set()
        for car in filter(self.is_car_out_of_bounds, self.cars.values()):
            self.space.remove_agent(car)
            to_delete.add(car)

        for car in to_delete:
            del self.cars[car.unique_id]

    def is_entry_occupied(self, entry: float) -> bool:
        if entry == Car.UP:
            return any(car for car in self.cars.values() if car.entry == entry and car.y > self.height - car.width * 3)
        elif entry == Car.DOWN:
            return any(car for car in self.cars.values() if car.entry == entry and car.y < car.height * 3)
        elif entry == Car.RIGHT:
            return any(car for car in self.cars.values() if car.entry == entry and car.x < car.width * 3)
        elif entry == Car.LEFT:
            return any(car for car in self.cars.values() if car.entry == entry and car.x > self.width - car.width * 3)
        return True

    def add_new_agents(self):
        for entry in (Car.UP, Car.DOWN, Car.RIGHT, Car.LEFT):
            if not self.is_entry_occupied(entry) and self.random.random() < self.spawn_rate:
                self.spawn_car(entry, 50, 30)

    def step(self):
        self.schedule.step()
        self.add_new_agents()
        self.remove_cars()
        self.control_cars()

    def control_cars(self):
        rects = {car.unique_id: car.rect for car in self.cars.values()}
        intersection = next((rect for rect in rects if rects[rect] in self.intersection), None)

        new_rects = []
        for car in self.cars.values():
            rect = car.new_rect
            if any(rect in rects[other] for other in rects if car.unique_id != other) or any(
                    rect in other for other in new_rects):
                car.can_move = False
            else:
                if rect in self.intersection and car.unique_id != intersection:
                    if intersection is None:
                        intersection = car.unique_id
                    else:
                        car.can_move = False
                        continue
                car.can_move = True
                new_rects.append(rect)
