import multiprocessing
from consts import *
from world import *
import time
import random
import sys
sys.path.append('../data')
sys.path.append('../generator')
sys.path.append('../RL')
from generator import SimpleGenerator
import postprocessor

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
    # run postprocessing
    postprocessor.postProcess(dataFolder)


def runTraining():
    #TODO(rajatmittal)
    while True:
        pass

def simDriver(num_cores, train_cores, nSims):

    print('using %d threads' % num_cores)

    trainWorkers = []
    for i in range(train_cores): # number of training processes
        print("running training process %d" % i)
        trainWorkers.append(multiprocessing.Process(target=runTraining))
        trainWorkers[i].start()
    batchSize = num_cores-train_cores
    nSims = list(range(nSims))
    for simID in range(0, len(nSims), batchSize):
        currSims = nSims[simID:simID+batchSize]
        workers = []
        for i in currSims:
            dataFolder = f"run{i}"
            workers.append(multiprocessing.Process(target=runSim, args=(dataFolder,)))
        for worker in workers:
            worker.start()
        for worker in workers:
            worker.join()
    
    for worker in trainWorkers:
        worker.join()

if __name__ == "__main__":
    simDriver(num_cores=4, train_cores=1, nSims=10)
    print("Simulation Driver Complete")