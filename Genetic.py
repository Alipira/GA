import random
import time

from split import Split
from local_search import LocalSearch
from population import Population
from Individual import Individual


class Genetic:
    def __init__(self, params):
        self.params = params
        self.split = Split(params)
        self.local_search = LocalSearch(params)
        self.population = Population(params, self.split, self.local_search)
        self.offspring = Individual(params)

    # Implement OX Crossover
    def crossover_ox(self, result, parent1, parent2):
        freq_client = [False] * (self.params.nbClients + 1)  # numpy.fill(shape, False)

        start = random.uniform(0, self.params.nbClients - 1)
        end = random.uniform(0, self.params.nbClients - 1)

        # Avoid that start and end coincide by accident
        while end == start:
            end = random.uniform(0, self.params.nbClients - 1)

        # Copy from start to end
        j = start
        while j % self.params.nbClients != ((end + 1) % self.params.nbClients):
            result.chromT[j % self.params.nbClients] = parent1.chromT[j % self.params.nbClients]
            freq_client[result.chromT[j % self.params.nbClients]] = True
            j += 1

        # Fill the remaining elements in the order given by the second parent
        for i in range(1, self.params.nbClients + 1):
            temp = parent2.chromT[(end + i) % self.params.nbClients]
            if not freq_client[temp]:
                result.chromT[j % self.params.nbClients] = temp
                j += 1

        # Complete the individual with the Split algorithm
        self.split.general_split(result, parent1.eval.nbRoutes)

    def run(self):
        self.population.generate_population()

        nb_iter = 0
        nb_iter_non_prod = 1

        if self.params.verbose:
            print("----- STARTING GENETIC ALGORITHM")

        while nb_iter_non_prod <= self.params.ap.nbIter and \
                (self.params.ap.timeLimit == 0 or
                 (time.clock() - self.params.startTime) / time.process_time() < self.params.ap.timeLimit):

            # Selection and Crossover
            self.crossover_ox(self.offspring,
                              self.population.get_binary_tournament(),
                              self.population.get_binary_tournament())

            # Local Search
            self.local_search.run(self.offspring,
                                  self.params.penaltyCapacity,
                                  self.params.penaltyDuration)

            is_new_best = self.population.add_individual(self.offspring, True)

            # Repair half of the solutions in case of infeasibility
            if not self.offspring.eval.isFeasible and random.randint(0, 1) == 0:
                self.local_search.run(self.offspring,
                                      self.params.penaltyCapacity * 10.,
                                      self.params.penaltyDuration * 10.)

                if self.offspring.eval.isFeasible:
                    is_new_best = self.population.add_individual(self.offspring, False) or is_new_best

            # TRACKING THE NUMBER OF ITERATIONS SINCE LAST SOLUTION IMPROVEMENT
            if is_new_best:
                nb_iter_non_prod = 1
            else:
                nb_iter_non_prod += 1

            # DIVERSIFICATION, PENALTY MANAGEMENT AND TRACES
            if nb_iter % self.params.ap.nbIterPenaltyManagement == 0:
                self.population.manage_penalties()

            if nb_iter % self.params.ap.nbIterTraces == 0:
                self.population.print_state(nb_iter, nb_iter_non_prod)

            # FOR TESTS INVOLVING SUCCESSIVE RUNS UNTIL A TIME LIMIT: WE RESET THE ALGORITHM/POPULATION EACH TIME maxIterNonProd IS ATTAINED
            if self.params.ap.timeLimit != 0 and nb_iter_non_prod == self.params.ap.nbIter:
                self.population.restart()
                nb_iter_non_prod = 1

            nb_iter += 1

        if self.params.verbose:
            print(f"----- GENETIC ALGORITHM FINISHED AFTER {nb_iter} ITERATIONS. "
                  f"TIME SPENT: {time.clock() - self.params.startTime}")
