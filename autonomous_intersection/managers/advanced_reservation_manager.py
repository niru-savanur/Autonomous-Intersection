from typing import Optional, Dict, List

import autonomous_intersection.model
from autonomous_intersection.agents.car import Car
from autonomous_intersection.agents.direction import Direction, Steer
from autonomous_intersection.managers.intersection_manager import IntersectionManager, quarter
from autonomous_intersection.rect import Rect


class AdvancedReservationBasedManager(IntersectionManager):
    def __init__(self, width: int, height: int, road_width: int, parameters: dict,
                 model: "autonomous_intersection.model.Intersection"):
        super().__init__(width, height, road_width, parameters, model)
        self.reservations: Dict[frozenset, Optional[Car]] = self.create_turns()
        self.reservation_paths: Dict[Car, List[frozenset[Direction]]] = {}
        self.debugs = []

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
                        self.reservation_paths[car] = occupied
                        self.agent_count += 1
                        if self.first_step is None: self.first_step = self.steps
                    else:
                        car.stop()
                        continue
                car.start()
                new_rects.append(rect)

        for debug in self.debugs:
            self.model.delete_debug_object(debug)
        self.debugs.clear()
        for key, val in self.reservations.items():
            if val is not None:
                if key == {Direction.Left, Direction.Down}:
                    self.debugs.append(
                        self.model.draw_debug_object(Rect(self.intersection.left, self.intersection.top, 7, 7), "red"))
                if key == {Direction.Left, Direction.Up}:
                    self.debugs.append(
                        self.model.draw_debug_object(Rect(self.intersection.right, self.intersection.top, 7, 7), "red"))
                if key == {Direction.Right, Direction.Down}:
                    self.debugs.append(
                        self.model.draw_debug_object(Rect(self.intersection.left, self.intersection.bottom, 7, 7),
                                                     "red"))
                if key == {Direction.Right, Direction.Up}:
                    self.debugs.append(
                        self.model.draw_debug_object(Rect(self.intersection.right, self.intersection.bottom, 7, 7),
                                                     "red"))

    def clear_reservations(self):
        to_del = []
        for car, path in self.reservation_paths.items():
            if not path:
                to_del.append(car)
                continue
            n1, n2 = path[0]
            rect = car.rect
            if not (rect in self.lanes[n1].bounds and rect in self.lanes[n2].bounds):
                self.reservations[path.pop(0)] = None
                if not path:
                    to_del.append(car)

        for car in to_del:
            del self.reservation_paths[car]

    @staticmethod
    def get_occupied_turns(car: Car) -> List[frozenset]:
        if car.steer_direction == Steer.Forward:
            return [quarter(car.initial_direction, car.initial_direction.turned(Steer.Right)),
                    quarter(car.initial_direction, car.initial_direction.turned(Steer.Left))]
        if car.steer_direction == Steer.Right:
            return [quarter(car.initial_direction, car.target)]
        return [quarter(car.initial_direction, car.target.reverse), quarter(car.initial_direction, car.target),
                quarter(car.initial_direction.reverse, car.target)]
