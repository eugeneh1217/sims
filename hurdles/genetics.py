from __future__ import annotations
import typing
import numpy as np
import math

class Node:
    def _left(self):
        raise NotImplementedError()

    def _right(self):
        raise NotImplementedError()

    def evaluate(self):
        raise NotImplementedError()

    def _validate_child(self, child: Node):
        if not any([isinstance(child, child_type) for child_type in self.VALID_CHILD_TYPES]):
            raise ValueError()

class Leaf(Node):
    def __init__(self, value: float):
        self.value = value

    def evaluate(self):
        return self.value

class Root(Node):
    VALID_CHILD_TYPES = (Node, )
    def __init__(self, left: Node):
        self.left = left

    @property
    def left(self):
        return self._left

    @left.setter
    def left(self, child: Node):
        self._validate_child(child)
        self._left = child

    def evaluate(self):
        return self.left.evaluate()

class Functional(Node):
    def __init__(self, left: Node, right: Node):
        self._left = left
        self._right = right

    @property
    def left(self):
        return self._left

    @property
    def right(self):
        return self._right

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
