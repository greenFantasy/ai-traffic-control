import multiprocessing
from consts import *
from world import *
import time
import random
import sys
sys.path.append('../data')
sys.path.append('../generator')
from generator import SimpleGenerator

def runSim(dataFolder):
    world = DedicatedLeftTurnIntersectionWorld(split_times=[8.,8.,8.,8.], dataFolder=dataFolder)
    world.set_spawnable_paths()
    world.add_generator(SimpleGenerator(world, {"p": 0.01}))
    for i in range(1000):
        world.play()
        # if i % 100 == 0:
        #     print(i)
    print("Simulation complete")
    world.close()

def simDriver(num_cores):

    print('using %d threads' % num_cores)

    workers = []
    for i in range(num_cores):
        dataFolder = f"run{i}"
        workers.append(multiprocessing.Process(target=runSim, args=(dataFolder,)))
    for worker in workers:
        worker.start()

    for worker in workers:
        worker.join()

if __name__ == "__main__":
    simDriver(num_cores=4)
    print("Simulation Driver Complete")