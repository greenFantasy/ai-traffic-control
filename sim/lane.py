from typing import Optional
from vehicle import Vehicle
from consts import *
from car import Car
import heapq

class Lane:
    def __init__(
        self,
        direction: Direction,
        position: float,
        width: float,
        start: float = None,
        end: float = None
    ):
        self.direction = direction
        self.position = position
        self.width = width
        self.start = start
        self.end = end
        # Vehicle list sorted depending on direction - furthest car on road is always first
        self.vehicles = []
        self.min = self.position - self.width / 2
        self.max = self.position + self.width / 2
        self.street = None

    def get_vehicles(self, start: Optional[float] = None, end: Optional[float] = None):
        start = start if start else -float('inf')
        end = end if end else float('inf')
        return [vehicleTup[1] for vehicleTup in self.vehicles if end>=vehicleTup[1].get_changing_coordinate()>=start]

    def add_vehicle(self, vehicle: Car):
        # Set lane in vehicle so it knows where it is.
        vehicle.setLane(self)
        vehicle.findBoundaries()
        # Ensure vehicle is in the lane
        if self.direction == Direction.north or self.direction == Direction.south:
            assert (self.min <= vehicle.rear_left[0] <= self.max) and (self.min <= vehicle.rear_right[0] <= self.max)
        elif self.direction == Direction.west or self.direction == Direction.east:
            assert (self.min <= vehicle.rear_left[1] <= self.max) and (self.min <= vehicle.rear_right[1] <= self.max)
        # Add to the sorted vehicle list (sorted depending on lane direction)
        if self.direction == Direction.north:
            heapq.heappush(self.vehicles, (-vehicle.rear_left[1],vehicle))
        elif self.direction == Direction.south:
            heapq.heappush(self.vehicles, (vehicle.rear_left[1], vehicle))
        elif self.direction == Direction.east:
            heapq.heappush(self.vehicles, (-vehicle.rear_left[0],vehicle))
        elif self.direction == Direction.west:
            heapq.heappush(self.vehicles, (vehicle.rear_left[0],vehicle))
