import numpy as np

class Node:
    def __init__(self, parent):
        self.parent = parent

    def evaluate(self):
        raise NotImplementedError

class BinaryFunctional(Node):
    def __init__(self, parent, child1, child2):
        super().__init__(parent)
        self.children = [child1, child2]
        self.children_values = list()

    def operate(self):
        raise NotImplementedError

    def evaluate(self):
        self.children_values = np.array([child.evaluate() for child in self.children])
        return self.operate()

class Addition(BinaryFunctional):
    def __init__(self, parent, children):
        super().__init__(parent, children)

    def operate(self):
        return self.children_values.sum()

class Subtraction(BinaryFunctional):
    def __init__(self, parent, children):
        super().__init__(parent, children)

    def operate(self):
        return self.children_values[1] - self.children_values[0]

class Multiplication(BinaryFunctional):
    def __init__(self, parent, children):
        super().__init__(parent, children)

    def operate(self):
        return self.children_values[1] * self.children_values[0]

class Division(BinaryFunctional):
    def __init__(self, parent, children):
        super().__init__(parent, children)

    def operate(self):
        return self.children_values[1] / self.children_values[0]

class Numerical(Node):
    def __init__(self, parent, value):
        super().__init__(parent, list(), children_values=None)
        self.value = value

    def operate(self):
        return self.value

