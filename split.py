import numpy as np

from numpy import ceil
from collections import deque
from dataclasses import dataclass

MY_EPSILON = 1e-10


@dataclass
class ClientSplit:
    demand: float = 0.0
    service_time: float = 0.0
    d0_x: float = 0.0
    dx_0: float = 0.0
    dnext: float = -np.inf


# Simple Deque which is used for all Linear Split algorithms
@dataclass
class TrivialDeque:
    def __init__(self, nb_elements, first_node):
        self.my_deque = deque([first_node] + [None]*(nb_elements - 1))
        self.index_front = 0
        self.index_back = 0

    def pop_front(self):
        self.index_front += 1

    def pop_back(self):
        self.index_back -= 1

    def push_back(self, i):
        self.index_back += 1
        self.my_deque[self.index_back] = i

    def get_front(self):
        return self.my_deque[self.index_front]

    def get_next_front(self):
        return self.my_deque[self.index_front + 1]

    def get_back(self):
        return self.my_deque[self.index_back]

    def reset(self, first_node):
        self.my_deque[0] = first_node
        self.index_back = 0
        self.index_front = 0

    def size(self):
        return self.index_back - self.index_front + 1


class Split:
    def __init__(self, params):
        self.params = params
        self.max_vehicles = 0
        self.cli_split = []
        self.potential = []
        self.pred = []
        self.sum_distance = []
        self.sum_load = []
        self.sum_service = []

        # Initialize structures
        self.cli_split = [ClientSplit() for _ in range(params.nb_clients + 1)]
        self.sum_distance = [0.0] * (params.nb_clients + 1)
        self.sum_load = [0.0] * (params.nb_clients + 1)
        self.sum_service = [0.0] * (params.nb_clients + 1)

        self.potential = [[1e30] * (params.nb_clients + 1) for _ in range(params.nb_vehicles + 1)]
        self.pred = [[0] * (params.nb_clients + 1) for _ in range(params.nb_vehicles + 1)]

    # To be called with i < j only
    # Computes the cost of propagating the label i until j
    def propagate(self, i, j, k):
        return (
            self.potential[k][i]
            + self.sum_distance[j]
            - self.sum_distance[i + 1]
            + self.cli_split[i + 1].d0_x
            + self.cli_split[j].dx_0
            + self.params.penalty_capacity * max(self.sum_load[j] - self.sum_load[i] - self.params.vehicle_capacity, 0.0)
        )

    # Tests if i dominates j as a predecessor for all nodes x >= j+1
    # We assume that i < j
    def dominates(self, i, j, k):
        return (
            self.potential[k][j]
            + self.cli_split[j + 1].d0_x
            > self.potential[k][i]
            + self.cli_split[i + 1].d0_x
            + self.sum_distance[j + 1]
            - self.sum_distance[i + 1]
            + self.params.penalty_capacity * (self.sum_load[j] - self.sum_load[i])
        )

    # Tests if j dominates i as a predecessor for all nodes x >= j+1
    # We assume that i < j
    def dominates_right(self, i, j, k):
        return (
            self.potential[k][j] + self.cli_split[j + 1].d0_x
            < self.potential[k][i]
            + self.cli_split[i + 1].d0_x
            + self.sum_distance[j + 1]
            - self.sum_distance[i + 1]
            + MY_EPSILON
        )

    # Split for unlimited fleet
    def split_simple(self, indiv):

        # Reinitialize the potential structures
        self.potential[0][0] = 0
        for i in range(1, self.params.nb_clients + 1):
            self.potential[0][i] = 1e30

        # MAIN ALGORITHM -- Simple Split using Bellman's algorithm in topological order
        # This code has been maintained as it is very simple and can be easily adapted
        # to a variety of constraints, whereas the O(n) Split has a more restricted application scope
        if self.params.is_duration_constraint:
            for i in range(self.params.nb_clients):
                load = 0.0
                distance = 0.0
                service_duration = 0.0
                j = i + 1  # Initialization before the while loop
                while (j < self.params.nb_clients) and (load <= 1.5 * self.params.vehicle_capacity):
                    load += self.cli_split[j].demand
                    service_duration += self.cli_split[j].service_time
                    if j == i + 1:
                        distance += self.cli_split[j].d0_x
                    else:
                        distance += self.cli_split[j - 1].dnext

                    cost = (
                        distance
                        + self.cli_split[j].dx_0
                        + self.params.penalty_capacity * max(load - self.params.vehicle_capacity, 0)
                        + self.params.penalty_duration
                        * max(distance + self.cli_split[j].dx_0 + service_duration - self.params.duration_limit, 0)
                    )

                    if self.potential[0][i] + cost < self.potential[0][j]:
                        self.potential[0][j] = self.potential[0][i] + cost
                        self.pred[0][j] = i
                    j += 1
        else:
            queue = TrivialDeque(self.params.nb_clients + 1, 0)

            for i in range(1, self.params.nb_clients + 1):
                # The front is the best predecessor for i
                self.potential[0][i] = self.propagate(queue.get_front(), i, 0)
                self.pred[0][i] = queue.get_front()

                if i < self.params.nb_clients:
                    # If i is not dominated by the last of the pile
                    if not self.dominates(queue.get_back(), i, 0):
                        # then i will be inserted, need to remove whoever is dominated by i
                        while (queue.size() > 0) and (self.dominates_right(queue.get_back(), i, 0)):
                            queue.pop_back()
                        queue.push_back(i)

                    # Check iteratively if front is dominated by the next front
                    while (
                        queue.size() > 1
                        and self.propagate(queue.get_front(), i + 1, 0)
                        > self.propagate(queue.get_next_front(), i + 1, 0) - MY_EPSILON
                    ):
                        queue.pop_front()

        if self.potential[0][self.params.nb_clients] > 1e29:
            raise Exception("ERROR: No Split solution has been propagated until the last node")

        # Filling the chromR structure
        for k in range(self.params.nb_vehicles - 1, self.max_vehicles - 1, -1):
            indiv.chromR[k].clear()

        end = self.params.nb_clients
        for k in range(self.max_vehicles - 1, -1, -1):
            indiv.chromR[k].clear()
            begin = self.pred[0][end]
            for ii in range(begin, end):
                indiv.chromR[k].append(indiv.chromT[ii])
            end = begin

        # Return OK in case the Split algorithm reached the beginning of the routes
        return end == 0

    # Split for limited fleet
    def split_lf(self, indiv):
        # Initialize the potential structures
        self.potential[0][0] = 0
        for k in range(self.max_vehicles + 1):
            for i in range(1, self.params.nb_clients + 1):
                self.potential[k][i] = 1e30

        # MAIN ALGORITHM -- Simple Split using Bellman's algorithm in topological order
        # This code has been maintained as it is very simple and can be easily adapted
        # to a variety of constraints, whereas the O(n) Split has a more restricted application scope
        if self.params.is_duration_constraint:
            for k in range(self.max_vehicles):
                for i in range(k, self.params.nb_clients):
                    if self.potential[k][i] >= 1e29:
                        break

                    load = 0.0
                    service_duration = 0.0
                    distance = 0.0
                    for j in range(i + 1, self.params.nb_clients + 1):
                        load += self.cli_split[j].demand
                        service_duration += self.cli_split[j].service_time

                        if j == i + 1:
                            distance += self.cli_split[j].d0_x
                        else:
                            distance += self.cli_split[j - 1].dnext

                        cost = (
                            distance
                            + self.cli_split[j].dx_0
                            + self.params.penalty_capacity * max(load - self.params.vehicle_capacity, 0.0)
                            + self.params.penalty_duration
                            * max(distance + self.cli_split[j].dx_0 + service_duration - self.params.duration_limit, 0.0)
                        )

                        if self.potential[k][i] + cost < self.potential[k + 1][j]:
                            self.potential[k + 1][j] = self.potential[k][i] + cost
                            self.pred[k + 1][j] = i

        # MAIN ALGORITHM -- Without duration constraints in O(n), from "Vidal, T. (2016). Split algorithm in O(n) for the capacitated vehicle routing problem. C&OR
        else:
            queue = TrivialDeque(self.params.nb_clients + 1, 0)

            for k in range(self.max_vehicles):
                # in the Split problem there is always one feasible solution with k routes that reaches the index k in the tour
                queue.reset(k)

                # The range of potentials < 1.29 is always an interval
                # The size of the queue will stay >= 1 until we reach the end of this interval
                for i in range(k + 1, self.params.nb_clients + 1):
                    if queue.size() <= 0:
                        break

                    # The front is the best predecessor for i
                    self.potential[k + 1][i] = self.propagate(queue.get_front(), i, k)
                    self.pred[k + 1][i] = queue.get_front()

                    if i < self.params.nb_clients:

                        #  If i is not dominated by the last of the pile
                        if not self.dominates(queue.get_back(), i, k):
                            # then i will be inserted, need to remove whoever he dominates
                            while queue.size() > 0 and self.dominates_right(queue.get_back(), i, k):
                                queue.pop_back()
                            queue.push_back(i)

                        # Check iteratively if front is dominated by the next front
                        while (
                            queue.size() > 1
                            and self.propagate(queue.get_front(), i + 1, k)
                            > self.propagate(queue.get_next_front(), i + 1, k) - MY_EPSILON
                        ):
                            queue.pop_front()

        if self.potential[self.max_vehicles][self.params.nb_clients] > 1e29:
            raise Exception("ERROR: No Split solution has been propagated until the last node")

        # It could be cheaper to use a smaller number of vehicles
        min_cost = self.potential[self.max_vehicles][self.params.nb_clients]
        nb_routes = self.max_vehicles

        for k in range(1, self.max_vehicles):
            if self.potential[k][self.params.nb_clients] < min_cost:
                min_cost = self.potential[k][self.params.nb_clients]
                nb_routes = k

        # Filling the chromR structure
        for k in range(self.params.nb_vehicles - 1, nb_routes - 1, -1):
            indiv.chromR[k].clear()

        end = self.params.nb_clients
        for k in range(nb_routes - 1, -1, -1):
            indiv.chromR[k].clear()
            begin = self.pred[k + 1][end]
            for ii in range(begin, end):
                indiv.chromR[k].append(indiv.chromT[ii])
            end = begin

        # Return OK in case the Split algorithm reached the beginning of the routes
        return end == 0

    # General Split function (tests the unlimited fleet,
    # and only if it does not produce a feasible solution, runs the Split algorithm for limited fleet)
    def general_split(self, indiv, nb_max_vehicles):
        # Do not apply Split with fewer vehicles than the trivial (LP) bin packing bound
        self.max_vehicles = max(nb_max_vehicles, ceil(self.params.total_demand / self.params.vehicle_capacity))

        # Initialization of the data structures for the linear split algorithms
        # Direct application of the code located at https://github.com/vidalt/Split-Library
        for i in range(1, self.params.nb_clients + 1):
            self.cli_split[i].demand = self.params.cli[indiv.chromT[i - 1]].demand
            self.cli_split[i].service_time = self.params.cli[indiv.chromT[i - 1]].service_duration
            self.cli_split[i].d0_x = self.params.time_cost[0][indiv.chromT[i - 1]]
            self.cli_split[i].dx_0 = self.params.time_cost[indiv.chromT[i - 1]][0]

            if i < self.params.nb_clients:
                self.cli_split[i].dnext = self.params.time_cost[indiv.chromT[i - 1]][indiv.chromT[i]]
            else:
                self.cli_split[i].dnext = -1e30

            self.sum_load[i] = self.sum_load[i - 1] + self.cli_split[i].demand
            self.sum_service[i] = self.sum_service[i - 1] + self.cli_split[i].service_time
            self.sum_distance[i] = self.sum_distance[i - 1] + self.cli_split[i - 1].dnext

        # We first try the simple split, and then the Split with limited fleet if this is not successful
        if self.split_simple(indiv) == 0:
            self.split_lf(indiv)

        # Build up the rest of the Individual structure
        indiv.evaluate_complete_cost(self.params)
