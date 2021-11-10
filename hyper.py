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
import numpy as np
import matplotlib.pyplot as plt

# print(pd.read_csv("data/vehicle_despawn.csv"))

all_splits = [[i] * 4 for i in range(1, 21)]
iterations = 10000
performances = []
for split_times in all_splits:
    w = world.DedicatedLeftTurnIntersectionWorld(split_times)
    w.add_generator(generator.SimpleGenerator(w, {"p": 0.01}))
    for i in range(iterations):
        w.play()
    #logger.logger = None
    w.close()
    f = open("data/vehicle_despawn.csv", "r")
    performances.append(len(f.readlines())) # len(pd.read_csv("data/vehicle_despawn.csv"))
    print(performances)
    f.close()
    print(f"Test with {split_times[0]} complete")
for p, st in zip(performances, all_splits):    
    print(st, p)
np.save("performance_split_times.npy", performances)
# performances = np.load("performance_split_times.npy")
plt.plot([elem[0] for elem in all_splits], performances)
plt.show()