from dataclasses import dataclass


@dataclass
class AlgorithmParameters:
    def __init__(self):
        self.nbGranular = 20
        self.mu = 25
        self.lambda_ = 40
        self.nbElite = 4
        self.nbClose = 5
        self.nbIterPenaltyManagement = 100
        self.targetFeasible = 0.2
        self.penaltyDecrease = 0.85
        self.penaltyIncrease = 1.2
        self.seed = 0
        self.nbIter = 20000
        self.nbIterTraces = 500
        self.timeLimit = 0
        self.useSwapStar = 1


def default_algorithm_parameters():
    return AlgorithmParameters()


def print_algorithm_parameters(ap):
    print("=========== Algorithm Parameters ================")
    print("---- nbGranular              is set to", ap.nbGranular)
    print("---- mu                      is set to", ap.mu)
    print("---- lambda                  is set to", ap.lambda_)
    print("---- nbElite                 is set to", ap.nbElite)
    print("---- nbClose                 is set to", ap.nbClose)
    print("---- nbIterPenaltyManagement is set to", ap.nbIterPenaltyManagement)
    print("---- targetFeasible          is set to", ap.targetFeasible)
    print("---- penaltyDecrease         is set to", ap.penaltyDecrease)
    print("---- penaltyIncrease         is set to", ap.penaltyIncrease)
    print("---- seed                    is set to", ap.seed)
    print("---- nbIter                  is set to", ap.nbIter)
    print("---- nbIterTraces            is set to", ap.nbIterTraces)
    print("---- timeLimit               is set to", ap.timeLimit)
    print("---- useSwapStar             is set to", ap.useSwapStar)
    print("================================================")


######################### TEST ###########################################################
# Create an instance of AlgorithmParameters using the default_algorithm_parameters function
# params = default_algorithm_parameters()

# # Print the parameters using the print_algorithm_parameters function
# print_algorithm_parameters(params)
