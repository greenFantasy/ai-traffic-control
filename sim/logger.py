from consts import *

def init(world):
    global logger
    logger = Logger(world)

class Logger:
    def __init__(self, world) -> None:
        self.world = world
    
    def logVehicleSpawn(self, vehicle) -> None:
        pass

    def logVehicleDespawn(self, vehicle) -> None:
        pass

    def logTrafficLightChange(self, traffic_light, state_old, state_new) -> None:
        pass
