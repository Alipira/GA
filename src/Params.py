import math
import random
import time

from typing import List

from AlgorithmParameter import AlgorithmParameters, default_algorithm_parameters
from CircleSector import CircleSector

PI = math.pi


class Client:
    def __init__(self):
        self.coordX = 0.0
        self.coordY = 0.0
        self.polarAngle = 0.0
        self.serviceDuration = 0.0
        self.demand = 0.0


class Params:
    def __init__(
        self,
        x_coords: List[float],
        y_coords: List[float],
        dist_mtx: List[List[float]],
        service_time: List[float],
        demands: List[float],
        vehicleCapacity: float,
        durationLimit: float,
        nbVeh: int,
        isDurationConstraint: bool,
        verbose: bool,
        ap: AlgorithmParameters
    ):
        self.ap = ap
        self.isDurationConstraint = isDurationConstraint
        self.nbVehicles = nbVeh
        self.durationLimit = durationLimit
        self.vehicleCapacity = vehicleCapacity
        self.timeCost = dist_mtx
        self.verbose = verbose

        # This marks the starting time of the algorithm
        # self.startTime = time.clock()

        self.nbClients = len(demands) - 1  # Need to subtract the depot from the number of nodes
        self.totalDemand = 0.0
        self.maxDemand = 0.0
        # Initialize RNG
        random.seed(ap['seed'])  # FIXME:

        # Check if valid coordinates are provided
        self.areCoordinatesProvided = len(demands) == len(x_coords) and len(demands) == len(y_coords)

        self.cli = [Client() for _ in range(self.nbClients + 1)]

        for i in range(self.nbClients + 1):
            # If useSwapStar==false, x_coords and y_coords may be empty.
            if ap['useSwapStar'] == 1 and self.areCoordinatesProvided:
                self.cli[i].coordX = x_coords[i]
                self.cli[i].coordY = y_coords[i]
                self.cli[i].polarAngle = CircleSector.positive_mod(
                    32768. * math.atan2(self.cli[i].coordY - self.cli[0].coordY,
                                         self.cli[i].coordX - self.cli[0].coordX) / PI)
            else:
                self.cli[i].coordX = 0.0
                self.cli[i].coordY = 0.0
                self.cli[i].polarAngle = 0.0

            self.cli[i].serviceDuration = service_time[i]
            self.cli[i].demand = demands[i]
            if self.cli[i].demand > self.maxDemand:
                self.maxDemand = self.cli[i].demand
            self.totalDemand += self.cli[i].demand

        if verbose and ap['useSwapStar'] == 1 and not self.areCoordinatesProvided:
            print("----- NO COORDINATES HAVE BEEN PROVIDED, SWAP* NEIGHBORHOOD WILL BE DEACTIVATED BY DEFAULT")

        # Default initialization if the number of vehicles has not been provided by the user
        if self.nbVehicles == float('inf'):
            self.nbVehicles = int(1.3 * self.totalDemand / self.vehicleCapacity) + 3  # Safety margin
            if verbose:
                print("----- FLEET SIZE WAS NOT SPECIFIED: DEFAULT INITIALIZATION TO {} VEHICLES".format(self.nbVehicles))
        else:
            if verbose:
                print("----- FLEET SIZE SPECIFIED: SET TO {} VEHICLES".format(self.nbVehicles))

        # Calculation of the maximum distance
        self.maxDist = 0.0
        for i in range(self.nbClients + 1):
            for j in range(self.nbClients + 1):
                if self.timeCost[i][j] > self.maxDist:
                    self.maxDist = self.timeCost[i][j]

        # Calculation of the correlated vertices for each customer (for the granular restriction)
        self.correlatedVertices = [[] for _ in range(self.nbClients + 1)]
        setCorrelatedVertices = [set() for _ in range(self.nbClients + 1)]

        for i in range(1, self.nbClients + 1):
            orderProximity = sorted([(self.timeCost[i][j], j) for j in range(1, self.nbClients + 1) if i != j])

            for j in range(min(ap.nbGranular, self.nbClients - 1)):
                # If i is correlated with j, then j should be correlated with i
                setCorrelatedVertices[i].add(orderProximity[j][1])
                setCorrelatedVertices[orderProximity[j][1]].add(i)

        # Filling the vector of correlated vertices
        for i in range(1, self.nbClients + 1):
            self.correlatedVertices[i].extend(setCorrelatedVertices[i])

        # Safeguards to avoid possible numerical instability
        if 0.1 < self.maxDist < 100000:
            raise Exception("The distances are of very small or large scale. This could impact numerical stability. "
                            "Please rescale the dataset and run again.")
        if 0.1 < self.maxDemand < 100000:
            raise Exception("The demand quantities are of very small or large scale. This could impact numerical stability. "
                            "Please rescale the dataset and run again.")
        if self.nbVehicles < math.ceil(self.totalDemand / self.vehicleCapacity):
            raise Exception("Fleet size is insufficient to service the considered clients.")

        # A reasonable scale for the initial values of the penalties
        self.penaltyDuration = 1
        self.penaltyCapacity = max(0.1, min(1000., self.maxDist / self.maxDemand))

        if verbose:
            print("----- INSTANCE SUCCESSFULLY LOADED WITH {} CLIENTS AND {} VEHICLES".format(self.nbClients, self.nbVehicles))


# Example instantiation
if __name__ == "__main__":
    # Dummy data for testing
    algo_params = {
        'seed': 123,
        'useSwapStar': True  # Example parameter, define according to your scenario
    }

    params = Params(
        x_coords=[0, 1, 2],
        y_coords=[0, 1, 2],
        dist_mtx=[[0, 1, 2],[1, 0, 3],[2, 3, 0]],
        service_time=[0,5,10],
        demands=[0, 1, 2],
        vehicleCapacity=10,
        durationLimit=100,
        nbVeh=4,
        isDurationConstraint=True,
        verbose=True,
        ap=algo_params
    )
