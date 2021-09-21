from consts import *

class Sensor:
    """
    Every sensor (radar, camera, loop) will defined on an individual path, and can return
    certain information about cars along certain p-values in that path. For example,
    loop detectors will return binary information (is there a vehicle over the sensor or not?),
    while cameras can return exact p-value of vehicles in their range.

    Note: Some sensors like a camera might be responsible for looking at vehicles at many paths
    at once. In this case, our implementation is to create separate sensors for each path that
    that camera looks at.
    """
    def __init__(self, path, p_min, p_max, sensor_type='binary') -> None:
        """
        Arguments:
            path: Path() object which the sensor is placed on
            p_min, p_max: Range of p-values that the sensor can detect vehicles on
            sensor_type: Must be one of ['binary', 'count', 'all']
                TODO (rajatmittal): Currently all is not supported
        """
        self.path = path
        self.p_min = p_min
        self.p_max = p_max
        self.sensor_type = sensor_type

    def get_data(self):
        vehicles = self.path.get_vehicles(self.p_min, self.p_max)
        if self.sensor_type == 'binary':
            return 1 if vehicles else 0
        elif self.sensor_type == 'count':
            return len(vehicles)
        elif self.sensor_type == 'all':
            raise NotImplementedError
        else:
            raise ValueError(f"Invalid sensor_type {self.sensor_type}")
