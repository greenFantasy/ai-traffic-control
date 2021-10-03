from consts import *
from world import *
import time
import random

world = SimpleIntersectionWorld()
#print(len(world.sensors))

world.add_vehicle_to_path(world.inner_north_lane_i)
world.add_vehicle_to_path(world.inner_south_lane_i)

streets = world.streets[::2]

for i in range(10000):
    world.play()
    if i % 20 == 0:
        r1 = random.randint(0, 3)
        r2 = random.randint(0, 1)
        world.add_vehicle_to_path(streets[r1].paths[r2])


# world.intersection.traffic_lights[('0', MovementOptions.through)].red_to_green()
# world.intersection.traffic_lights[('0', MovementOptions.left)].red_to_green()
# world.intersection.traffic_lights[('0', MovementOptions.right)].red_to_green()

# world.intersection.traffic_lights[('0', MovementOptions.through)].green_to_yellow()
# world.intersection.traffic_lights[('0', MovementOptions.left)].green_to_yellow()
# world.intersection.traffic_lights[('0', MovementOptions.right)].green_to_yellow()

# for i in range(1000):
#     print(world.vehicles)
#     # print(world.sensors[0].get_data(), world.time)
#     world.play()

# for i in range(100):
#     #print(world.vehicles)
#     world.play()


# print("Intersection Lower Boundary:", world.intersection.lower_boundary)
# s = time.time()
# for i in range(100):
#     for v in world.vehicles:
#         print(world.time, v.rear_left)
#         tl = world.intersection.traffic_lights[(Direction.north, MovementOptions.through)]
    # if len(tl.get_sensor_data()) > 0:
    #    print("I SEE A CAR LETS GOOOOOOOOO")
#     world.play()
# e = time.time()
# print(e - s)
