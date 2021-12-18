from typing import Dict, Tuple

import autonomous_intersection.model
from autonomous_intersection.agents.car import Car, Steer, Direction
from autonomous_intersection.intersection_builder import IntersectionBackgroundBuilder
from autonomous_intersection.lane import Lane
from autonomous_intersection.rect import Rect


class IntersectionManager:
    def __init__(self, width: int, height: int, road_width: int, default_velocity: int,
                 model: "autonomous_intersection.model.Intersection"):
        self.road_width: int = road_width
        self.width: int = width
        self.height: int = height
        self.model = model
        self.default_velocity = default_velocity
        self.cars: Dict[int, Car] = {}
        self.intersection = self._get_intersection_rect()
        self.lanes: Dict[Direction, Lane] = self.create_lanes()

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

        self.model.draw_debug_object(result[Direction.Right].line.bounds, "red")
        self.model.draw_debug_object(result[Direction.Left].line.bounds, "lime")
        self.model.draw_debug_object(result[Direction.Up].line.bounds, "yellow")
        self.model.draw_debug_object(result[Direction.Down].line.bounds, "purple")

        return result

    def _get_intersection_rect(self) -> Rect:
        return Rect(self.width / 2 - self.road_width / 2, self.height / 2 - self.road_width / 2, self.road_width,
                    self.road_width, 0)

    def create_new_car(self, initial_direction: Direction, car_size: Tuple[int, int], agent_id: int):
        car = Car(agent_id, self.model, self.lanes[initial_direction].line,
                  self.get_initial_car_position(initial_direction),
                  car_size, initial_direction, initial_direction, velocity=self.default_velocity)
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

    def control_cars(self):
        rects = {car.unique_id: car.rect for car in self.cars.values()}
        intersection = next((rect for rect in rects if rects[rect] in self.intersection), None)

        new_rects = []
        for car in self.cars.values():
            rect = car.new_rect
            # collisions
            if any(rect in rects[other] for other in rects if car.unique_id != other) or any(
                    rect in other for other in new_rects):
                car.can_move = False
            else:
                should_move = self.should_car_turn(car)
                if (should_move or rect in self.intersection) and car.unique_id != intersection:
                    if intersection is None:
                        intersection = car.unique_id
                    else:
                        car.can_move = False
                        continue
                if should_move:
                    car.turn(car.steer_direction,
                             round(self.distance_from_line(car.initial_direction, car.steer_direction, car.x,
                                                           car.y)))
                car.can_move = True
                new_rects.append(rect)

    def should_car_turn(self, car: Car) -> bool:
        if car.steer_direction == Steer.Forward or car.steer != Steer.Forward: return False
        current_dist = self.distance_from_line(car.initial_direction, car.steer_direction, car.x, car.y)
        next_dist = self.distance_from_line(car.initial_direction, car.steer_direction, *car.new_position[:2])
        return current_dist >= 2 * car.width >= next_dist

    def distance_from_line(self, initial_direction: Direction, steer: Steer, x: int, y: int) -> float:
        if steer == Steer.Right:
            if initial_direction in (Direction.Up, Direction.Down):
                return abs(self.intersection.center[1] - y)
            else:
                return abs(self.intersection.center[0] - x)
        else:
            if initial_direction == Direction.Up:
                return abs(self.intersection.top - y)
            elif initial_direction == Direction.Down:
                return abs(self.intersection.bottom - y)
            elif initial_direction == Direction.Left:
                return abs(self.intersection.right - x)
            else:
                return abs(self.intersection.left - x)
