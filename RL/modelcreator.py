import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset, WeightedRandomSampler
from typing import Optional, List, Tuple
from sklearn.model_selection import train_test_split
import os
import dill
import time
import datetime
import itertools
from evals import * # Evaluation metrics for model.

def construct_sequential(layer_sizes):
    return nn.Sequential(*([nn.Flatten()] + list(itertools.chain(*[[nn.Linear(l1, l2), nn.LeakyReLU()] \
        for l1,l2 in zip(layer_sizes[:-1], layer_sizes[1:])]))[:-1]))

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

def get_geometric_sequence_tensor(ratio, length, descending=True):
    """
    if descending, that value at start of tensor is 1 and then value at end of tensor is ratio^(length - 1), otherwise reverse
    """
    sequence = torch.ones(length)
    if descending:
        for i in range(1, length):
            sequence[i] = ratio * sequence[i-1]
    else:
        for i in range(length - 2, -1, -1):
            sequence[i] = ratio * sequence[i+1]
    return sequence

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

        layers = construct_sequential([self.input_size, 512, 256, 256, 256, 256, self.output_size])
        self.forward_block = nn.Sequential(*layers)

        self.optim = None

        # self.init_parameters(init_low, init_high)

    def init_parameters(self, init_low, init_high):
        for p in self.parameters():
            p.data.uniform_(init_low, init_high)
            
    def forward(self, state):
        return self.forward_block(state)
    
    def archive_filename(self, train_data_dir, filename):
        # Assuming these are accurate
        archive_data_dir = "../RL/archivedata"
        old_filepath = os.path.join(train_data_dir, filename)
        new_filepath = os.path.join(archive_data_dir, filename)
        os.replace(old_filepath, new_filepath)

    def sort_files(self, file_list, reverse=False):
        # Assume files have the format "'%Y_%m_%d_%H_%M_%S_run#'.pkl"
        sort_list = []
        for filename in file_list:
            split_filename = filename.split("_")[:-1]
            if len(split_filename) != 6:
                continue
            date_time = datetime.datetime(*list(map(int, split_filename)))
            sort_list.append((date_time, filename))
        sort_list.sort(key=lambda x: x[0], reverse=reverse)
        return [x[1] for x in sort_list]
    
    def archive_data(self, train_data_dir) -> None:
        filenames = self.sort_files(os.listdir(train_data_dir))
        to_archive = filenames[:-40]
        for filename in to_archive:
            self.archive_filename(train_data_dir, filename)
    
    def load_data(self, train_data_dir, train_params) -> Tuple[Optional[DataLoader], Optional[DataLoader]]:
        filenames = self.sort_files(os.listdir(train_data_dir))
        sars = []
        lengths = []
        if filenames:
            print(f"Training with {filenames[0]} up to {filenames[-1]}")
        for filename in filenames:
            if filename.split(".")[-1] != 'pkl':
                continue
            with open(os.path.join(train_data_dir, filename), "rb") as file:
                single_sim_sars = dill.load(file)
                lengths.append(len(single_sim_sars))
                sars.extend(single_sim_sars)
        if not sars:
            return None, None
        batch_size = train_params.get('batch_size', 32)
        # weights = torch.repeat_interleave(get_geometric_sequence_tensor(train_params['sampling_ratio'], len(filenames), descending=False), \
        #     torch.tensor(lengths))
        # batch_sampler = WeightedRandomSampler(weights, batch_size, replacement=False)
        train_sars, val_sars = train_test_split(sars, test_size=0.1)
        train_ds = StateActionValueDataset(train_sars)
        val_ds = StateActionValueDataset(val_sars)
        train_dl = DataLoader(train_ds, batch_size, shuffle=True) # sampler=batch_sampler)
        val_dl = DataLoader(val_ds, batch_size, shuffle=True)
        return train_dl, val_dl
    
    def get_optim(self, train_params):
        learning_rate = train_params.get("learning_rate", 0.001)
        weight_decay = train_params.get('weight_decay', 0.)
        momentum = train_params.get('momentum', 0.0)
        if train_params['optim'] == "Adam":
            if isinstance(self.optim, optim.Adam):
                for g in self.optim.param_groups:
                    g['lr'] = learning_rate
                    g['weight_decay'] = weight_decay
            else:
                self.optim = optim.Adam(self.parameters(), lr=learning_rate, weight_decay=weight_decay)
        elif train_params['optim'] == "SGD":
            if isinstance(self.optim, optim.SGD):
                for g in self.optim.param_groups:
                    g['lr'] = learning_rate
                    g['momentum'] = momentum
                    g['weight_decay'] = weight_decay
            else:
                self.optim = optim.SGD(self.parameters(), lr=learning_rate, momentum=momentum, weight_decay=weight_decay)
        else:
            raise ValueError("optim must be Adam or SGD currently")
        print(self.optim)
        return self.optim

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
        if 'weight_decay' in train_params:
            train_params['weight_decay'] = float(train_params['weight_decay'])
        if 'epochs' in train_params:
            train_params['epochs'] = int(train_params['epochs'])
        if 'batch_size' in train_params:
            train_params['batch_size'] = int(train_params['batch_size'])
        if 'sampling_ratio' in train_params:
            train_params['sampling_ratio'] = float(train_params['sampling_ratio'])
        if 'momentum' in train_params:
            train_params['momentum'] = float(train_params['momentum'])
        if 'keep_training' in train_params:
            train_params['keep_training'] = bool(train_params['keep_training'])
        if 'print_every' in train_params:
            train_params['print_every'] = int(train_params['print_every'])        
        
        train_params['optim'] = self.get_optim(train_params)        
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
                pass
                # print(f"Starting round {round}")

            train_dl, val_dl = self.load_data(train_data_dir, train_params)
            if train_dl is None:
                wait_time = train_params.get("wait_time", 2)
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

                    pred_values = torch.gather(self.forward(states), dim=1, index=actions.unsqueeze(1)).squeeze(1)
                    loss = self.compute_loss(pred_values, values)

                    loss.backward()
                    optimizer.step()

                    running_loss += (loss * batch_size).item()
                    total_data += batch_size
                
                if train_params.get('verbose', 1) >= 1 and epoch % train_params.get('print_every', 200) == 0:
                    print(f"Epoch {epoch} Training Loss: {running_loss / total_data}")
                    tab_size = " " * len(f'Epoch {epoch}')
                    # print(f"{tab_size} Training MSE: {mse(self, train_dl)}")
                    print(f"{tab_size} Min Pred: {min_pred(self, train_dl)}")
                    print(f"{tab_size} Max Pred: {max_pred(self, train_dl)}")
                    print(f"{tab_size} Training MAE: {mae(self, train_dl)}")
                    print(f"{tab_size} Val MAE: {mae(self, val_dl)}")
                    print(f"{tab_size} Train Avg Pred: {average_pred(self, train_dl)}")
                    print(f"{tab_size} Val Avg Pred: {average_pred(self, val_dl)}")
            
            self.save_model()
            self.archive_data(train_data_dir)
            round += 1
    
    def save_model(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        torch.save(self, os.path.join(dir_path, 'model.pt'))
        # print("Saved new copy of model.")
                
if __name__ == '__main__':
    model = StateActionNetwork(loss_function=nn.MSELoss(), input_size=20*10, output_size=4, init_low=-0.1, init_high=0.1)
    print(torch.__version__)
    dir_path = os.path.dirname(os.path.realpath(__file__))
    torch.save(model, os.path.join(dir_path, 'model.pt'))
