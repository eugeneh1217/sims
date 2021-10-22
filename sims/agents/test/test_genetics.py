import unittest
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
        print(str(actual), str(expected))
        self.assertEqual(actual, expected)

    def test_array_to_str(self):
        pass

    def test_str_to_int(self):
        pass

    def test_validate_literal(self):
        pass

    def test_from_array(self):
        pass

    def test_setter(self):
        pass

    def test_flip(self):
        pass

    def test_flip_random(self):
        pass

if __name__ == '__main__':
    unittest.main()
