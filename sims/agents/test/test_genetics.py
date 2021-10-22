import unittest
from unittest import mock

import numpy as np

from sims.agents import genetics

class TestBinary(unittest.TestCase):
    def setUp(self):
        self.binary = genetics.Binary(6)

    def test__str(self):
        actual = str(self.binary)
        expected = '0b110'
        self.assertEqual(actual, expected)

    def test__int(self):
        actual = int(self.binary)
        expected = 6
        self.assertEqual(actual, expected)

    def test__len(self):
        actual = len(self.binary)
        expected = 3
        self.assertEqual(actual, expected)

    def test__eq_true(self):
        other_binary = genetics.Binary(6)
        actual = other_binary == self.binary
        expected = True
        self.assertEqual(actual, expected)

    def test__eq_false(self):
        other_binary = genetics.Binary(5)
        actual = other_binary == self.binary
        expected = False
        self.assertEqual(actual, expected)

    def test__getitem_single_1(self):
        actual = self.binary[1]
        expected = genetics.Binary(1)
        self.assertEqual(actual, expected)

    def test__getitem_single_0(self):
        actual = self.binary[2]
        expected = genetics.Binary(0)
        self.assertEqual(actual, expected)

    def test__getitem_slice_all(self):
        actual = self.binary[:]
        expected = genetics.Binary(6)
        self.assertEqual(actual, expected)

    def test__get_item_slice_partial(self):
        actual = self.binary[1:]
        expected = genetics.Binary(2)
        self.assertEqual(actual, expected)

    def test__setitem(self):
        self.binary[:] = 0
        actual = self.binary
        expected = genetics.Binary(0)
        self.assertEqual(actual, expected)

    def test_array_to_str(self):
        test_array = np.array([1, 1, 0], dtype=np.uint8)
        actual = genetics.Binary.array_to_str(test_array)
        expected = '0b110'
        self.assertEqual(actual, expected)

    def test_str_to_int(self):
        test_str = '0b110'
        actual = genetics.Binary.str_to_int(test_str)
        expected = 6
        self.assertEqual(actual, expected)

    def test_validate_literal_not_array(self):
        test_literal = 'hello'
        with self.assertRaises(ValueError):
            genetics.Binary.validate_literal(test_literal)

    def test_validate_literal_wrong_dtype(self):
        test_literal = np.array([1, 1, 0], dtype=np.uint16)
        with self.assertRaises(ValueError):
            genetics.Binary.validate_literal(test_literal)

    def test_validate_literal_true(self):
        test_literal = np.array([1, 1, 0], dtype=np.uint8)
        genetics.Binary.validate_literal(test_literal)

    def test_from_array(self):
        actual = genetics.Binary.from_array(np.array([1, 1, 0]))
        expected = self.binary
        self.assertEqual(actual, expected)

    def test_flip(self):
        self.binary.flip(2)
        actual = self.binary
        expected = genetics.Binary(7)
        self.assertEqual(actual, expected)

    @mock.patch('sims.agents.genetics.np.random.rand')
    def test_flip_random_0th_index(self, mock_rand):
        mock_rand.return_value = 0
        self.binary.flip_random()
        actual = self.binary
        expected = genetics.Binary(2)
        self.assertEqual(actual, expected)

    @mock.patch('sims.agents.genetics.np.random.rand')
    def test_flip_random_1st_index(self, mock_rand):
        mock_rand.return_value = .5
        self.binary.flip_random()
        actual = self.binary
        expected = genetics.Binary(4)
        self.assertEqual(actual, expected)

    @mock.patch('sims.agents.genetics.np.random.rand')
    def test_flip_random_2nd_index(self, mock_rand):
        mock_rand.return_value = 0.999
        self.binary.flip_random()
        actual = self.binary
        expected = genetics.Binary(7)
        self.assertEqual(actual, expected)

if __name__ == '__main__':
    unittest.main()
