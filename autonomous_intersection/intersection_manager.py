import random
from math import ceil
from typing import Dict, Tuple, Optional, List, Set

import autonomous_intersection.model
from autonomous_intersection.agents.car import Car
from autonomous_intersection.agents.direction import Direction, Steer
from autonomous_intersection.constants import PIXEL_PER_METER, STEPS_PER_SECONDS
from autonomous_intersection.intersection_builder import IntersectionBackgroundBuilder
from autonomous_intersection.lane import Lane
from autonomous_intersection.rect import Rect
from autonomous_intersection.unit_translator import kmh_to_pixel_per_step


class IntersectionManager:
    def __init__(self, width: int, height: int, road_width: int, parameters: dict,
                 model: "autonomous_intersection.model.Intersection"):
        self.road_width: int = road_width
        self.width: int = width
        self.height: int = height
        self.model = model
        self.default_velocity = kmh_to_pixel_per_step(parameters.get("velocity", 50), PIXEL_PER_METER,
                                                      STEPS_PER_SECONDS)
        self.acceleration = ceil(kmh_to_pixel_per_step(parameters.get("acceleration", 20), PIXEL_PER_METER,
                                                       STEPS_PER_SECONDS) / STEPS_PER_SECONDS)
        self.deceleration = self.default_velocity

        self.cars: Dict[int, Car] = {}
        self.intersection = self._get_intersection_rect()
        self.lanes: Dict[Direction, Lane] = self.create_lanes()
        self.agent_count = 0
        self.steps = 0
        self.first_step = None
        self.reservations: Dict[frozenset, Optional[Car]] = self.create_turns()

    def build_background(self):
        return IntersectionBackgroundBuilder.generate(self.width, self.height, self.road_width, self.road_width // 10,
                                                      self.road_width // 25, self)

    def create_lanes(self) -> Dict[Direction, Lane]:
        result = {}
        int_rect = self.intersection
        result[Direction.Right] = Lane(Rect(0, int_rect.center[1], self.width, int_rect.height // 2))
        result[Direction.Left] = Lane(Rect(0, int_rect.top, self.width, int_rect.height // 2))
        result[Direction.Down] = Lane(Rect(int_rect.left, 0, int_rect.width // 2, self.height))
        result[Direction.Up] = Lane(Rect(int_rect.center[0], 0, int_rect.width // 2, self.height))

        return result

    @staticmethod
    def create_turns() -> Dict[frozenset, Optional[Car]]:
        result = {
            frozenset({Direction.Left, Direction.Down}): None,
            frozenset({Direction.Left, Direction.Up}): None,
            frozenset({Direction.Right, Direction.Down}): None,
            frozenset({Direction.Right, Direction.Up}): None}
        return result

    def _get_intersection_rect(self) -> Rect:
        return Rect(self.width / 2 - self.road_width / 2, self.height / 2 - self.road_width / 2, self.road_width,
                    self.road_width, 0)

    def create_new_car(self, initial_direction: Direction, car_size: Tuple[int, int], agent_id: int):
        direction = random.choice([d for d in Direction if d != initial_direction.reverse])
        car = Car(agent_id, self.model, self.lanes[initial_direction].line, self.lanes[direction].line,
                  self.get_initial_car_position(initial_direction),
                  car_size, initial_direction, direction,
                  velocity=self.default_velocity,
                  acceleration=self.acceleration,
                  deceleration=self.deceleration)
        self.cars[agent_id] = car
        return car

    def get_initial_car_position(self, direction: Direction) -> Tuple[int, int]:
        lane = self.lanes[direction]
        if direction == Direction.Up:
            return round(lane.bounds.center[0]), self.height - 1
        if direction == Direction.Down:
            return round(lane.bounds.center[0]), 0
        if direction == Direction.Left:
            return self.width - 1, round(lane.bounds.center[1])
        return 0, round(lane.bounds.center[1])

    def is_entry_occupied(self, initial_direction: Direction):
        if initial_direction == Direction.Up:
            return any(car for car in self.cars.values() if
                       car.initial_direction == initial_direction and car.y > self.height - car.width * 3)
        elif initial_direction == Direction.Down:
            return any(car for car in self.cars.values() if
                       car.initial_direction == initial_direction and car.y < car.height * 3)
        elif initial_direction == Direction.Right:
            return any(car for car in self.cars.values() if
                       car.initial_direction == initial_direction and car.x < car.width * 3)
        elif initial_direction == Direction.Left:
            return any(car for car in self.cars.values() if
                       car.initial_direction == initial_direction and car.x > self.width - car.width * 3)
        return True

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

    def remove_cars(self, space):
        to_delete = set()
        for car in filter(self.is_car_out_of_bounds, self.cars.values()):
            space.remove_agent(car)
            to_delete.add(car)

        for car in to_delete:
            del self.cars[car.unique_id]

    def clear_reservations(self):
        for key in self.reservations:
            if self.reservations[key] is not None:
                rect = self.reservations[key].rect
                if rect not in self.intersection:
                    self.reservations[key] = None

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

    @staticmethod
    def get_occupied_turns(car: Car) -> List[frozenset]:
        if car.steer_direction == Steer.Forward:
            return [frozenset({car.initial_direction, car.initial_direction.turned(Steer.Right)}),
                    frozenset({car.initial_direction, car.initial_direction.turned(Steer.Left)})]
        if car.steer_direction == Steer.Right:
            return [frozenset({car.initial_direction, car.target})]
        return [frozenset({car.initial_direction, car.target}), frozenset({car.initial_direction, car.target.reverse}),
                frozenset({car.initial_direction.reverse, car.target})]
