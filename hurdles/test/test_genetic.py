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

if __name__ == '__main__':
    unittest.main()
