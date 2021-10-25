from __future__ import annotations

import time

import numpy as np

class Binary:
    """Wrapper class for python built-in binary strings with least significant byte at right
    """
    dtype = np.uint8
    invalid_literal_type_msg = 'attempted to assign literal of invalid type "{literal_type}" to Binary'
    invalid_literal_dtype_msg = 'attempted to assign literal of invalid dtype "{literal_type}" to Binary'
    invalid_literal_value_msg = 'attempted to assign literal with invalid value "{literal}" of invalid dtype to Binary'

    @staticmethod
    def array_to_str(arr: np.ndarray):
        return '0b' + ''.join(arr.astype(str))

    @classmethod
    def validate_literal(cls, new_literal: np.ndarray):
        if not isinstance(new_literal, np.ndarray):
            raise ValueError(cls.invalid_literal_type_msg.format(literal_type=type(new_literal)))
        if new_literal.dtype != cls.dtype:
            raise ValueError(cls.invalid_literal_dtype_msg.format(literal_type=new_literal.dtype))
        if new_literal[(new_literal != 0) & (new_literal != 1)].size != 0:
            raise ValueError(cls.invalid_literal_value_msg.format(literal=new_literal))

    def __init__(self, literal: int | str | np.ndarray):
        self._literal = None
        if isinstance(literal, int) or isinstance(literal, self.dtype):
            self.literal = np.array([*bin(literal)][2:], dtype=self.dtype)
        elif isinstance(literal, str):
            self.literal = np.array([*literal[2:]], dtype=self.dtype)
        elif isinstance(literal, np.ndarray):
            self.literal = literal.astype(self.dtype)
        else:
            self.literal = literal

    def __str__(self):
        return self.array_to_str(self.literal)

    def __int__(self):
        return int(str(self), 2)

    def __len__(self):
        return self.literal.size

    def __eq__(self, other: Binary):
        return str(self) == str(other)

    def __getitem__(self, key: slice):
        segment = self.literal[key]
        return self.__class__(segment)

    def __setitem__(self, key: slice, value: int):
        self.literal[key] = value

    @property
    def literal(self):
        return self._literal

    @literal.setter
    def literal(self, new_literal: np.ndarray):
        self.validate_literal(new_literal)
        self._literal = new_literal

    def append(self, new_segment: np.ndarray | Binary):
        if isinstance(new_segment, np.ndarray):
            self.literal = np.append(self.literal, new_segment).astype(self.dtype)
        if isinstance(new_segment, Binary):
            self.append(new_segment.literal)

    def flip(self, position: int):
        self.literal[position] = int(not bool(self.literal[position]))

    def flip_random(self):
        self.flip(int(np.random.rand() * self.literal.size))

class Genotype:
    invalid_literal_msg = (
        'attempted to assign invalid '
        'literal "{literal}" to "{genotype}" Genotype')

    def __init__(self, literal, mut_rate):
        self.literal = literal
        self.mut_rate = mut_rate

    def __str__(self):
        return (
            f'{self.__class__.__name__} Genotype;'
            f'literal={self.literal}; mut_rate={self.mut_rate}')

    #TODO: test __len__
    def __len__(self):
        return len(self.literal)

    def __getitem__(self, key):
        return self.__class__(self.literal[key], self.mut_rate)

    @property
    def literal(self):
        return self._literal

    @literal.setter
    def literal(self, new_literal):
        self.validate_literal(new_literal)
        self._literal = new_literal

    # pylint: disable=unused-argument
    @classmethod
    def validate_literal(cls, new_literal):
        raise NotImplementedError()

    def mutate(self):
        raise NotImplementedError()

    def crossover(self, other, position):
        raise NotImplementedError()

class Nbit(Genotype):
    @classmethod
    def validate_literal(cls, new_literal):
        if not isinstance(new_literal, Binary):
            raise ValueError(
                cls.invalid_literal_msg.format(
                    literal=new_literal, genotype=cls.__name__))

    def __int__(self):
        return int(self.literal)

    def mutate(self):
        self.literal.flip_random()

    def append(self, other: np.ndarray | Binary | Nbit):
        if isinstance(other, Nbit):
            self.literal.append(other.literal)
        else:
            self.literal.append(other)

    def crossover(self, other: Nbit, position: int) -> tuple[Nbit, Nbit]:
        """Single point crossover where literal[position:] of self and other are swapped

        Args:
            other (Nbit): other parent
            position (int): position

        Returns:
            tuple[Nbit, Nbit]: offspring
        """
        offspring_a = self[:position]
        offspring_b = other[:position]
        offspring_a.append(other[position:])
        offspring_b.append(self[position:])
        return offspring_a, offspring_b

