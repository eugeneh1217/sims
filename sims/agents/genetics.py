from __future__ import annotations
import typing
import numpy as np
import math

class Node:
    def _get_valid_children_types(self):
        raise NotImplementedError()

    @classmethod
    def _validate_child(cls, child: Node):
        if not any([isinstance(child, child_type)
                    for child_type in cls._get_valid_children_types()]):
            raise ValueError(
                f'"{type(child)}" child invalid for "{type(cls)}" parent')

    def evaluate(self):
        raise NotImplementedError()

class Root(Node):
    def __init__(self, left: Node):
        self.left = left

    @property
    def left(self):
        return self._left

    @left.setter
    def left(self, child: Node):
        self._validate_child(child)
        self._left = child

    @classmethod
    def _get_valid_children_types(cls):
        return (Node, )

    def evaluate(self):
        return self.left.evaluate()

class Leaf(Node):
    def __init__(self, value: float):
        self.value = value

    def evaluate(self):
        return self.value

class Functional(Node):
    def __init__(self, left: Node, right: Node):
        self.left = left
        self.right = right

    @property
    def left(self):
        return self._left

    @left.setter
    def left(self, child: Node):
        self._validate_child(child)
        self._left = child

    @property
    def right(self):
        return self._right

    @right.setter
    def right(self, child: Node):
        self._validate_child(child)
        self._right = child

    @classmethod
    def _get_valid_children_types(cls):
        return (Functional, Leaf)

    def _function(self, a, b):
        raise NotImplementedError()

    def evaluate(self):
        return self._function(self.left.evaluate(), self.right.evaluate())

class Add(Functional):
    def _function(self, a, b):
        return a + b

class Subtract(Functional):
    def _function(self, a, b):
        return a - b

class Multiply(Functional):
    def _function(self, a, b):
        return a * b

class Divide(Functional):
    def _function(self, a, b):
        return a / b

class Exponentiate(Functional):
    def _function(self, a, b):
        return a ** b

class Log(Functional):
    def _function(self, a, b):
        return math.log(a, b)
