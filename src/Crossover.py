import numpy as np


class Crossover:
    def __init__(self, customers):
        self.point = np.random.randint(low=1, high=len(customers))

    def single_point(self, parent_A, parent_B):
        offspring_A = np.append(parent_A[:self.point], parent_B[self.point:])
        offspring_B = np.append(parent_B[:self.point], parent_A[self.point:])
        return offspring_A, offspring_B

    def k_point(self, parent_A, parent_B):
        pass

    # order crossover or OX crossover
    def ox_crossover(self, parent_A, parent_B):
        size = len(parent_A)
        # Create empty offspring with placeholder values
        offspring = np.full(size, -1, dtype=parent_A.dtype)

        # Select crossover points
        crossover_point1 = np.random.randint(0, size)
        crossover_point2 = np.random.randint(0, size)

        if crossover_point1 > crossover_point2:
            crossover_point1, crossover_point2 = crossover_point2, crossover_point1

        # Insert the slice from parent1 into the offspring
        offspring[crossover_point1:crossover_point2] = parent_A[crossover_point1:crossover_point2]

        # Fill the remaining positions with the genes from parent2
        offspring_pos = crossover_point2
        for gene in parent_B:
            if gene not in offspring:
                if offspring_pos >= size:
                    offspring_pos = 0
                offspring[offspring_pos] = gene
                offspring_pos += 1

        return offspring

    def uniform(self, parent_A, parent_B):
        pass
