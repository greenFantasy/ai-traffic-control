import sys
import dill
import pandas as pd
import numpy as np
from typing import List

vehicle_intersection_times = dill.load(open("../data/vehicle_intersection_times.pkl", "rb"))
traffic_light_changes = pd.read_csv("../data/traffic_light_change.csv")
# print(traffic_light_changes["TimeStamp"])

REWARD_INTERVAL = 10

def get_reward(action_time, vehicle_intersection_times):
    wait_times: List[float] = []
    for r in vehicle_intersection_times:
        if r[2] <= action_time + REWARD_INTERVAL and r[3] >= action_time:
            start_time: float = max(r[2], action_time - REWARD_INTERVAL)
            end_time: float = min(r[3], action_time + REWARD_INTERVAL)
            wait_times.append(end_time - start_time)
    print(wait_times)
get_reward(10.0, vehicle_intersection_times)

get_reward(12.5, vehicle_intersection_times)

get_reward(14.0, vehicle_intersection_times)