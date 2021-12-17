from typing import Dict, Tuple

from autonomous_intersection.agents.car import Car, Steer
from autonomous_intersection.intersection_builder import IntersectionBuilder
from autonomous_intersection.rect import Rect


class IntersectionManager:
    def __init__(self, width: int, height: int, road_width: int, default_velocity: int):
        self.road_width: int = road_width
        self.width: int = width
        self.height: int = height
        self.default_velocity = default_velocity
        self.cars: Dict[int, Car] = {}
        self.intersection = self._get_intersection_rect()

    def build_background(self):
        return IntersectionBuilder.generate(self.width, self.height, self.road_width, self.road_width // 10,
                                            self.road_width // 25, self)

    def _get_intersection_rect(self) -> Rect:
        return Rect(self.width / 2 - self.road_width / 2, self.height / 2 - self.road_width / 2, self.road_width,
                    self.road_width, 0)

    def create_new_car(self, entry: Tuple[int, int], width: int, height: int, agent_id: int, model):
        if entry == Car.UP:
            car = Car(agent_id, (self.width / 2 + self.road_width / 4 - height / 2, self.height - width),
                      (width, height), model, Car.ANGLE_UP, Car.DOWN, velocity=self.default_velocity)
        elif entry == Car.DOWN:
            car = Car(agent_id, (self.width / 2 - self.road_width / 4 - height / 2, 0), (width, height), model,
                      Car.ANGLE_DOWN, Car.DOWN, velocity=self.default_velocity)
        elif entry == Car.LEFT:
            car = Car(agent_id, (self.width - width, self.height / 2 - self.road_width / 4 - height / 2),
                      (width, height), model, Car.ANGLE_LEFT, Car.UP, velocity=self.default_velocity)
        elif entry == Car.RIGHT:
            car = Car(agent_id, (0, self.height / 2 + self.road_width / 4 - height / 2), (width, height), model,
                      Car.ANGLE_RIGHT, Car.UP, velocity=self.default_velocity)
        else:
            raise Exception()
        self.cars[agent_id] = car
        return car

    def is_entry_occupied(self, entry: float):
        if entry == Car.UP:
            return any(car for car in self.cars.values() if car.entry == entry and car.y > self.height - car.width * 3)
        elif entry == Car.DOWN:
            return any(car for car in self.cars.values() if car.entry == entry and car.y < car.height * 3)
        elif entry == Car.RIGHT:
            return any(car for car in self.cars.values() if car.entry == entry and car.x < car.width * 3)
        elif entry == Car.LEFT:
            return any(car for car in self.cars.values() if car.entry == entry and car.x > self.width - car.width * 3)
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
                             self.distance_from_line(car.entry, car.steer_direction, car.x,
                                                     car.y))
                car.can_move = True
                new_rects.append(rect)

    def should_car_turn(self, car) -> bool:
        if car.steer_direction == Steer.Forward or car.steer != Steer.Forward: return False
        current_dist = self.distance_from_line(car.entry, car.steer_direction, car.x, car.y)
        next_dist = self.distance_from_line(car.entry, car.steer_direction, *car.new_position[:2])
        return current_dist >= 2 * car.width >= next_dist

    def distance_from_line(self, entry, steer, x, y):
        if steer == Steer.Right:
            if entry in (Car.ANGLE_UP, Car.ANGLE_DOWN):
                return abs(self.intersection.center[1] - y)
            else:
                return abs(self.intersection.center[0] - x)
        else:
            if entry == Car.ANGLE_UP:
                return abs(self.intersection.top - y)
            elif entry == Car.ANGLE_DOWN:
                return abs(self.intersection.bottom - y)
            elif entry == Car.ANGLE_LEFT:
                return abs(self.intersection.right - x)
            else:
                return abs(self.intersection.left - x)
