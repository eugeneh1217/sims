from sims.agents import genetics
from sims.environments import hurdles

def hurdles_fitness(individual: genetics.Individual):
    return individual.phenotype.termination_state.frame_number

class TrainingEnvironment(genetics.Environment):
    def __init__(self):
        super().__init__(hurdles_fitness)

    def phenotype(self, genotype: genetics.Genotype, history: list) -> hurdles.ProximityHurdler:
        return hurdles.ProximityHurdler(int(genotype), history=history)

    def load_phenotypes(self):
        hurdlers = [individual.phenotype for individual in self.individuals]
        self.simulation = hurdles.Simulation(hurdlers=hurdlers, hurdles=[hurdles.Hurdle()])

if __name__ == '__main__':
    env = TrainingEnvironment()
    genotypes = [genetics.Nbit(genetics.Binary(i), 1/4) for i in range(10, 100, 10)]
    env.run(genotypes)