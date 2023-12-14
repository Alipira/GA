class CostFunction():
    def __init__(self,):
        self.fitness = None
        self.ranking = []

    def calculate_fitness(self, n_elite, population, n_closest):
        for i in range(len(population)):
            self.ranking.append(
                (
                    self.averageBrokenPairsDistanceClosest(
                        population[i], n_closest
                    ), i
                )
            )

        self.ranking.sort()

        # update the cost function
        if len(population) == 1:
            pass  # FIXME:
        else:
            for i in range(len(population)):
                div_rank = i / (len(population) - 1)
                fit_rank = self.ranking[i][1] / (len(population) - 1)  # FIXME:

                if len(population) <= n_elite:
                    pass  # FIXME:
                else:
                    fitness = fit_rank + ((1 - n_elite / len(population)) * div_rank)

    def averageBrokenPairsDistanceClosest(self, n_closest):
        result = 0
        maxsize = min(n_closest, )

    def manage_penalties(self, ):
        pass

    def __str__(self, ):
        return f'{self.Total_distance:0.2f}'
