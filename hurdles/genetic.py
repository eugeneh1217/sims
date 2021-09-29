import typing
import numpy as np

class Node:
    def __init__(self, parent: Node, children: list[Node]):
        self.parent = parent
        self.children = children

    def evaluate(self):
        raise NotImplementedError()

class Root(Node):
    CHILD_COUNT = 1
    def __init__(self, children: list[Node]):
        super().__init__(None, children)

    def evaluate(self):
        return self.children[0].evaluate()

class Leaf(Node):
    def __init__(self, parent: Node, value: float):
        super().__init__(parent, None)
        self.value = value

    def evaluate(self):
        return self.value

class FunctionalNode(Node):
    def __init__(self, parent: Node, children: list[Node]):
        super().__init__(parent, children)
        self._children_values = list()

    def function(self):
        raise NotImplementedError()

    def evaluate(self):
        self.children_values = np.array([child.evaluate() for child in self.children])
        return self.function()

class BinaryFunctional(FunctionalNode):
    CHILD_COUNT = 2

class Addition(BinaryFunctional):
    def function(self):
        return self.children_values.sum()

class Subtraction(BinaryFunctional):
    def function(self):
        return self.children_values[1] - self.children_values[0]

class Multiplication(BinaryFunctional):
    def function(self):
        return self.children_values[1] * self.children_values[0]

class Division(BinaryFunctional):
    def function(self):
        return self.children_values[1] / self.children_values[0]

class MonoFunctional(FunctionalNode):
    CHILD_COUNT = 1

class LnFunctional(MonoFunctional):
    def function(self):
        return np.log(self.children[0])
