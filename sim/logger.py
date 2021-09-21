from sim.consts import TrafficLightStates
from car import Car
from consts import *
from trafficlight import TrafficLight

def init(world):
    global logger
    logger = Logger(world)

class Logger:
    def __init__(self, world) -> None:
        self.world = world
    
    def logVehicleSpawn(self, vehicle : Car) -> None:
        pass

    def logVehicleDespawn(self, vehicle : Car) -> None:
        pass

    def logTrafficLightChange(self, traffic_light: TrafficLight, state_old: TrafficLightStates, state_new: TrafficLightStates) -> None:
        pass
