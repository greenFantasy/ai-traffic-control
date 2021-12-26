import torch
import torch.nn as nn
from modelcreator import StateActionNetwork

model = torch.load('../RL/model.pt')
model.train_all("../RL/traindata", "../RL/trainparamstest.txt")