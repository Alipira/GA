import sys
import random
import time
from typing import List, Tuple
from Individual import Individual

MY_EPSILON = 1e-6


class Population:
    def __init__(self, params, split, local_search):
        self.params = params
        self.split = split
        self.local_search = local_search
        self.feasible_subpop = []
        self.infeasible_subpop = []
        self.list_feasibility_load = [True] * params.ap.nbIterPenaltyManagement
        self.list_feasibility_duration = [True] * params.ap.nbIterPenaltyManagement
        self.search_progress = []  # Tuple of (clock_t, double)
        self.best_solution_restart = Individual(params)
        self.best_solution_overall = Individual(params)

    def generate_population(self):
        if self.params.verbose:
            print("----- BUILDING INITIAL POPULATION")
        i = 0
        while i < 4 * self.params.ap.mu and (i == 0 or self.params.ap.timeLimit == 0 or
                                             (time.clock() - self.params.startTime) / CLOCKS_PER_SEC < self.params.ap.timeLimit):
            random_indiv = Individual(self.params)
            self.split.general_split(random_indiv, self.params.nbVehicles)
            self.local_search.run(random_indiv, self.params.penaltyCapacity, self.params.penaltyDuration)
            self.add_individual(random_indiv, True)
            if not random_indiv.eval.is_feasible and random.randint(0, 1) == 0:
                self.local_search.run(random_indiv, self.params.penaltyCapacity * 10., self.params.penaltyDuration * 10.)
                if random_indiv.eval.is_feasible:
                    self.add_individual(random_indiv, False)
            i += 1

    def add_individual(self, indiv, update_feasible):
        if update_feasible:
            self.list_feasibility_load.append(indiv.eval.capacity_excess < MY_EPSILON)
            self.list_feasibility_duration.append(indiv.eval.duration_excess < MY_EPSILON)
            self.list_feasibility_load.pop(0)
            self.list_feasibility_duration.pop(0)

        subpop = self.feasible_subpop if indiv.eval.is_feasible else self.infeasible_subpop

        my_individual = Individual(indiv)
        for my_individual2 in subpop:
            my_distance = self.broken_pairs_distance(my_individual, my_individual2)
            my_individual2.indivs_per_proximity[my_distance] = my_individual
            my_individual.indivs_per_proximity[my_distance] = my_individual2

        place = len(subpop)
        while place > 0 and subpop[place - 1].eval.penalized_cost > indiv.eval.penalized_cost - MY_EPSILON:
            place -= 1
        subpop.insert(place, my_individual)

        if len(subpop) > self.params.ap.mu + self.params.ap.lambda_:
            while len(subpop) > self.params.ap.mu:
                self.remove_worst_biased_fitness(subpop)

        if indiv.eval.is_feasible and indiv.eval.penalized_cost < self.best_solution_restart.eval.penalized_cost - MY_EPSILON:
            self.best_solution_restart = indiv
            if indiv.eval.penalized_cost < self.best_solution_overall.eval.penalized_cost - MY_EPSILON:
                self.best_solution_overall = indiv
                self.search_progress.append((time.clock() - self.params.startTime, self.best_solution_overall.eval.penalized_cost))
            return True
        else:
            return False

    def update_biased_fitnesses(self, pop):
        ranking = sorted(enumerate(pop), key=lambda x: -self.average_broken_pairs_distance_closest(x[1], self.params.ap.nbClose))

        if len(pop) == 1:
            pop[0].biased_fitness = 0
        else:
            for i, (_, ind) in enumerate(ranking):
                div_rank = i / (len(pop) - 1)
                fit_rank = ranking[i][0] / (len(pop) - 1)
                if len(pop) <= self.params.ap.nbElite:
                    ind.based_fitness = fit_rank
                else:
                    ind.based_fitness = fit_rank + (1.0 - self.params.ap.nbElite / len(pop)) * div_rank

    def remove_worst_biased_fitness(self, pop):
        self.update_biased_fitnesses(pop)
        if len(pop) <= 1:
            raise ValueError("Eliminating the best individual: this should not occur in HGS")

        worst_individual = None
        worst_individual_position = -1
        is_worst_individual_clone = False
        worst_individual_biased_fitness = -1e30
        for i, ind in enumerate(pop[1:], 1):
            is_clone = self.average_broken_pairs_distance_closest(ind, 1) < MY_EPSILON
            if (is_clone and not is_worst_individual_clone) or (is_clone == is_worst_individual_clone and ind.based_fitness > worst_individual_biased_fitness):
                worst_individual_biased_fitness = ind.based_fitness
                is_worst_individual_clone = is_clone
                worst_individual_position = i
                worst_individual = ind

        pop.pop(worst_individual_position)

        for indiv2 in pop:
            del indiv2.indivs_per_proximity[worst_individual]

        del worst_individual

    def restart(self):
        if self.params.verbose:
            print("----- RESET: CREATING A NEW POPULATION -----")
        for indiv in self.feasible_subpop:
            del indiv
        for indiv in self.infeasible_subpop:
            del indiv
        self.feasible_subpop.clear()
        self.infeasible_subpop.clear()
        self.best_solution_restart = Individual(self.params)
        self.generate_population()

    def manage_penalties(self):
        fraction_feasible_load = sum(self.list_feasibility_load) / len(self.list_feasibility_load)
        if fraction_feasible_load < self.params.ap.target_feasible - 0.05 and self.params.penalty_capacity < 100000.:
            self.params.penalty_capacity = min(self.params.penalty_capacity * self.params.ap.penalty_increase, 100000.)
        elif fraction_feasible_load > self.params.ap.target_feasible + 0.05 and self.params.penalty_capacity > 0.1:
            self.params.penalty_capacity = max(self.params.penalty_capacity * self.params.ap.penalty_decrease, 0.1)

        fraction_feasible_duration = sum(self.list_feasibility_duration) / len(self.list_feasibility_duration)
        if fraction_feasible_duration < self.params.ap.target_feasible - 0.05 and self.params.penalty_duration < 100000.:
            self.params.penalty_duration = min(self.params.penalty_duration * self.params.ap.penalty_increase, 100000.)
        elif fraction_feasible_duration > self.params.ap.target_feasible + 0.05 and self.params.penalty_duration > 0.1:
            self.params.penalty_duration = max(self.params.penalty_duration * self.params.ap.penalty_decrease, 0.1)

        for ind in self.infeasible_subpop:
            ind.eval.penalized_cost = ind.eval.distance + self.params.penalty_capacity * ind.eval.capacity_excess + self.params.penalty_duration * ind.eval.duration_excess

        for i in range(len(self.infeasible_subpop)):
            for j in range(len(self.infeasible_subpop) - i - 1):
                if self.infeasible_subpop[j].eval.penalized_cost > self.infeasible_subpop[j + 1].eval.penalized_cost + MY_EPSILON:
                    self.infeasible_subpop[j], self.infeasible_subpop[j + 1] = self.infeasible_subpop[j + 1], self.infeasible_subpop[j]

    def get_binary_tournament(self):
        place1 = random.randint(0, len(self.feasible_subpop) + len(self.infeasible_subpop) - 1)
        place2 = random.randint(0, len(self.feasible_subpop) + len(self.infeasible_subpop) - 1)
        indiv1 = self.infeasible_subpop[place1 - len(self.feasible_subpop)] if place1 >= len(self.feasible_subpop) else self.feasible_subpop[place1]
        indiv2 = self.infeasible_subpop[place2 - len(self.feasible_subpop)] if place2 >= len(self.feasible_subpop) else self.feasible_subpop[place2]

        self.update_biased_fitnesses(self.feasible_subpop)
        self.update_biased_fitnesses(self.infeasible_subpop)

        return indiv1 if indiv1.based_fitness < indiv2.based_fitness else indiv2

    def get_best_feasible(self):
        return self.feasible_subpop[0] if self.feasible_subpop else None

    def get_best_infeasible(self):
        return self.infeasible_subpop[0] if self.infeasible_subpop else None

    def get_best_found(self):
        return self.best_solution_overall if self.best_solution_overall.eval.penalized_cost < 1e29 else None

    def print_state(self, nb_iter, nb_iter_no_improvement):
        if self.params.verbose:
            print(f"It {nb_iter:6d} {nb_iter_no_improvement:6d} | T(s) {time.clock() - self.params.start_time:.2f}", end="")

            best_feasible = self.get_best_feasible()
            if best_feasible:
                print(f" | Feas {len(self.feasible_subpop)} {best_feasible.eval.penalized_cost:.2f} {self.get_average_cost(self.feasible_subpop):.2f}", end="")
            else:
                print(" | NO-FEASIBLE", end="")

            best_infeasible = self.get_best_infeasible()
            if best_infeasible:
                print(f" | Inf {len(self.infeasible_subpop)} {best_infeasible.eval.penalized_cost:.2f} {self.get_average_cost(self.infeasible_subpop):.2f}", end="")
            else:
                print(" | NO-INFEASIBLE", end="")

            print(f" | Div {self.get_diversity(self.feasible_subpop)")  # FIXME:

    def get_diversity(self, pop):
        average = 0.
        size = min(self.params.ap.mu, len(pop))
        for i in range(size):
            average += self.average_broken_pairs_distance_closest(pop[i], size)
        return average / size if size > 0 else -1.0

    def get_average_cost(self, pop):
        average = 0.
        size = min(self.params.ap.mu, len(pop))
        for i in range(size):
            average += pop[i].eval.penalized_cost
        return average / size if size > 0 else -1.0

    def broken_pairs_distance(self, indiv1, indiv2):
        differences = 0
        for j in range(1, self.params.nbClients + 1):
            if indiv1.successors[j] != indiv2.successors[j] and indiv1.successors[j] != indiv2.predecessors[j]:
                differences += 1
            if indiv1.predecessors[j] == 0 and indiv2.predecessors[j] != 0 and indiv2.successors[j] != 0:
                differences += 1
        return differences / self.params.nbClients

    def average_broken_pairs_distance_closest(self, indiv, nb_closest):
        result = 0.
        items = list(indiv.indivs_per_proximity.items())
        items.sort(key=lambda x: x[0])
        max_size = min(nb_closest, len(items))
        for i in range(max_size):
            result += items[i][0]
        return result / max_size if max_size > 0 else 0

    def export_search_progress(self, file_name, instance_name):
        with open(file_name, 'w') as file:
            for state in self.search_progress:
                file.write(f"{instance_name};{self.params.ap.seed};{state[1]};{state[0] / CLOCKS_PER_SEC}\n")

    def export_cvrplib_format(self, indiv, file_name):
        try:
            with open(file_name, 'w') as file:
                for k, route in enumerate(indiv.chrom_r):
                    if route:
                        file.write(f"Route #{k + 1}: {' '.join(map(str, route))}\n")
                file.write(f"Cost {indiv.eval.penalized_cost}\n")
        except IOError:
            print(f"----- IMPOSSIBLE TO OPEN: {file_name}")

    def __del__(self):
        for indiv in self.feasible_subpop + self.infeasible_subpop:
            del indiv




# Example usage:
# params = Params()
# split = Split()
# local_search = LocalSearch()
# population = Population(params, split, local_search)
# population.generatePopulation()