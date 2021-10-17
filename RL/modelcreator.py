import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
import torchvision
from torchvision import models
import random
# from flags import CUDA
from tqdm import tqdm
import os

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
                 init_low=-0.001,
                 init_high=0.001,
                 cuda=False,
                ):

        super(StateActionNetwork, self).__init__()
        # self.input_size = input_size

        self.cuda = cuda

        self.init_low = init_low
        self.init_high = init_high

        # self.resnet = models.resnet18(pretrained=False)
        # self.resnet.conv1 = nn.Conv2d(13, 64, kernel_size=(7, 7), stride=(2, 2), padding=(3, 3), bias=False)
        # self.resnet_head = nn.Sequential(*list(self.resnet.children())[:-1])
        # del self.resnet
        # self.flatten = nn.Flatten()
        # self.fc = nn.Linear(518, 1)

        self.init_parameters(init_low, init_high)

    def init_parameters(self, init_low, init_high):
        for p in self.parameters():
            p.data.uniform_(init_low, init_high)
            
    def forward(self, state):
        dev = "cuda" if self.cuda else "cpu"
        
        assert tuple(state.shape[1:]) == (6,), f'Environment state is size {state.shape} in forward, expected {}'
    

        return values

    def train_all(self,
                  train_data,
                  validation_data=None,
                  epochs=20,
                  learning_rate=1e-4,
                  batch_size=1,
                  opt=torch.optim.SGD,
                  printing=True,
                  per_epoch=20,
                  loss_function=None,
                  silent=False
                 ):
        if self.cuda:
          train_data = ((train_data[0][0].float().cuda(), train_data[0][1].float().cuda()), train_data[1].float().cuda())
          if validation_data is not None:
            validation_data = ((validation_data[0][0].float().cuda(), validation_data[0][1].float().cuda()), validation_data[1].float().cuda())
        else:
          train_data = ((train_data[0][0].float(), train_data[0][1].float()), train_data[1].float())
          if validation_data is not None:
            validation_data = ((validation_data[0][0].float(), validation_data[0][1].float()), validation_data[1].float())

        if loss_function is not None:
            self.loss_function = loss_function

        # Use Adam to optimize the parameters
        optim = opt(self.parameters(), lr=learning_rate, momentum=0.9)

        if validation_data is not None:
            best_validation_loss = float('inf')
            validation_loss = self.evaluate(validation_data, metrics=self.loss_function)
            if validation_loss < best_validation_loss:
                best_validation_loss = validation_loss
        # Run the optimization for multiple epochs

        states, values = train_data
        num_batches = int(np.ceil(len(states[0]) / batch_size))
        # self.best_model = copy.deepcopy(self.state_dict()

        self.train()
        initial_train_loss = self.evaluate((states, values), self.loss_function)
        print("Initial loss: %.6f" % initial_train_loss)

        for epoch in range(epochs):
            # Shuffling, training data, can remove if necessary
            # Can also add to inner loop instead to change mini-batches in each epoch
            shuffled_idxs = np.arange(len(states[0]))
            np.random.shuffle(shuffled_idxs)
            values = values[shuffled_idxs]
            states = states[0][shuffled_idxs], states[1][shuffled_idxs]

            self.train()
            total = 0
            running_loss = 0.0

            if False and printing and not silent:
                iterator = range(num_batches)
                # iterator = tqdm(range(num_batches))
            else:
                iterator = range(num_batches)

            for i in iterator:

                # Zero the parameter gradients
                self.zero_grad()

                s1 = states[0][i*batch_size:(i+1)*batch_size]
                s2 = states[1][i*batch_size:(i+1)*batch_size]
                y = values[i*batch_size:(i+1)*batch_size]

                # Run forward pass and compute loss along the way.
                logits = self.forward((s1, s2), a=None,train=True)

                loss = self.loss_function(logits, y)

                # Perform backpropagation
                loss.backward()
                # Update parameters
                optim.step()

                # Training stats
                total += 1
                running_loss += loss.item()


            # Evaluate and track improvements on the validation dataset
            if validation_data is not None:
                validation_loss = self.evaluate(validation_data, metrics=self.loss_function)
                if validation_loss < best_validation_loss:
                    best_validation_loss = validation_loss
                    # self.best_model = copy.deepcopy(self.state_dict())

            train_loss = self.evaluate((states, values), self.loss_function)

            if printing and ((epoch+1) % per_epoch == 0 or epoch==0) and not silent:
                print(f'Epoch {epoch}\t' +
                      f'\tTrain Loss: {train_loss:.6f}' +
                      f'\t Mean L1 Loss: {torch.abs(logits - y).mean():.6f}' +
                      (f'\tVal Loss: {validation_loss:.4f}' if validation_data is not None else '')
                      )

    def evaluate(self, dataset, metrics):
        self.eval()
        states, values = dataset
        if isinstance(metrics, list):
            preds = self.forward(states, a=None, train=False)
            return [metric(preds, values) for metric in metrics]
        return metrics(self.forward(states, a=None, train=False), values)

if __name__ == '__main__':
    model = StateActionNetwork(loss_function=nn.MSELoss(), init_low=-0.1, init_high=0.1, cuda=CUDA)
    print(torch.__version__)
    dir_path = os.path.dirname(os.path.realpath(__file__))
    torch.save(model, os.path.join(dir_path, 'model.pt'))
