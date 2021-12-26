import os
import dill
import torch

train_data_dir = '../data'
filename = '2021_12_25_21_31_08_run2/vehicle_intersection_times.pkl'

with open(os.path.join(train_data_dir, filename), "rb") as file:
    single_sim_sars = dill.load(file)
    print(single_sim_sars)