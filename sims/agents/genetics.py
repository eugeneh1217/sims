from __future__ import annotations

import copy
import json
import re
import time
from unittest.result import TestResult

import numpy as np

def intable(string: str) -> bool:
    try:
        int(string)
    except ValueError:
        return False
    return True

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

class NodeString:
    @classmethod
    def validate_literal(cls, new: str):
        if not isinstance(new, str):
            raise ValueError(
                f'NodeString initialized with invalid literal "{new}" of type "{type(new)}"'
            )

    @classmethod
    def even_open_close(cls, string: str) -> str:
        """Finds first substring of string that has same number of open and close delimiters

        Args:
            string (str): string to parse

        Raises:
            ValueError: invalid string passed to even_open_close

        Returns:
            str: substring
        """
        if Node.OPEN_DELIM not in string:
            raise ValueError(
                f'Open delimiter "{Node.OPEN_DELIM}" must be in '
                f'string passed to even_open_close "{string}"')
        open_index = string.index(Node.OPEN_DELIM)
        delim_diff = 1
        for i in range(open_index + 1, len(string)):
            if string[i] == Node.OPEN_DELIM:
                delim_diff += 1
            if string[i] == Node.CLOSE_DELIM:
                delim_diff -= 1
            if delim_diff == 0:
                return string[open_index:i + 1]
        raise ValueError(f'uneven delimiters in string "{string}" passed to even_open_close')

    @classmethod
    def parse_first_int(cls, string: str) -> tuple[int, str]:
        """Parse first int from string

        Args:
            string (str): string to parse

        Returns:
            tuple[int, str]: value of parsed int and string after int
        """
        match = re.search('[0-9]+', string)
        return int(match.group()), string[match.end():]

    @classmethod
    def parse_child(cls, child_str: str) -> str:
        """Parses first child from child_str

        Args:
            child_str (str): child string.

        Returns:
            str: first child string
        """
        nodetype, child_str = cls.parse_first_int(child_str)
        if not child_str.startswith(Node.SEP_DELIM):
            if len(child_str) == 0:
                return str(nodetype)
            if child_str.startswith(Node.CLOSE_DELIM):
                return str(nodetype)
            child_children = cls.even_open_close(child_str)
            return f'{nodetype}{child_children}'
        return str(nodetype)

    @classmethod
    def parse_children(cls, children_string) -> list[str]:
        """Parses children from children string

        Returns:
            list[str]: children strings
        """
        children_strs = []
        if len(children_string) == 0:
            return []
        while True:
            child_str = cls.parse_child(children_string)
            children_strs.append(child_str)
            children_string = children_string[len(child_str) + len(Node.SEP_DELIM):]
            if Node.OPEN_DELIM not in children_string:
                if Node.CLOSE_DELIM in children_string or len(children_string) == 0:
                    break
        return children_strs

class Node:
    invalid_children_msg = 'Attempted to assign invalid children "{children}" of type {children_type}'
    OPEN_DELIM = '('
    CLOSE_DELIM = ')'
    SEP_DELIM = ','
    STRING_IDENTIFIER = 'Node: '
    invalid_str_msg = 'Attempted to generate Node from invalid string {string}'

    @classmethod
    def validate_children(cls, new: list[Node]):
        if not hasattr(new, '__len__'):
            raise ValueError(f'Attempted to assign non iterable children "{new}" of type {type(new)}')
        if not all([isinstance(node, Node) for node in new]):
            raise ValueError(
                f'Attempted to assign non-node children '
                f'"{new}" of type [{[type(node) for node in new]}]')

    @classmethod
    def build_node_from_string(cls, string: str):
        nodetype, children_str = NodeString.parse_first_int(string)
        children_str = children_str[len(cls.OPEN_DELIM):-len(cls.CLOSE_DELIM)]
        children_strings = NodeString.parse_children(children_str)
        children = [cls.build_node_from_string(child) for child in children_strings]
        return cls(
            children=children,
            nodetype=nodetype
        )

    @classmethod
    def from_string(cls, string: str):
        try:
            if string.startswith(cls.STRING_IDENTIFIER):
                string = string[len(cls.STRING_IDENTIFIER):]
            return cls.build_node_from_string(string)
        except Exception as err:
            print(f"ERROR: {cls.invalid_str_msg.format(string=string)}")
            raise err

    def __init__(self, children: list[Node]=None, parent: Node=None, nodetype: int=0):
        if children is None:
            children = []
        self._children = None
        self.children = children
        for child in self.children:
            child.parent = self
        self.parent = parent
        self.nodetype = nodetype

    def __str__(self):
        as_str = ''
        if self.parent is None:
            as_str = self.STRING_IDENTIFIER
        if len(self.children) > 0:
            children_str = ','.join(str(child) for child in self.children)
            as_str += f'{self.nodetype}({children_str})'
        else:
            as_str += str(self.nodetype)
        return as_str

    @property
    def children(self):
        return self._children

    @children.setter
    def children(self, new: list[Node] | Node | None):
        self.validate_children(new)
        self._children = new

    def depth(self):
        if len(self.children) > 0:
            return max([child.depth() for child in self.children]) + 1
        return 1

