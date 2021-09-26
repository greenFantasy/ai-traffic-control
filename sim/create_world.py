from consts import *
from world import *
import time

world = SimpleIntersectionWorld()
#print(len(world.sensors))

world.add_vehicle_to_path(world.inner_north_lane_i)
for i in range(100):
    #print(world.vehicles)
    print(world.sensors[0].get_data(), world.time)
    world.play()

world.intersection.traffic_lights[('0', MovementOptions.through)].red_to_green()
world.intersection.traffic_lights[('0', MovementOptions.left)].red_to_green()
world.intersection.traffic_lights[('0', MovementOptions.right)].red_to_green()


for i in range(100):
    #print(world.vehicles)
    world.play()


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
