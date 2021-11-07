from consts import *
from io import BytesIO
import csv
import sys
import numpy as np
import dill
import os
sys.path.append('../data')

# https://stackoverflow.com/questions/41888080/python-efficient-way-to-add-rows-to-dataframe

def init(world, enable):
    global logger
    logger = Logger(world, enable)

dataPathPrefix = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../data/') # TODO (rajatmittal, shyamsai): Fix ugliness
roundingPrecision = 3

class Logger:
    def __init__(self, world, enable) -> None:
        self.world = world
        self.enabled = enable
        self.csv_writer_dict = {}
        self.np_array_dict = {}
        
    def logVehicleSpawn(self, vehicle) -> None:
        '''
        Logs Vehicle Spawn Times
        Saved in a CSV - vehicle_spawn.csv
        '''
        if not self.enabled:
            return
        dataName = 'vehicle_spawn' # HERE
        if dataName not in self.csv_writer_dict:
            # Initialize
            filename = dataPathPrefix+dataName+".csv"
            csvwriter = csv.writer(open(filename,'w', newline=''))
            fields = ["Vehicle_ID","Time_Spawn"] # HERE
            csvwriter.writerow(fields)
            self.csv_writer_dict[dataName] = csvwriter
        csvwriter = self.csv_writer_dict[dataName]
        data = [vehicle.id, round(self.world.time, roundingPrecision)] # 
        csvwriter.writerow(data)

    def logVehicleDespawn(self, vehicle) -> None:
        '''
        Logs Vehicle Despawn Times
        Saved in a CSV - vehicle_despawn.csv
        '''
        if not self.enabled:
            return
        dataName = 'vehicle_despawn'
        if dataName not in self.csv_writer_dict:
            # Initialize
            filename = dataPathPrefix+dataName+".csv"
            csvwriter = csv.writer(open(filename,'w', newline=''))
            fields = ["Vehicle_ID","Time_Despawn"]
            csvwriter.writerow(fields)
            self.csv_writer_dict[dataName] = csvwriter
        csvwriter = self.csv_writer_dict[dataName]
        data = [vehicle.id, round(self.world.time, roundingPrecision)]
        csvwriter.writerow(data)

    def logVehicleMovement(self, vehicleList) -> None:
        '''
        Logs Vehicle Despawn Times
        Saved in a CSV - vehicle_despawn.csv
        '''
        if not self.enabled:
            return
        dataName = 'vehicle_movement' # HERE
        if dataName not in self.csv_writer_dict:
            # Initialize
            filename = dataPathPrefix+dataName+".csv"
            csvwriter = csv.writer(open(filename,'w', newline=''))
            fields = ["Vehicle_Coords","TimeStamp"] # HERE
            csvwriter.writerow(fields)
            self.csv_writer_dict[dataName] = csvwriter
        csvwriter = self.csv_writer_dict[dataName]
        coords = []
        currTime = round(self.world.time, roundingPrecision)
        for vehicle in vehicleList:
            coords.append(vehicle.center)
        data = [coords, currTime]
        csvwriter.writerow(data)

    def logTrafficLightChange(self, traffic_light, state_old, state_new) -> None:
        if not self.enabled:
            return
        dataName = 'traffic_light_change' # HERE
        if dataName not in self.csv_writer_dict:
            # Initialize
            filename = dataPathPrefix+dataName+".csv"
            csvwriter = csv.writer(open(filename,'w', newline=''))
            fields = ["Traffic_Light_ID","State_Old","State_New", "TimeStamp"] # HERE
            csvwriter.writerow(fields)
            self.csv_writer_dict[dataName] = csvwriter
        csvwriter = self.csv_writer_dict[dataName]
        data = [traffic_light.id, state_old.name, state_new.name, round(self.world.time, roundingPrecision)] # HERE
        csvwriter.writerow(data)

    def logVehiclePathExit(self, vehicle, path, time_path_entered):
        if not self.enabled:
            return
        dataName = 'path_exit'
        if dataName not in self.csv_writer_dict:
            # Initialize
            filename = dataPathPrefix+dataName+'.csv'
            csvwriter = csv.writer(open(filename,'w', newline=''))
            fields = ["Path_ID","Vehicle_ID","Time_Spent","Average_Speed"]
            csvwriter.writerow(fields)
            self.csv_writer_dict[dataName] = csvwriter
        csvwriter = self.csv_writer_dict[dataName]
        # Measure time spent on path (Time_spent_on_path) 
        # Average Speed on Path (Time_spent_on_path / path_length (maxPos))
        time_spent = self.world.time - time_path_entered
        average_speed = time_spent / path.parametrization.max_pos
        data = [path.id, vehicle.id, round(time_spent, roundingPrecision), average_speed]
        csvwriter.writerow(data)

    def logSensorData(self, sensor): #Currently only accepts scalar sensor data
        if not self.enabled:
            return
        dataName = 'sensor_data'
        if dataName not in self.csv_writer_dict:
            # Initialize
            filename = dataPathPrefix+dataName+".csv"
            csvwriter = csv.writer(open(filename,'w', newline=''))
            fields = ["Sensor_ID","SensorData","TimeStamp"]
            csvwriter.writerow(fields)
            self.csv_writer_dict[dataName] = csvwriter
        csvwriter = self.csv_writer_dict[dataName]
        data = [sensor.id, sensor.get_data(),round(self.world.time, roundingPrecision)]
        csvwriter.writerow(data)

    def logSaveWorld(self, world):
        worldSavePath = dataPathPrefix + "worldsave" + ".pkl"
        with open(worldSavePath, 'wb') as filehandler:
            dill.dump(world, filehandler)