class BinaryNode(Node):
    STRING_IDENTIFIER = 'BinaryNode: '
    @classmethod
    def validate_children(cls, new: list[Node]):
        super().validate_children(new)
        if len(new) > 2:
            raise ValueError(f'Attempted to assign {len(new)} children to BinaryTree')

    def __init__(
        self, children: list[Node]=None, parent: Node=None,
        nodetype: int=0):
        super().__init__(children=children, parent=parent, nodetype=nodetype)

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

    def __len__(self):
        return len(self.literal)

    def __getitem__(self, key):
        return self.__class__(self.literal[key], self.mut_rate)

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
        report = IndividualReport(literal, parent_literals, self.fitness)
        return report

class Report:
    @classmethod
    def from_dict(cls, as_dict: dict) -> Report:
        raise NotImplementedError()

    @classmethod
    def from_json(cls, json_path):
        raise NotImplementedError()

    def __str__(self):
        raise NotImplementedError()

    def to_dict(self) -> dict:
        raise NotImplementedError()

    def to_json(self, json_path):
        as_dict = self.to_dict()
        with open(json_path, 'w') as jfile:
            json.dump(as_dict, jfile, indent=4)

class IndividualReport(Report):
    def __init__(
        self,
        genotype_literal: str,
        parent_genotype_literals: list[str],
        fitness: float):
        self.literal = genotype_literal
        self.parent_literals = parent_genotype_literals
        self.fitness = fitness

    def to_dict(self) -> dict:
        return {
            'type': 'individual',
            'literal': self.literal,
            'parent_literals': self.parent_literals,
            'fitness': self.fitness
        }

# TODO: Add generation number to generation report
class GenerationReport(Report):
    def __init__(
        self,
        individuals: list[IndividualReport],
        highest_fitness: float,
        average_fitness: float):
        self.individuals = individuals
        self.highest_fitness = highest_fitness
        self.average_fitness = average_fitness

    def to_dict(self) -> dict:
        indiv_reports = [individual.to_dict() for individual in self.individuals]
        return {
            'type': 'generation',
            'individuals': indiv_reports,
            'highest_fitness': self.highest_fitness,
            'average_fitness': self.average_fitness
        }

class AlgorithmReport(Report):
    def __init__(
        self,
        generations: list[GenerationReport],
        runtime: float,
        memory_consumption: float=None):
        self.generations = generations
        self.runtime = runtime
        self.memory_consumption = memory_consumption

    def to_dict(self) -> dict:
        gen_reports = [generation.to_dict() for generation in self.generations]
        return {
            'type': 'algorithms',
            'generations': gen_reports,
            'runtime': self.runtime,
            'memory_consumption': self.memory_consumption
        }

class GeneticAlgorithm:
    def __init__(self, generation_size: int):
        self.generations = []
        self.generation_size = generation_size
        self._next_generation = None

    @staticmethod
    def phenotype(genotype: Genotype):
        raise NotImplementedError()

    def check_termination(self):
        raise NotImplementedError()

    def next_generation(self, generation: list[Individual]) -> list[Individual]:
        raise NotImplementedError()

    def seed_generation(self) -> list[Individual]:
        raise NotImplementedError()

    def run_generation(self, generation: list[Individual]):
        raise NotImplementedError()

    def generation_report(self, generation: list[Individual]) -> GenerationReport:
        indiv_reports = []
        for individual in generation:
            indiv_reports.append(individual.report())
        indiv_reports_sorted = copy.deepcopy(indiv_reports)
        indiv_reports_sorted.sort(key=(lambda x: x.fitness))
        average_fitness = np.sum([indiv.fitness for indiv in indiv_reports]) / len(indiv_reports)
        gen_report = GenerationReport(
            indiv_reports,
            indiv_reports_sorted[-1].fitness,
            average_fitness)
        return gen_report

    def generation_reports(self) -> list[GenerationReport]:
        reports = []
        for generation in self.generations:
            reports.append(self.generation_report(generation))
        return reports

    def algorithm_report(self, elapsed, memory=None) -> AlgorithmReport:
        gen_reports = self.generation_reports()
        algo_report = AlgorithmReport(gen_reports, elapsed, memory_consumption=memory)
        return algo_report

    def run(self):
        start = time.perf_counter()
        self._next_generation = self.seed_generation()
        while not self.check_termination():
            self.run_generation(self._next_generation)
            self.generations.append(self._next_generation)
            self._next_generation = self.next_generation(self.generations[-1])
        end = time.perf_counter()
        elapsed = end - start
        algo_report = self.algorithm_report(elapsed)
        return algo_report

if __name__ == '__main__':
    a = Binary(6)
    print(a[:])
