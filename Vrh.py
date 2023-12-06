import numpy as np


class Vrh:
    x = 0
    y = 0
    z = 0

    def __init__(self, x=0,y=0, z=0):
        self.x = x
        self.y = y
        self.z = z

    def to_arr(self):
        return np.array([self.x,self.y,self.z])