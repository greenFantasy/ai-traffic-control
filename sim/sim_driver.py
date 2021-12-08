from consts import *
from world import *
from generator import SimpleGenerator

def get_sim_parameters(filename):
    sim_params = {}
    with open(filename, "r") as sim_params_file:
        for line in sim_params_file.readlines():
            split_line = line.strip().split("=")
            if len(split_line) != 2:
                print(f"Encountered bad line while loading train_params: {line}, skipping for now")
            else:
                sim_params[split_line[0]] = split_line[1]

    if 'iterations' in sim_params:
        sim_params['iterations'] = int(sim_params['iterations'])

    return sim_params

def run_simulation(dataFolder):
    sim_params_filename = "../sim/simsettings.txt"
    sim_params = get_sim_parameters(sim_params_filename)
    world = DedicatedLeftTurnIntersectionWorld(float(sim_params['greedy_prob']), split_times=[8.,8.,8.,8.], dataFolder=dataFolder)
    world.set_spawnable_paths()
    world.add_generator(SimpleGenerator(world, {"p": 0.01}))
    for i in range(sim_params['iterations']):
        world.play()
    world.close()
    