class Individual:
    """Abstract Individual returned by Environment.run

    Raises:
        ValueError: Raised if fitness or history is accessed before initialization
    """
    uninitialized_post_process = 'post-process data accessed before initialized'

    def __init__(self, genotype: Genotype, phenotype: any, parents: list[Individual]=None):
        self.genotype = genotype
        self.phenotype = phenotype
        self.parents = parents
        self._fitness = None
        self._history = None

    @property
    def fitness(self):
        if self._fitness is not None:
            return self._fitness
        raise ValueError(self.uninitialized_post_process)

    @fitness.setter
    def fitness(self, fitness: float):
        self._fitness = fitness

    @property
    def history(self):
        if self._history is not None:
            return self._history
        raise ValueError(self.uninitialized_post_process)

    @history.setter
    def history(self, history: float):
        self._history = history

    def report(self) -> IndividualReport:
        literal = str(self.genotype.literal)
        parent_literals = None
        if self.parents is not None:
            parent_literals = [str(parent.genotype.literal) for parent in self.parents]
        report = IndividualReport(literal, parent_literals, self.history, self.fitness)
        return report

class Report:
    @classmethod
    def from_json(cls, json_path):
        raise NotImplementedError()

    def __str__(self):
        raise NotImplementedError()

    def to_json(self, json_path):
        raise NotImplementedError()

class IndividualReport(Report):
    def __init__(
        self,
        genotype_literal: str,
        parent_genotype_literals: list[str],
        history: list,
        fitness: float):
        self.literal = genotype_literal
        self.parent_literals = parent_genotype_literals
        self.history = history
        self.fitness = fitness

class GenerationReport(Report):
    def __init__(self, individuals: list[Individual]):
        self.individuals = individuals
        self.highest_fitness = None
        self.average_fitness = None

class AlgorithmReport(Report):
    def __init__(
        self,
        generation_reports: list[GenerationReport],
        runtime: float,
        memory_consumption: float=None):
        self.generation_reports = generation_reports
        self.runtime = runtime
        self.memory_consumption = memory_consumption

class GeneticAlgorithm:
    def __init__(self, generation_size: int):
        self.generations = []
        self.generation_size = generation_size
        self._next_generation = None

    @staticmethod
    def phenotype(genotype: Genotype):
        raise NotImplementedError()

    @staticmethod
    def post_process_generation(generation: list[Individual]):
        raise NotImplementedError()

    def check_termination(self):
        raise NotImplementedError()

    def select(self, generation: list[Individual]) -> list[list[Individual]]:
        raise NotImplementedError()

    def breed(self, parents: list[Individual]) -> list[Individual]:
        raise NotImplementedError()

    def mutate(self, individual: Individual) -> Individual:
        raise NotImplementedError()

    def seed_generation(self) -> list[Individual]:
        raise NotImplementedError()

    def run_generation(self, generation: list[Individual]):
        raise NotImplementedError()

    def generation_report(self, generation: list[Individual]) -> GenerationReport:
        reports = []
        for individual in generation:
            reports.append(individual.report())
        return reports

    def generation_reports(self) -> list[GenerationReport]:
        reports = []
        for generation in self.generations:
            reports.append(self.generation_report(generation))
        return reports

    def run(self):
        start = time.perf_counter()
        self._next_generation = self.seed_generation()
        while not self.check_termination():
            self.run_generation(self._next_generation)
            self.post_process_generation(self._next_generation)
            self.generations.append(self._next_generation)
            parent_sets = self.select(self._next_generation)
            parent_sets += self.select(self._next_generation)
            next_generation = [child for parents in parent_sets for child in self.breed(parents)]
            self._next_generation = [self.mutate(individual) for individual in next_generation]
        end = time.perf_counter()
        elapsed = end - start
        generation_reports = self.generation_reports()
        return AlgorithmReport(generation_reports, elapsed)

if __name__ == '__main__':
    a = Binary(6)
    print(a[:])
