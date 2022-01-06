import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


sys.path.append("../ai-traffic-control/sim")
sys.path.append("../ai-traffic-control/RL")
sys.path.append("../ai-traffic-control/generator")
import world
from map_creator import DynamicWorld
import generator
from util.analyze import analyze

num_trials = 50
max_split = 10
iterations = 1000
rl = False

all_splits = [[i] * 4 for i in range(1, max_split+1)]
trials = {}

for split_times in (all_splits if not rl else [(1,)]):
    trials[tuple(split_times)] = []
    for _ in range(num_trials):
        w = world.DedicatedLeftTurnIntersectionWorld(1.0, split_times=split_times, rl=rl)
        # w.add_generator(generator.SimpleGenerator(w, {"p": 0.003}))
        # w = DynamicWorld()
        w.add_generator(generator.MarkovGenerator(w, {"car2car": 0.02, "nocar2nocar": 0.995}))
        # w.add_generator(generator.MarkovGenerator(w, {"car2car": 0.06, 'nocar2nocar': 0.995}))
        for i in range(iterations):
            w.play()
        w.close()
        results = analyze('data')
        trials[tuple(split_times)].append(results)
    print("spawned", split_times[0], ": ", np.mean([x['total_spawned'] for x in trials[tuple(split_times)]]))
    print("through", split_times[0], ": ", np.mean([x['total_through'] for x in trials[tuple(split_times)]]))
    print("left", split_times[0], ": ", np.mean([x['total_left_over'] for x in trials[tuple(split_times)]]))
    print("wait", split_times[0], ": ", np.mean([x['mean_wait_time'] for x in trials[tuple(split_times)]]))
    print("aog", split_times[0], ": ", np.mean([x['percentage_arrival_on_green'] for x in trials[tuple(split_times)]]))
    # print(split_times[0], ": ", np.mean([x['mean_wait_time'] for x in trials[tuple(split_times)]]))
    
# print(trials)

# np.save("trials10_performance_split_times.npy", trials)
# trials = np.load("trials10_performance_split_times.npy")
# perfLists = [[trials[i][j] for i in range(len(trials))] for j in range(len(trials[0]))]
# perfAvg = [np.mean(perfLists[i]) for i in range(len(perfLists))]
# #performances = np.load("performance_split_times.npy")
# plt.plot([elem[0] for elem in all_splits], perfAvg)
# plt.show()