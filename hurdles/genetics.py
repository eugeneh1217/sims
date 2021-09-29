import typing
import numpy as np

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

class BinaryFunctional(Node):
    def __init__(self, left: Node, right: Node):
        self.left = left
        self.right = right

    def _left(self):
        return self.left.evaluate()

    def _right(self):
        return self.right.evaluate()

class Add(BinaryFunctional):
    def evaluate(self):
        return self._left() + self._right()

class Subtract(BinaryFunctional):
    def evaluate(self):
        return self._left() - self._right()

class Multiply(BinaryFunctional):
    def evaluate(self):
        return self._left() * self._right()

class Divide(BinaryFunctional):
    def evaluate(self):
        return self._left() / self._right()

class Exponentiate(BinaryFunctional):
    def evaluate(self):
        return self._left() ** self._right()

class Ln(SingleChild):
    def evaluate(self):
        return np.log(self._left())
