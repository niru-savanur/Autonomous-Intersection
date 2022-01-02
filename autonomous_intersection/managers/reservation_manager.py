from typing import Optional, Dict, List

import autonomous_intersection.model
from autonomous_intersection.agents.car import Car
from autonomous_intersection.agents.direction import Steer
from autonomous_intersection.managers.intersection_manager import IntersectionManager, quarter


class ReservationBasedManager(IntersectionManager):
    def __init__(self, width: int, height: int, road_width: int, parameters: dict,
                 model: "autonomous_intersection.model.Intersection"):
        super().__init__(width, height, road_width, parameters, model)
        self.reservations: Dict[frozenset, Optional[Car]] = self.create_turns()

    def control_cars(self):
        self.steps += 1
        rects = {car.unique_id: car.rect for car in self.cars.values()}
        self.clear_reservations()

        new_rects = []
        for car in self.cars.values():
            rect = car.new_rect
            # collisions
            if any(rect in rects[other] for other in rects if car.unique_id != other) or any(
                    rect in other for other in new_rects):
                car.stop()
            else:
                # at intersection
                if rect in self.intersection and car not in self.reservations.values():
                    occupied = self.get_occupied_turns(car)
                    if all(self.reservations[turn] is None for turn in occupied):
                        # reserve lanes
                        for turn in occupied:
                            self.reservations[turn] = car
                        self.agent_count += 1
                        if self.first_step is None: self.first_step = self.steps
                    else:
                        car.stop()
                        continue
                car.start()
                new_rects.append(rect)

    def clear_reservations(self):
        for key in self.reservations:
            if self.reservations[key] is not None:
                rect = self.reservations[key].rect
                if rect not in self.intersection:
                    self.reservations[key] = None

    @staticmethod
    def get_occupied_turns(car: Car) -> List[frozenset]:
        if car.steer_direction == Steer.Forward:
            return [quarter(car.initial_direction, car.initial_direction.turned(Steer.Right)),
                    quarter(car.initial_direction, car.initial_direction.turned(Steer.Left))]
        if car.steer_direction == Steer.Right:
            return [quarter(car.initial_direction, car.target)]
        return [quarter(car.initial_direction, car.target), quarter(car.initial_direction, car.target.reverse),
                quarter(car.initial_direction.reverse, car.target)]
