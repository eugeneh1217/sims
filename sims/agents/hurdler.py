import copy

import numpy as np

from sims.agents import genetics
from sims.environments import hurdles
from settings import Settings

class ProximityHurdlerTrainer(genetics.GeneticAlgorithm):
    invalid_num_parents_msg = 'Parent set of invalid size {size}. Must be 2.'

    @staticmethod
    def phenotype(genotype: genetics.Genotype) -> hurdles.ProximityHurdler:
        return hurdles.ProximityHurdler(int(genotype))

    @staticmethod
    def pop_random(series: list):
        return series.pop(int(np.random.rand() * len(series)))

    @staticmethod
    def post_process_generation(generation: genetics.Individual):
        for individual in generation:
            individual.fitness = individual.phenotype.termination_state.frame_number
            individual.history = individual.phenotype.history

    @classmethod
    def pair(cls, generation: list[genetics.Individual]) -> list[genetics.Individual]:
        parent_a = cls.pop_random(generation)
        parent_b = cls.pop_random(generation)
        return parent_a, parent_b

    def __init__(self, generation_size: int, seed_genotype_max: int, to_video: bool=False):
        super().__init__(generation_size)
        self.to_video = to_video
        self.seed_genotype_max = seed_genotype_max

    def check_termination(self):
        return len(self.generations) >= Settings.nbit_generations

    def select(self, generation: list[genetics.Individual]) -> list[genetics.Individual]:
        generation_copy = copy.deepcopy(generation)
        generation_copy.sort(key=(lambda x: x.fitness))
        parent_pool = generation_copy[-int(self.generation_size / 2):]
        parent_sets = []
        while len(parent_pool) >= 2:
            parent_sets.append(self.pair(parent_pool))
        return parent_sets

    def breed(self, parents: list[genetics.Individual]) -> list[genetics.Individual]:
        if len(parents) != 2:
            raise ValueError(self.invalid_num_parents_msg.format(len(parents)))
        parent_genotypes = [parent.genotype for parent in parents]
        parent_genotypes.sort(key=(lambda x: len(x)))
        cross_position = int(np.random.rand() * len(parent_genotypes[0]))
        children_genotypes = parent_genotypes[0].crossover(parent_genotypes[1], cross_position)
        children_phenotypes = [self.phenotype(child) for child in children_genotypes]
        children = [
            genetics.Individual(children_genotypes[i], children_phenotypes[i], parents=parents)
            for i in range(len(children_genotypes))]
        return children

    def mutate(self, individual: genetics.Individual) -> genetics.Individual:
        copy_genotype = copy.deepcopy(individual.genotype)
        copy_genotype.mutate()
        return genetics.Individual(copy_genotype, self.phenotype(copy_genotype))

    def seed_generation(self) -> list[genetics.Individual]:
        seed_genotypes = [
            genetics.Nbit(genetics.Binary(int(np.random.rand() * self.seed_genotype_max)), 1)
            for _ in range(self.generation_size)]
        seed_indivs = [
            genetics.Individual(genotype, self.phenotype(genotype))
            for genotype in seed_genotypes]
        return seed_indivs

    def run_generation(self, generation: list[genetics.Individual]):
        hurdlers = [individual.phenotype for individual in generation]
        sim = hurdles.Simulation(hurdlers=hurdlers, hurdles=[hurdles.Hurdle()])
        sim.run(self.to_video)

if __name__ == '__main__':
    trainer = ProximityHurdlerTrainer(20, 10000, to_video=False)
    algo_rep = trainer.run()
    # algo_rep.to_json()
