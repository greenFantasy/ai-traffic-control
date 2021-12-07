import sys
import dill
import pandas as pd
import numpy as np
from typing import List
import torch
import os
import datetime

# save_path = os.path.join("traindata", f"{str(datetime.datetime.now()).replace(' ', '_')}.pkl")

# vehicle_intersection_times = dill.load(open("../data/vehicle_intersection_times.pkl", "rb"))
# actions = dill.load(open("../data/controller_actions.pkl", "rb"))
# snapshot_data = dill.load(open("../data/snapshot_data.pkl", "rb"))

# snapshot_data = [(-1.0, torch.zeros(8)) for _ in range(4)] + snapshot_data
# snapshot_time_to_index = {t[0]:i for i,t in enumerate(snapshot_data)}

REWARD_INTERVAL = 10

def get_reward(action_time, vehicle_intersection_times):
    wait_times: List[float] = []
    for r in vehicle_intersection_times:
        car_entrance_time, car_exit_time = r[2], r[3] if r[3] else float("inf")
        if car_entrance_time <= action_time + REWARD_INTERVAL and car_exit_time >= action_time:
            start_time: float = max(car_entrance_time, action_time - REWARD_INTERVAL)
            end_time: float = min(car_exit_time, action_time + REWARD_INTERVAL)
            wait_times.append(end_time - start_time)
    return -np.mean(wait_times)

def get_env_state(action_time, snapshot_data, snapshot_time_to_index):
    i = snapshot_time_to_index[action_time]
    if i < 4:
        assert "Accessing snapshots prior to time zero not allowed."
    else:
        return torch.hstack([x[1] for x in snapshot_data[i-4:i+1]])

# all_sars = []
# state = get_env_state(actions[0][0], snapshot_data, snapshot_time_to_index)
# for a in actions[1:]:
#     next_state = get_env_state(a[0], snapshot_data, snapshot_time_to_index)
#     action = a[1]
#     reward = get_reward(a[0], vehicle_intersection_times)
#     all_sars.append((state, action, reward, next_state))
#     state = next_state

# with open(save_path, 'wb') as filehandler:           
#     dill.dump(all_sars, filehandler)

def post_process(dataFolder):
    save_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "traindata", f"{dataFolder}.pkl")
    dataFolder = dataFolder + "/"
    dataPathPrefix = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../data', dataFolder)
    vehicle_intersection_times = dill.load(open(dataPathPrefix + 'vehicle_intersection_times' + ".pkl", "rb"))
    actions = dill.load(open(dataPathPrefix + 'controller_actions' + ".pkl", "rb"))
    snapshot_data = dill.load(open(dataPathPrefix + 'snapshot_data' + ".pkl", "rb"))
    snapshot_data = [(-1.0, torch.zeros(8)) for _ in range(4)] + snapshot_data
    snapshot_time_to_index = {t[0]:i for i,t in enumerate(snapshot_data)}
    all_sars = []
    state = get_env_state(actions[0][0], snapshot_data, snapshot_time_to_index)
    for a in actions[1:]:
        next_state = get_env_state(a[0], snapshot_data, snapshot_time_to_index)
        action = a[1]
        reward = get_reward(a[0], vehicle_intersection_times)
        all_sars.append((state, action, reward, next_state))
        state = next_state

    with open(save_path, 'wb') as filehandler:           
        dill.dump(all_sars, filehandler)
