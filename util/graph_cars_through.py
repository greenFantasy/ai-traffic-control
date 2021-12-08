import matplotlib.pyplot as plt
import sys
import os
import numpy as np
# sys.path.append("/Users/rajatmittal/Documents/Projects/ai-traffic-control/RL")
# from modelcreator import StateActionNetwork

sim_data_dir = "../data"
dirnames = os.listdir(sim_data_dir)
plotting_tups = []
for dirname in dirnames:
    if "." in dirname:
        continue
    idx = int(dirname.split("_")[-1][3:])
    filepath = os.path.join(sim_data_dir, dirname, "vehicle_despawn.csv")
    f = open(filepath, "r")
    numCars = len(f.readlines())
    f.close()
    plotting_tups.append((idx, numCars))
plotting_tups.sort(key=lambda x: x[0])
plt.plot([elem[0] for elem in plotting_tups], [elem[1] for elem in plotting_tups])
# plt.show()
plt.plot([elem[0] for elem in plotting_tups], np.convolve([elem[1] for elem in plotting_tups], np.ones(10)/10, mode='same'), "r")
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