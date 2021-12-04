from posixpath import split
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset
from typing import Optional, List
# import torchvision
# from torchvision import models
# import random
# from flags import CUDA
# from tqdm import tqdm
import os
import dill
import time

class StateActionValueDataset(Dataset):
    def __init__(self, sars):
        self.sars = sars
        
        self.states = torch.stack([x[0] for x in self.sars]).float()
        self.actions = torch.tensor([x[1] for x in self.sars]).long()
        self.values = torch.tensor([x[2] for x in self.sars]).float()
    
    def __len__(self):
        return len(self.sars)
    
    def __getitem__(self, idx):
        return self.states[idx], self.actions[idx], self.values[idx]

def print_children_nan(model):
    for c in model.children():
        if len(list(c.children())) > 0:
            print_children_nan(c)
        else:
            if 'weight' in dir(c):
                print(c, torch.isnan(c.weight).sum())
            else:
                print('NO WEIGHT', c)

class StateActionNetwork(nn.Module):
    def __init__(self,
                 loss_function,
                 input_size,
                 output_size,
                 init_low=-0.1,
                 init_high=0.1,
                 cuda=False,
                ):

        super(StateActionNetwork, self).__init__()
        self.input_size = input_size
        self.output_size = output_size

        self.cuda = cuda

        self.init_low = init_low
        self.init_high = init_high

        layers = [nn.Flatten(), nn.Linear(self.input_size, 20), 
                    nn.ReLU(), nn.Linear(20, 10), 
                    nn.ReLU(), nn.Linear(10, self.output_size)]
        self.forward_block = nn.Sequential(*layers)

        self.init_parameters(init_low, init_high)

    def init_parameters(self, init_low, init_high):
        for p in self.parameters():
            p.data.uniform_(init_low, init_high)
            
    def forward(self, state):
        return self.forward_block(state)
    
    def load_data(self, train_data_dir, train_params) -> Optional[DataLoader]:
        filenames = os.listdir(train_data_dir)
        sars = []
        for filename in filenames:
            if filename.split(".")[-1] != 'pkl':
                continue
            with open(os.path.join(train_data_dir, filename), "rb") as file:
                sars.extend(dill.load(file))
        if not sars:
            return None
        train_ds = StateActionValueDataset(sars)
        train_dl = DataLoader(train_ds, train_params.get('batch_size', 32), shuffle=True)
        return train_dl
    
    def get_optim(self, train_params):
        learning_rate = train_params.get("learning_rate", 0.001)
        if train_params['optim'] == "Adam":
            return optim.Adam(self.parameters(), lr=learning_rate)
        else:
            raise ValueError("optim must be Adam currently")

    def get_train_params(self, filename):
        train_params = {}
        with open(filename, "r") as train_params_file:
            for line in train_params_file.readlines():
                split_line = line.strip().split("=")
                if len(split_line) != 2:
                    print(f"Encountered bad line while loading train_params: {line}, skipping for now")
                else:
                    train_params[split_line[0]] = split_line[1]

        if 'learning_rate' in train_params:
            train_params['learning_rate'] = float(train_params['learning_rate'])
        if 'epochs' in train_params:
            train_params['epochs'] = int(train_params['epochs'])
        if 'keep_training' in train_params:
            train_params['keep_training'] = bool(train_params['keep_training'])
        
        train_params['optim'] = self.get_optim(train_params)

        print(train_params)
        
        return train_params
    
    def compute_loss(self, preds, actuals):
        return nn.MSELoss()(preds, actuals)

    def train_all(self,
                  train_data_dir,
                  train_params_filename,
                 ):
        
        round = 0
        while True:
            
            train_params = self.get_train_params(train_params_filename)

            if not train_params.get('keep_training', True):
                print("Training ending.")
                return
            
            epochs, optimizer = train_params.get('epochs', 1), train_params['optim']

            if train_params.get('verbose', 1) >= 1:
                print(f"Starting round {round}")

            train_dl = self.load_data(train_data_dir, train_params)
            if train_dl is None:
                wait_time = train_params.get("wait_time", 10)
                print(f"Found no data in file, waiting now for {wait_time} seconds")
                time.sleep(wait_time)
                continue 

            for epoch in range(epochs):
                running_loss = 0
                total_data = 0

                for batch in train_dl:
                    self.train()
                    self.zero_grad()

                    states, actions, values = batch
                    batch_size = len(values)

                    pred_values = torch.gather(self.forward(states), dim=1, index=actions.unsqueeze(1))
                    loss = self.compute_loss(pred_values, values)

                    loss.backward()
                    optimizer.step()

                    running_loss += (loss * batch_size).item()
                    total_data += batch_size
                
                if train_params.get('verbose', 1) >= 1:
                    print(f"Epoch {epoch} Training Loss: {running_loss / total_data}")
            
            self.save_model()

            round += 1
    
    def save_model(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        torch.save(self, os.path.join(dir_path, 'model.pt'))
        print("Saved new copy of model.")
                
if __name__ == '__main__':
    model = StateActionNetwork(loss_function=nn.MSELoss(), input_size=40, output_size=4, init_low=-20.0, init_high=20.0)
    print(torch.__version__)
    dir_path = os.path.dirname(os.path.realpath(__file__))
    torch.save(model, os.path.join(dir_path, 'model.pt'))
