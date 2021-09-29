import unittest
import numpy as np

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
                        genetics.Ln(
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
                        genetics.Ln(
                            genetics.Leaf(6)
                        )
                    )
                )
            )
        )

    def test_eval(self):
        self.assertEqual((5 * 7 / np.log(9)) + (16 ** .5 - .8 * np.log(6)), self.sample_tree.evaluate())

if __name__ == '__main__':
    unittest.main()
