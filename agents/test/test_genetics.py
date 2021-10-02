import unittest
import numpy as np
import math

from hurdles import genetics

class TestGenetic(unittest.TestCase):
    def setUp(self):
        # (5 * 7 / ln(9)) + (16 ** .5 - .8 * ln(6))
        self.sample_tree = genetics.Root(
            genetics.Add(
                genetics.Multiply(
                    genetics.Leaf(5),
                    genetics.Divide(
                        genetics.Leaf(7),
                        genetics.Log(
                            genetics.Leaf(2),
                            genetics.Leaf(9)
                        )
                    )
                ),
                genetics.Subtract(
                    genetics.Exponentiate(
                        genetics.Leaf(16),
                        genetics.Leaf(0.5)
                    ),
                    genetics.Multiply(
                        genetics.Leaf(0.8),
                        genetics.Log(
                            genetics.Leaf(8),
                            genetics.Leaf(6)
                        )
                    )
                )
            )
        )

    def test_eval(self):
        self.assertAlmostEqual((5 * 7 / math.log(2, 9)) + (16 ** .5 - .8 * math.log(8, 6)), self.sample_tree.evaluate())

    def test_root_inavlid_child(self):
        with self.assertRaises(ValueError):
            genetics.Root('apple')

    def test_root_valid_child(self):
        genetics.Root(genetics.Leaf(5))
        genetics.Root(genetics.Node())

    def test_functional_invalid_child(self):
        with self.assertRaises(ValueError):
            genetics.Functional(genetics.Root(genetics.Leaf(5)), genetics.Leaf(5))

    def test_functional_valid_child(self):
            genetics.Functional((genetics.Leaf(5)), genetics.Leaf(5))
            genetics.Functional(genetics.Functional(
                genetics.Leaf(5), genetics.Leaf(5)), genetics.Leaf(5))

if __name__ == '__main__':
    unittest.main()
