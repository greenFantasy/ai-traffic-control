# import matplotlib.pyplot as plt

# cars_through = 

# f = open("data/vehicle_despawn.csv", "r")
# cars_through.append(len(f.readlines())) # len(pd.read_csv("data/vehicle_despawn.csv"))
# f.close()

# plt.plot(cars_through)
import sys
sys.path.append("/Users/rajatmittal/Documents/Projects/ai-traffic-control/RL")
from modelcreator import StateActionNetwork

import torch
import dill 

path = "/Users/rajatmittal/Documents/Projects/ai-traffic-control/RL/traindata/2021_12_08_12_56_02_run1577.pkl"
with open(path, "rb") as file:
    sars = dill.load(file)

model = torch.load("/Users/rajatmittal/Documents/Projects/ai-traffic-control/RL/model.pt")


for idx in range(len(sars)):
    print("State: ", sars[idx][0])
    print("Action: ", sars[idx][1])
    print("Reward: ", sars[idx][2])
    print("Current (Not time of Sim) Model Predictions: ", model.forward(sars[idx][0].unsqueeze(0)))
    print()
    print()