import unittest
from unittest import mock

import numpy as np

from sims.agents import genetics

class TestBinary(unittest.TestCase):
    def setUp(self):
        self.binary = genetics.Binary(6)

    def test_from_str(self):
        actual = genetics.Binary('0b110')
        expected = self.binary
        self.assertEqual(actual, expected)

    def test_from_str_prefix_zeros(self):
        actual = genetics.Binary('0b0110').literal
        expected = np.array([0, 1, 1, 0], dtype=np.uint8)
        np.testing.assert_array_equal(actual, expected)

    def test_from_array(self):
        actual = genetics.Binary(np.array([1, 1, 0]))
        expected = self.binary
        self.assertEqual(actual, expected)

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

    def test__eq_false_value(self):
        other_binary = genetics.Binary(5)
        actual = other_binary == self.binary
        expected = False
        self.assertEqual(actual, expected)

    def test__eq_false_prefix(self):
        other_binary = genetics.Binary('0b0110')
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
        expected = genetics.Binary('0b000')
        self.assertEqual(actual, expected)

    def test_array_to_str(self):
        test_array = np.array([1, 1, 0])
        actual = genetics.Binary.array_to_str(test_array)
        expected = '0b110'
        self.assertEqual(actual, expected)

    def test_str_to_int(self):
        test_str = '0b110'
        actual = genetics.Binary(test_str)
        expected = genetics.Binary(6)
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

    def test_append_ndarray(self):
        self.binary.append(np.array([1, 0]))
        actual = self.binary
        expected = genetics.Binary(26)
        self.assertEqual(actual, expected)

    def test_append_binary(self):
        self.binary.append(genetics.Binary(2))
        actual = self.binary
        expected = genetics.Binary(26)
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
        expected = genetics.Binary('0b010')
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

class TestNbit(unittest.TestCase):
    def setUp(self):
        self.nbit_a = genetics.Nbit(genetics.Binary(157), 2)
        self.nbit_b = genetics.Nbit(genetics.Binary(12), 2)

    @mock.patch('sims.agents.genetics.np.random.rand')
    def test_mutate_0th(self, mock_rand):
        mock_rand.return_value = 0
        self.nbit_a.mutate()
        actual = str(self.nbit_a.literal)
        expected = '0b00011101'
        self.assertEqual(actual, expected)

    @mock.patch('sims.agents.genetics.np.random.rand')
    def test_mutate_4th(self, mock_rand):
        mock_rand.return_value = 0.125 * 4
        self.nbit_a.mutate()
        actual = str(self.nbit_a.literal)
        expected = '0b10010101'
        self.assertEqual(actual, expected)

    @mock.patch('sims.agents.genetics.np.random.rand')
    def test_mutate_last(self, mock_rand):
        mock_rand.return_value = 0.125 * 7
        self.nbit_a.mutate()
        actual = str(self.nbit_a.literal)
        expected = '0b10011100'
        self.assertEqual(actual, expected)

    def test_append_nbit(self):
        self.nbit_a.append(self.nbit_b)
        actual = self.nbit_a.literal
        expected = genetics.Binary('0b100111011100')
        self.assertEqual(actual, expected)

    def test_append_Binary(self):
        self.nbit_a.append(self.nbit_b.literal)
        actual = self.nbit_a.literal
        expected = genetics.Binary('0b100111011100')
        self.assertEqual(actual, expected)

    def test_append_array(self):
        self.nbit_a.append(self.nbit_b.literal.literal)
        actual = self.nbit_a.literal
        expected = genetics.Binary('0b100111011100')
        self.assertEqual(actual, expected)

    def test_crossover(self):
        print(self.nbit_a.literal, self.nbit_b.literal)
        offspring = self.nbit_a.crossover(self.nbit_b, 2)
        actual = str(offspring[0].literal), str(offspring[1].literal)
        expected = ('0b1000', '0b11011101')
        self.assertEqual(actual, expected)

if __name__ == '__main__':
    unittest.main()
