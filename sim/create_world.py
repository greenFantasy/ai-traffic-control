from consts import *
from world import *
import time

world = SimpleIntersectionWorld()
world.add_vehicle_to_lane(world.outer_north_lane)
print("Intersection Lower Boundary:", world.intersection.lower_boundary)
s = time.time()
for i in range(10000):
    # for v in world.vehicles:
        # print(world.time, v.rear_left)
    #    tl = world.intersection.traffic_lights[(Direction.north, MovementOptions.through)]
    # if len(tl.get_sensor_data()) > 0:
    #    print("I SEE A CAR LETS GOOOOOOOOO")
    world.play()
e = time.time()
print(e - s)
