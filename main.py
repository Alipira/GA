from Genetic import Genetic
from CommandLine import CommandLine
from local_search import print_algorithm_parameters
from InstanceCVRPLIB import InstanceCVRPLIB


def main():
    try:
        # Reading the arguments of the program
        commandline = CommandLine()

        # Print all algorithm parameter values
        if commandline.verbose:
            print_algorithm_parameters(commandline.ap)

        # Reading the data file and initializing some data structures
        if commandline.verbose:
            print("----- READING INSTANCE:", commandline.pathInstance)
        cvrp = InstanceCVRPLIB(commandline.pathInstance, commandline.isRoundingInteger)

        params = {
            'x_coords': cvrp.x_coords,
            'y_coords': cvrp.y_coords,
            'dist_mtx': cvrp.dist_mtx,
            'service_time': cvrp.service_time,
            'demands': cvrp.demands,
            'vehicle_capacity': cvrp.vehicleCapacity,
            'duration_limit': cvrp.durationLimit,
            'nb_vehicles': commandline.nbVeh,
            'is_duration_constraint': cvrp.isDurationConstraint,
            'verbose': commandline.verbose,
            'ap': commandline.ap
        }

        # Running HGS
        solver = Genetic(params)
        solver.run()

        # Exporting the best solution
        best_found = solver.population.getBestFound()
        if best_found is not None:
            if params['verbose']:
                print("----- WRITING BEST SOLUTION IN:", commandline.pathSolution)
            solver.population.exportCVRPLibFormat(best_found, commandline.pathSolution)
            solver.population.exportSearchProgress(commandline.pathSolution + ".PG.csv", commandline.pathInstance)

    except Exception as e:
        print(f"EXCEPTION | {e}")


if __name__ == "__main__":
    main()
