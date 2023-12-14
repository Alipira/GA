import numpy as np

from numpy import ceil
from collections import deque
from typing import Union, Dict


class Split:
    def __init__(self, nb_elements, firstnode, parameters: Union[Dict, None]):
        clisplit = {
            'demand': 0, 'service_time': 0, 'd0_x': 0, 'dx_0': 0, 'dnext': 0
        }
        self.parameters = parameters
        self.v_clisplit = [None] * (nb_elements - 1)
        self.v_clisplit.insert(0, clisplit)
        self.trival = deque([0] * nb_elements)
        self.trival[0] = firstnode
        self.sum_distance = np.zeros(shape=())
        self.sum_load = np.zeros(shape=())
        self.sum_services = np.zeros(shape=())
        self.potential = np.zeros(shape=())
        self.pred = np.zeros(shape=())

    def general_split(self, max_nb_vehicle):
        max_vehicle = max(max_nb_vehicle, ceil(self.parameters['t_demand'] / self.parameters['vehicle_capacity']))

        for i in range(self.parameters['nb_client']):
            self.v_clisplit[i]['demand'] = 0


test = Split(5, 1)

for i in range(5):
    test.trival[0] += i

breakpoint()
