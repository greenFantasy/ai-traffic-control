import matplotlib.pyplot as plt
import sys
import os
import numpy as np
import dill
import pandas as pd
# sys.path.append("/Users/rajatmittal/Documents/Projects/ai-traffic-control/RL")
# from modelcreator import StateActionNetwork

sim_data_dir = "../data"
dirnames = os.listdir(sim_data_dir)
plotting_tups = []
plotting_tups_fail = []
plotting_tups_all = []
plotting_tups_wait = []
for dirname in dirnames:
    if "." in dirname:
        continue
    idx = int(dirname.split("_")[-1][3:])
    try:
        filepath = os.path.join(sim_data_dir, dirname, "vehicle_intersection_times.pkl")
        vehicle_intersection_times = dill.load(open(filepath, "rb"))
        vehicle_spawn = pd.read_csv(os.path.join(sim_data_dir, dirname, "vehicle_spawn.csv"))
        vehicle_spawn_dict = {car: spawn_time for car, spawn_time in vehicle_spawn.itertuples(index=False)}
        max_t = 90.0

        total_spawned = len([c for c in vehicle_spawn_dict if vehicle_spawn_dict[c] < max_t])
        total_through = len([c for c, its, ent, ext in vehicle_intersection_times if ext is not None and vehicle_spawn_dict[c] < max_t])
        wait_time = np.max([(ext if ext else 100.0) - ent for c, its, ent, ext in vehicle_intersection_times])

        plotting_tups.append((idx, total_through))
        plotting_tups_fail.append((idx, total_spawned - total_through))
        plotting_tups_all.append((idx, total_spawned))
        plotting_tups_wait.append((idx, wait_time))
    except FileNotFoundError:
       print(f"No data for {idx}")
       pass
    
plotting_tups.sort(key=lambda x: x[0])
plotting_tups_fail.sort(key=lambda x: x[0])
plotting_tups_all.sort(key=lambda x: x[0])
plotting_tups_wait.sort(key=lambda x: x[0])
# plt.plot([elem[0] for elem in plotting_tups], [elem[1] for elem in plotting_tups])
# plt.plot([elem[0] for elem in plotting_tups_all], [elem[1] for elem in plotting_tups_all])
# plt.show()
d = 20
plt.plot(np.convolve([elem[1] for elem in plotting_tups], np.ones(d)/d, mode='valid'), "r")
plt.plot(np.convolve([elem[1] for elem in plotting_tups_fail], np.ones(d)/d, mode='valid'), "orange")
plt.plot(np.convolve([elem[1] for elem in plotting_tups_all], np.ones(d)/d, mode='valid'), "g")
plt.yticks(range(0,30,1))
plt.title("Cars allowed through intersection")
plt.show()

plt.plot(np.convolve([elem[1] for elem in plotting_tups_wait], np.ones(d)/d, mode='valid'), "r")
plt.show()

# import torch
# import dill 

# path = "/Users/rajatmittal/Documents/Projects/ai-traffic-control/RL/traindata/2021_12_08_12_56_02_run1577.pkl"
# with open(path, "rb") as file:
#     sars = dill.load(file)

# model = torch.load("/Users/rajatmittal/Documents/Projects/ai-traffic-control/RL/model.pt")


# for idx in range(len(sars)):
#     print("State: ", sars[idx][0])
#     print("Action: ", sars[idx][1])
#     print("Reward: ", sars[idx][2])
#     print("Current (Not time of Sim) Model Predictions: ", model.forward(sars[idx][0].unsqueeze(0)))
#     print()
#     print()