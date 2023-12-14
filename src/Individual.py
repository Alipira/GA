import numpy as np
from collections import namedtuple


class Individual:
    def __init__(self, n_vehicle, n_customer, distance_matrix):
        # construct chromosome
        self.chrom_vehicle = np.full(shape=(n_vehicle, n_customer), fill_value=np.nan)
        self.chrom_customer = np.zeros(shape=n_customer, dtype=int)
        self.succesors = np.zeros(shape=n_customer + 1, dtype=int)
        self.predesuccesors = np.zeros(shape=n_customer + 1, dtype=int)

        # construct costs
        self.penallized_cost = 0  # 1e30
        self.nb_routes = 0
        self.distance = 0.0
        self.capacity_excess = 0.0
        self.distance_excess = 0.0
        self.is_feasible = False
        self.dist_matrix = distance_matrix

    def evaluate_cost(self, ):
        for i in range(len(self.n_vehicle)):
            if not np.any(self.chrom_vehicle):
                self.distance = self.dist_matrix[0, self.chrom_vehicle[i, 0]] #FIXME: in c++ distance is different from self.distance
                load = client_list[self.chrom_vehicle[i, 0]].demand
                # services = client_list[self.chrom_vehicle[i, 0]].service_duration
                self.predesuccesors[self.chrom_vehicle[i, 0]] = 0

                for j in range(len(self.chrom_vehicle)):
                    self.distance += self.dist_matrix[self.chrom_vehicle[i, j-1], self.chrom_vehicle[i, j]]
                    load += client_list[self.chrom_vehicle[i, j]].demand
                    # services += client_list[self.chrom_vehicle[i, j]].service_duration
                    self.predesuccesors[self.chrom_vehicle[i, j]] = self.chrom_vehicle[i, j-1]
                    self.succesors[self.chrom_vehicle[i, j-1]] = self.chrom_vehicle[i, j]

                self.succesors[self.chrom_vehicle[i, len(self.chrom_vehicle[i]) - 1]] = 0  # FIXME: IN C++ IS .size() it should be check
                self.distance += self.dist_matrix[self.chrom_vehicle[i, len(self.chrom_vehicle[i]) - 1], 0]
                self.nb_routes += 1
                if load > vehicle_capacity:
                    self.capacity_excess += load - vehicle_capacity

                if distance + services > duration_limit:
                    duration_excess += distance + services - duration_limit

    self.penallized_cost = self.distance + self.capacity_excess * penalty_capacity + duration_excess * penalty_duration
    self.is_feasible = (self.capacity_excess < my_epsilon and duration_excess < my_epsilon)
