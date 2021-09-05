from sensor import Sensor
from consts import *
from typing import Tuple

class Camera (Sensor):
    def __init__(self, range: float) -> None:
        super().__init__()
        self.range = range

    def get_range(self):
        return self.range