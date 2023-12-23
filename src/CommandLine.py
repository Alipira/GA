import sys
from AlgorithmParameter import default_algorithm_parameters


class CommandLine:
    def __init__(self, argv):
        self.ap = default_algorithm_parameters()

        self.nbVeh = sys.maxsize  # Number of vehicles. Default value: infinity
        self.pathInstance = ""  # Instance path
        self.pathSolution = ""  # Solution path
        self.verbose = True
        self.isRoundingInteger = True

        argc = len(argv)
        breakpoint()
        if (argc % 2 != 1) or (argc > 35) or (argc < 3):
            print("----- NUMBER OF COMMANDLINE ARGUMENTS IS INCORRECT:", argc)
            self.display_help()
            raise ValueError("Incorrect line of command")
        else:
            self.pathInstance = argv[1]
            self.pathSolution = argv[2]
            i = 3
            while i < argc:
                if argv[i] == "-t":
                    self.ap.timeLimit = float(argv[i + 1])
                elif argv[i] == "-it":
                    self.ap.nbIter = int(argv[i + 1])
                elif argv[i] == "-seed":
                    self.ap.seed = int(argv[i + 1])
                elif argv[i] == "-veh":
                    self.nbVeh = int(argv[i + 1])
                elif argv[i] == "-round":
                    self.isRoundingInteger = int(argv[i + 1])
                elif argv[i] == "-log":
                    self.verbose = int(argv[i + 1])
                elif argv[i] == "-nbGranular":
                    self.ap.nbGranular = int(argv[i + 1])
                elif argv[i] == "-mu":
                    self.ap.mu = int(argv[i + 1])
                elif argv[i] == "-lambda":
                    self.ap.lambda_ = int(argv[i + 1])
                elif argv[i] == "-nbElite":
                    self.ap.nbElite = int(argv[i + 1])
                elif argv[i] == "-nbClose":
                    self.ap.nbClose = int(argv[i + 1])
                elif argv[i] == "-nbIterPenaltyManagement":
                    self.ap.nbIterPenaltyManagement = int(argv[i + 1])
                elif argv[i] == "-nbIterTraces":
                    self.ap.nbIterTraces = int(argv[i + 1])
                elif argv[i] == "-targetFeasible":
                    self.ap.targetFeasible = float(argv[i + 1])
                elif argv[i] == "-penaltyIncrease":
                    self.ap.penaltyIncrease = float(argv[i + 1])
                elif argv[i] == "-penaltyDecrease":
                    self.ap.penaltyDecrease = float(argv[i + 1])
                else:
                    print("----- ARGUMENT NOT RECOGNIZED:", argv[i])
                    self.display_help()
                    raise ValueError("Incorrect line of command")
                i += 2

    def display_help(self):
        print()
        print("--------------------------------------------------- HGS-CVRP algorithm ---------------------------------------------------------")
        print("Call with: ./hgs instancePath solPath [-it nbIter] [-t myCPUtime] [-seed mySeed] [-veh nbVehicles] [-log verbose]               ")
        print("[-it <int>] sets a maximum number of iterations without improvement. Defaults to 20,000                                         ")
        print("[-t <double>] sets a time limit in seconds. If this parameter is set the code will be run iteratively until the time limit      ")
        print("[-seed <int>] sets a fixed seed. Defaults to 0                                                                                  ")
        print("[-veh <int>] sets a prescribed fleet size. Otherwise a reasonable UB on the the fleet size is calculated                        ")
        print("[-round <bool>] rounding the distance to the nearest integer or not. It can be 0 (not rounding) or 1 (rounding). Defaults to 1. ")
        print("[-log <bool>] sets the verbose level of the algorithm log. It can be 0 or 1. Defaults to 1.                                     ")
        print()
        print("Additional Arguments:                                                                                                           ")
        print("[-nbIterTraces <int>] Number of iterations between traces display during HGS execution. Defaults to 500                         ")
        print("[-nbGranular <int>] Granular search parameter, limits the number of moves in the RI local search. Defaults to 20                ")
        print("[-mu <int>] Minimum population size. Defaults to 25                                                                             ")
        print("[-lambda <int>] Number of solutions created before reaching the maximum population size (i.e., generation size). Defaults to 40 ")
        print("[-nbElite <int>] Number of elite individuals. Defaults to 5                                                                     ")
        print("[-nbClose <int>] Number of closest solutions/individuals considered when calculating diversity contribution. Defaults to 4      ")
        print("[-nbIterPenaltyManagement <int>] Number of iterations between penalty updates. Defaults to 100                                  ")
        print("[-targetFeasible <double>] target ratio of feasible individuals between penalty updates. Defaults to 0.2                        ")
        print("[-penaltyIncrease <double>] penalty increase if insufficient feasible individuals between penalty updates. Defaults to 1.2      ")
        print("[-penaltyDecrease <double>] penalty decrease if sufficient feasible individuals between penalty updates. Defaults to 0.85       ")
        print("--------------------------------------------------------------------------------------------------------------------------------")
        print()


# Usage example:
# cmd_line = CommandLine(sys.argv)
