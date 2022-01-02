from typing import Optional

import autonomous_intersection.model
from autonomous_intersection.agents.car import Car
from autonomous_intersection.agents.direction import Direction, Steer
from autonomous_intersection.constants import STEPS_PER_SECOND
from autonomous_intersection.managers.intersection_manager import IntersectionManager


class TrafficLightManager(IntersectionManager):
    def __init__(self, width: int, height: int, road_width: int, parameters: dict,
                 model: "autonomous_intersection.model.Intersection"):
        super().__init__(width, height, road_width, parameters, model)
        self.current_light: Optional[Direction] = Direction.Right
        self.next_light: Optional[Direction] = None
        self.change_time = STEPS_PER_SECOND * 10
        self.indicator = self.model.draw_debug_object(self.lanes[self.current_light].line.bounds, "green")
        self.agents = set()

    def change_lights(self) -> None:
        if self.current_light is None and self.change_time == self.steps:
            self.change_time += STEPS_PER_SECOND * 10
            self.current_light = self.next_light
            self.indicator = self.model.draw_debug_object(self.lanes[self.current_light].line.bounds, "green")
        elif self.current_light is not None and self.change_time == self.steps:
            self.change_time += STEPS_PER_SECOND * 2
            self.next_light = self.current_light.turned(Steer.Left)
            self.current_light = None
            self.model.delete_debug_object(self.indicator)
            self.indicator = None

    def can_turn(self, car: Car) -> bool:
        return self.current_light and (self.current_light == car.initial_direction or (
                car.steer_direction == Steer.Right and car.target == self.current_light.reverse))

    def control_cars(self) -> None:
        self.change_lights()
        rects = {car.unique_id: car.rect for car in self.cars.values()}

        new_rects = []
        for car in self.cars.values():
            rect = car.new_rect
            # collisions
            if any(rect in rects[other] for other in rects if car.unique_id != other) or any(
                    rect in other for other in new_rects):
                car.stop()
            else:
                # at intersection
                if rect in self.intersection:
                    self.agents.add(car.unique_id)
                    if self.first_step is None:
                        self.first_step = self.steps
                    if self.can_turn(car):
                        car.start(STEPS_PER_SECOND)
                    else:
                        if car.rect in self.intersection:
                            car.start()
                        else:
                            car.stop()
                else:
                    car.start(STEPS_PER_SECOND // 2)
                new_rects.append(rect)

        self.steps += 1
        self.agent_count = len(self.agents)
