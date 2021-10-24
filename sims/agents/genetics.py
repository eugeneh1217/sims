from __future__ import annotations

import copy

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
        self._literal = literal
        self.mut_rate = mut_rate

    def __str__(self):
        return (
            f'{self.__class__.__name__} Genotype;'
            f'literal={self.literal}; mut_rate={self.mut_rate}')

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
    uninitialized_fitness_msg = 'fitness accessed before initialized'

    def __init__(self, genotype: Genotype, phenotype: any, history: list):
        self.genotype = genotype
        self.phenotype = phenotype
        self._fitness = None
        self.history = history

    @property
    def fitness(self):
        if self._fitness is not None:
            return self._fitness
        raise ValueError(self.uninitialized_fitness_msg)

    @fitness.setter
    def fitness(self, fitness: float):
        self._fitness = fitness

    def report(self) -> dict:
        pass

class Environment:
    invalid_genotypes_msg = 'Attempted to load invalid genotypes "{genotypes}"'

    def __init__(self, fit_func: type):
        self.fit_func = fit_func
        self.simulation = None
        self.individuals = []

    def phenotype(self, genotype: Genotype, history: list):
        """Maps genotype to phenotype

        Args:
            genotype (Genotype): genotype

        Raises:
            NotImplementedError: Must be overriden
        """
        raise NotImplementedError()

    def load_phenotypes(self):
        """Loads phenotypes of individuals into simulation

        Raises:
            NotImplementedError: Must be overriden
        """
        raise NotImplementedError()

    def update_fitness(self):
        """Updates fitness of individuals after simulation has been run
        """
        for individual in self.individuals:
            individual.fitness = self.fit_func(individual)

    def run(self, genotypes: list[Genotype]) -> Individual:
        """Runs environment
            1. Initializes individuals
            2. Loads phenotypes into simulation
            3. Runs simulation
            4. Updates fitness of individuals

        Args:
            genotypes (list[Genotype]): genotypes to run in environment

        Raises:
            ValueError: invalid genotype

        Returns:
            Individual: evaluated individuals
        """
        if not hasattr(genotypes, '__iter__'):
            raise ValueError(self.invalid_genotypes_msg.format(genotypes))
        if not isinstance(genotypes[0], Genotype):
            raise ValueError(self.invalid_genotypes_msg.format(genotypes))
        # self.individuals = [Individual(genotype, self.phenotype(genotype)) for genotype in genotypes]
        for genotype in genotypes:
            history = []
            self.individuals.append(Individual(genotype, self.phenotype(genotype, history), history))
        self.load_phenotypes()
        self.simulation.run()
        self.update_fitness()
        return self.individuals

class GeneticAlgorithm:
    def __init__(self):
        pass

    def select(self):
        pass

    def breed(self):
        pass

    def mutate(self):
        pass

    def run_generation(self):
        pass

    def check_termination(self):
        pass

    def generation_report(self):
        pass

    def algorithm_report(self):
        pass

if __name__ == '__main__':
    a = Binary(6)
    print(a[:])
