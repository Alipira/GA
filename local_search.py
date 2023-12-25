import math


class InstanceCVRPLIB:
    def __init__(self, path_to_instance: str, is_rounding_integer=True):
        self.x_coords = []
        self.y_coords = []
        self.dist_mtx = [[]]
        self.service_time = []
        self.demands = []
        self.duration_limit = 1e30  # Route duration limit
        self.vehicle_capacity = 1e30  # Capacity limit
        self.is_duration_constraint = False  # Indicates if the problem includes duration constraints
        self.nb_clients = 0  # Number of clients (excluding the depot)

        self.read_instance_file(path_to_instance, is_rounding_integer)

    def read_instance_file(self, path_to_instance, is_rounding_integer):
        service_time_data = 0.0

        with open(path_to_instance, 'r') as input_file:
            content = input_file.readline().strip()
            content2 = input_file.readline().strip()
            content3 = input_file.readline().strip()

            for content in input_file:
                if content == "NODE_COORD_SECTION":
                    break

                if content.startswith("DIMENSION"):
                    _, content2, self.nb_clients = content.split()
                    self.nb_clients = int(self.nb_clients) - 1  # Subtract the depot from the number of nodes
                elif content.startswith("EDGE_WEIGHT_TYPE"):
                    _, content2, content3 = content.split()
                elif content.startswith("CAPACITY"):
                    _, content2, self.vehicle_capacity = content.split()
                elif content.startswith("DISTANCE"):
                    _, content2, self.duration_limit = content.split()
                    self.is_duration_constraint = True
                elif content.startswith("SERVICE_TIME"):
                    _, content2, service_time_data = content.split()
                else:
                    raise ValueError("Unexpected data in input file: " + content.strip())

            if self.nb_clients <= 0:
                raise ValueError("Number of nodes is undefined")
            if self.vehicle_capacity == 1e30:
                raise ValueError("Vehicle capacity is undefined")

            self.x_coords = [0.0] * (self.nb_clients + 1)
            self.y_coords = [0.0] * (self.nb_clients + 1)
            self.demands = [0.0] * (self.nb_clients + 1)
            self.service_time = [0.0] * (self.nb_clients + 1)

            # Reading node coordinates
            for i in range(self.nb_clients + 1):
                node_number, self.x_coords[i], self.y_coords[i] = map(float, input_file.readline().split())
                if node_number != i + 1:
                    raise ValueError("The node numbering is not in order.")

            # Reading demand information
            content = input_file.readline().strip()
            if content != "DEMAND_SECTION":
                raise ValueError("Unexpected data in input file: " + content)
            for i in range(self.nb_clients + 1):
                content, self.demands[i] = input_file.readline().split()
                self.service_time[i] = 0.0 if i == 0 else float(service_time_data)

            # Calculating 2D Euclidean Distance
            self.dist_mtx = [[0.0] * (self.nb_clients + 1) for _ in range(self.nb_clients + 1)]
            for i in range(self.nb_clients + 1):
                for j in range(self.nb_clients + 1):
                    self.dist_mtx[i][j] = math.sqrt(
                        (self.x_coords[i] - self.x_coords[j]) ** 2 +
                        (self.y_coords[i] - self.y_coords[j]) ** 2
                    )

                    if is_rounding_integer:
                        self.dist_mtx[i][j] = round(self.dist_mtx[i][j])

            # Reading depot information
            content, content2, content3, _ = input_file.readline().split()
            if content != "DEPOT_SECTION":
                raise ValueError("Unexpected data in input file: " + content)
            if content2 != "1":
                raise ValueError("Expected depot index 1 instead of " + content2)
            if content3 != "EOF":
                raise ValueError("Unexpected data in input file: " + content3)
