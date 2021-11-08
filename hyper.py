from posixpath import split
import sys
sys.path.append("../ai-traffic-control/sim")
sys.path.append("../ai-traffic-control/RL")
sys.path.append("../ai-traffic-control/generator")
sys.path.append("../ai-traffic-control/data")
import world
import generator
import pandas as pd
import time
import logger

# print(pd.read_csv("data/vehicle_despawn.csv"))

all_splits = [[i] * 4 for i in [1, 2, 5, 10, 15, 20]]
performances = []
for split_times in all_splits:
    w = world.DedicatedLeftTurnIntersectionWorld(split_times)
    w.add_generator(generator.SimpleGenerator(w, {"p": 0.01}))
    for i in range(10000):
        w.play()
    logger.logger = None
    f = open("data/vehicle_despawn.csv", "r")
    performances.append(len(f.readlines())) # len(pd.read_csv("data/vehicle_despawn.csv"))
    f.close()
for p, st in zip(performances, all_splits):    
    print(st, p)