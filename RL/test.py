import torch
from modelcreator import StateActionNetwork

model = torch.load("model.pt")

model.train_all("traindata", "trainparams.txt")