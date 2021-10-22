from __future__ import annotations
import numpy as np

"""
TODO: trim binary literals
"""

class ErrorMessages:
    invalid_genotype_literal = (
        'attempted to assign invalid literal"{literal}" to "{genotype}" Genotype')
    invalid_binary_literal = (
        'attempted to assign invalid literal"{literal}" to Binary'
    )

class Binary:
    """Wrapper class for python built-in binary strings with least significant byte at right
    """
    dtype = np.uint8

    @staticmethod
    def array_to_str(arr: np.ndarray):
        return '0b' + ''.join(arr.astype(str))

    @staticmethod
    def str_to_int(string: str):
        return int(string, 2)

    @classmethod
    def validate_literal(cls, new_literal):
        if not isinstance(new_literal, np.ndarray):
            raise ValueError(ErrorMessages.invalid_binary_literal.format(literal=new_literal))
        if new_literal.dtype != cls.dtype:
            raise ValueError(ErrorMessages.invalid_binary_literal.format(literal=new_literal))

    @classmethod
    def from_array(cls, arr: np.ndarray):
        return Binary(cls.str_to_int(cls.array_to_str(arr)))

    def __init__(self, literal: int):
        self._literal = np.array([*bin(literal)][2:], dtype=self.dtype)

    def __str__(self):
        return self.array_to_str(self.literal)

    def __int__(self):
        return self.str_to_int(str(self))

    def __len__(self):
        return self.literal.size

    def __eq__(self, other: Binary):
        return int(self) == int(other)

    def __getitem__(self, key: slice):
        segment = self.literal[key]
        return self.from_array(segment)

    def __setitem__(self, key: slice, value: int):
        self.literal[key] = value

    @property
    def literal(self):
        return self._literal

    @literal.setter
    def set_literal(self, new_literal: np.ndarray):
        self.validate_literal(new_literal)
        self._literal = new_literal

    def flip(self, position: int):
        self.literal[position] = int(not bool(self.literal[position]))

    def flip_random(self):
        self.flip(int(np.random.rand() * self.literal.size))

class Genotype:
    def __init__(self, literal, mutation_rate):
        self._literal = literal
        self.mutation_rate = mutation_rate

    @property
    def literal(self):
        return self._literal

    @literal.setter
    def set_literal(self, new_literal):
        self.validate_literal(new_literal)
        self._literal = new_literal

    # pylint: disable=unused-argument
    @classmethod
    def validate_literal(cls, new_literal):
        raise NotImplementedError()

    def mutate(self):
        raise NotImplementedError()

    def crossover(self):
        raise NotImplementedError()

class Nbit(Genotype):
    @classmethod
    def validate_literal(cls, new_literal):
        if not isinstance(new_literal, Binary):
            raise ValueError(
                ErrorMessages.invalid_genotype_literal.format(
                    literal=new_literal, genotype=cls.__name__))

    def mutate(self):
        self.literal.flip_random()

    def crossover(self, other, position):
        this_segment = self.literal[position:]
        other_segment = self.literal[position:]
        self.literal[position] = other_segment
        other.literal[position] = this_segment

class Individual:
    def __init__(self, genotype: Genotype, fitness: float, history: dict):
        self.genotype = genotype
        self.fitness = fitness
        self.history = history

class Simulation:
    def __init__(self):
        pass

class GeneticAlgorithm:
    def __init__(self):
        pass

if __name__ == '__main__':
    a = Binary(6)
    print(a[:])
