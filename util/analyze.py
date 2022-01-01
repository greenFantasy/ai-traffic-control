import pandas as pd
import dill 
import numpy as np
import os

def analyze(dirname, max_t=90.0):
    results = {}

    results['vehicle_intersection_times'] = vehicle_intersection_times = \
        dill.load(open(os.path.join(dirname, "vehicle_intersection_times.pkl"), "rb"))
    vehicle_spawn = pd.read_csv(os.path.join(dirname, "vehicle_spawn.csv"))
    results['vehicle_spawn_dict'] = vehicle_spawn_dict = \
        {car: spawn_time for car, spawn_time in vehicle_spawn.itertuples(index=False)}

    # Cars that spawn after max_t should not be considered as they have not been given enough time
    # to go through the intersection
    results['total_spawned'] = len([c for c in vehicle_spawn_dict if vehicle_spawn_dict[c] < max_t]) 
    results['total_through'] = len([c for c, its, ent, ext in vehicle_intersection_times if ext is not None and vehicle_spawn_dict[c] < max_t])
    results['mean_wait_time'] = np.mean([ext - ent for c, its, ent, ext in vehicle_intersection_times if ext is not None])
    return results