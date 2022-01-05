from typing import Dict

import autonomous_intersection.model
from autonomous_intersection.agents.car import Car
from autonomous_intersection.managers.intersection_manager import IntersectionManager
from autonomous_intersection.rect import Rect


class PredictionBasedManager(IntersectionManager):
    def __init__(self, width: int, height: int, road_width: int, parameters: dict,
                 model: "autonomous_intersection.model.Intersection"):
        super().__init__(width, height, road_width, parameters, model)
        self.reservations: Dict[Car, Dict[int, Rect]] = {}

    def reserve(self, car: Car):
        state = car.state
        step = self.steps
        self.reservations[car] = {}
        visited = False
        while not visited or car.rect(state) in self.intersection:
            state = car.simulate(state, 1)
            self.reservations[car][step] = car.rect(state)
            step += 1
            if not visited and car.rect(state) in self.intersection:
                visited = True

    def can_reserve(self, car: Car) -> bool:
        state = car.state
        step = self.steps
        visited = False
        while not visited or car.rect(state) in self.intersection:
            state = car.simulate(state, 1)
            rect = car.rect(state)
            if not visited and rect in self.intersection:
                visited = True
            for reservation in self.reservations.values():
                if (step in reservation and reservation[step] in rect) or (
                        step - 1 in reservation and reservation[step - 1] in rect):
                    return False
            step += 1

        return True

    def control_cars(self):
        self.steps += 1
        rects = {car.unique_id: car.rect() for car in self.cars.values()}
        self.clear_reservations()

        new_rects = []
        for car in self.cars.values():
            rect = car.new_rect
            # collisions
            reserved = car in self.reservations
            if not reserved and (any(rect in rects[other] for other in rects if car.unique_id != other) or any(
                    rect in other for other in new_rects)):
                car.stop()
            else:
                # at intersection
                if not reserved and rect in self.intersection:
                    if self.can_reserve(car):
                        # reserve lanes
                        self.reserve(car)
                        self.agent_count += 1
                        if self.first_step is None: self.first_step = self.steps
                    else:
                        car.stop()
                        continue
                car.start()
                new_rects.append(rect)

    def clear_reservations(self):
        to_del = set()
        for car, reservations in self.reservations.items():
            if not reservations:
                to_del.add(car)
        for car in to_del:
            del self.reservations[car]
