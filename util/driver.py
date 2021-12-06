import multiprocessing
import time
import random
import sys
sys.path.append('../data')
sys.path.append('../generator')
sys.path.append('../RL')
sys.path.append('../sim')
import torch
from modelcreator import StateActionNetwork
import postprocessor
import sim_driver
import datetime

def runSim(dataFolder):
    sim_driver.run_simulation(dataFolder)
    postprocessor.post_process(dataFolder)

def runTraining():
    model = torch.load('../RL/model.pt')
    model.train_all("../RL/traindata", "../RL/trainparams.txt")

def driver(num_cores, train_cores):

    print('using %d threads' % num_cores)

    trainWorkers = []
    for i in range(train_cores): # number of training processes
        print("running training process %d" % i)
        trainWorkers.append(multiprocessing.Process(target=runTraining))
        trainWorkers[i].start()
    
    simNumber = 0
    while True:
        currSims = []
        for i in range(num_cores - train_cores): # number of simulation processes
            currSims.append(simNumber)
            simNumber += 1
        workers = []
        for i in currSims:
            timestamp = datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
            dataFolder = f"{timestamp}_run{i}"
            workers.append(multiprocessing.Process(target=runSim, args=(dataFolder,)))
            print("running sim process %d" % i)
        for worker in workers:
            worker.start()
        for worker in workers:
            worker.join()
    
    for worker in trainWorkers:
        worker.join()

if __name__ == "__main__":
    driver(num_cores=4, train_cores=1)
    print("Driver Complete")