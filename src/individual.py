import random

class EvalIndiv:
    def __init__(self):
        self.penalized_cost = 0.0
        self.nb_routes = 0
        self.distance = 0.0
        self.capacity_excess = 0.0
        self.duration_excess = 0.0
        self.is_feasible = False


class Individual:
    def __init__(self, params, file_name=None):
        self.eval = EvalIndiv()
        self.chrom_t = list(range(1, params.nb_clients + 1))  # numpy array
        self.chrom_r = [[] for _ in range(params.nb_vehicles)]  # numpy array
        self.successors = [0] * (params.nb_clients + 1)
        self.predecessors = [0] * (params.nb_clients + 1)
        self.indivs_per_proximity = set()  # SortedSet from a third-party library like sortedcontainers.
        self.biased_fitness = 0.0

        if file_name:
            self.read_from_file(params, file_name)
        else:
            self.initialize_random_individual(params)

    def evaluate_complete_cost(self, params):
        self.eval = EvalIndiv()  # no need for this line
        for r, route in enumerate(self.chrom_r):
            if route:
                distance = params.time_cost[0][route[0]]
                load = params.cli[route[0]].demand
                service = params.cli[route[0]].service_duration
                self.predecessors[route[0]] = 0

                for i in range(1, len(route)):
                    distance += params.time_cost[route[i - 1]][route[i]]
                    load += params.cli[route[i]].demand
                    service += params.cli[route[i]].service_duration
                    self.predecessors[route[i]] = route[i - 1]
                    self.successors[route[i - 1]] = route[i]

                self.successors[route[-1]] = 0
                distance += params.time_cost[route[-1]][0]
                self.eval.distance += distance
                self.eval.nb_routes += 1
                if load > params.vehicle_capacity:
                    self.eval.capacity_excess += load - params.vehicle_capacity
                if distance + service > params.duration_limit:
                    self.eval.duration_excess += distance + service - params.duration_limit

        self.eval.penalized_cost = self.eval.distance + self.eval.capacity_excess * params.penalty_capacity + self.eval.duration_excess * params.penalty_duration
        self.eval.is_feasible = self.eval.capacity_excess < params.my_epsilon and self.eval.duration_excess < params.my_epsilon

    def initialize_random_individual(self, params):
        random.shuffle(self.chrom_t)
        self.eval.penalized_cost = float('inf')

    def read_from_file(self, params, file_name):
        try:
            with open(file_name, 'r') as file:
                content = file.readlines()

            self.chrom_t = []
            read_cost = None
            current_route = []
            for line in content:
                if line.startswith("Route"):
                    if current_route:
                        self.chrom_r.append(current_route)
                    current_route = []
                elif line.startswith("Cost"):
                    read_cost = float(line.split()[-1])
                else:
                    line_items = line.split()
                    for item in line_items:
                        if item.isdigit():
                            customer = int(item)
                            self.chrom_t.append(customer)
                            current_route.append(customer)

            if current_route:
                self.chrom_r.append(current_route)

            if read_cost is not None:
                self.evaluate_complete_cost(params)
                if len(self.chrom_t) != params.nb_clients:
                    raise ValueError("Input solution does not contain the correct number of clients")
                if not self.eval.is_feasible:
                    raise ValueError("Input solution is infeasible")
                if abs(self.eval.penalized_cost - read_cost) > params.my_epsilon:
                    raise ValueError("Input solution has a different cost than announced in the file")

            if params.verbose:
                print("----- INPUT SOLUTION HAS BEEN SUCCESSFULLY READ WITH COST ", self.eval.penalized_cost)
        except IOError:
            raise Exception("Impossible to open solution file provided in input: " + file_name)