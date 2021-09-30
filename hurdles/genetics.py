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

class Leaf(Node):
    def __init__(self, value: float):
        self.value = value

    def evaluate(self):
        return self.value

class SingleChild(Node):
    def __init__(self, left: Node):
        self.left = left

    def _left(self):
        return self.left.evaluate()

class Root(SingleChild):
    def evaluate(self):
        return self._left()

class Functional(Node):
    def __init__(self, left: Node, right: Node):
        self.left = left
        self.right = right

    def _left(self):
        return self.left.evaluate()

    def _right(self):
        return self.right.evaluate()

class Add(Functional):
    def evaluate(self):
        return self._left() + self._right()

class Subtract(Functional):
    def evaluate(self):
        return self._left() - self._right()

class Multiply(Functional):
    def evaluate(self):
        return self._left() * self._right()

class Divide(Functional):
    def evaluate(self):
        return self._left() / self._right()

class Exponentiate(Functional):
    def evaluate(self):
        return self._left() ** self._right()

class Log(Functional):
    def evaluate(self):
        return math.log(self._left(), self._right())
