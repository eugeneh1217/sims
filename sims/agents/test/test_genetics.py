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
        offspring = self.nbit_a.crossover(self.nbit_b, 2)
        actual = str(offspring[0].literal), str(offspring[1].literal)
        expected = ('0b1000', '0b11011101')
        self.assertEqual(actual, expected)

class TestNodeString(unittest.TestCase):
    def test_even_open_close(self):
        valid_mock_str = '1(1,2(3,4)),()'
        valid_actual = genetics.NodeString.even_open_close(valid_mock_str)
        valid_expected = '(1,2(3,4))'
        self.assertEqual(valid_actual, valid_expected)
        uneven_mock_str = '1(1,2(3,4),()'
        with self.assertRaises(ValueError):
            genetics.NodeString.even_open_close(uneven_mock_str)
        no_open_mock_str = '1'
        with self.assertRaises(ValueError):
            genetics.NodeString.even_open_close(no_open_mock_str)

    def test_parse_first_int(self):
        int_first_mock_str = '12312(1,2,3)'
        int_first_actual = genetics.NodeString.parse_first_int(int_first_mock_str)
        int_first_expected = (12312, '(1,2,3)')
        self.assertEqual(int_first_actual, int_first_expected)
        prematter_mock_str = 'ab(12312(1,2,3)'
        prematter_actual = genetics.NodeString.parse_first_int(prematter_mock_str)
        prematter_expected = (12312, '(1,2,3)')
        self.assertEqual(prematter_actual, prematter_expected)

    def test_parse_child(self):
        grand_children_mock_child = '123(2,3(3,4),1),43(1,2)'
        grand_children_actual = genetics.NodeString.parse_child(grand_children_mock_child)
        grand_children_expected = '123(2,3(3,4),1)'
        self.assertEqual(grand_children_actual, grand_children_expected)
        child_mock_child = '23,3(2,3)'
        child_actual = genetics.NodeString.parse_child(child_mock_child)
        child_expected = '23'
        self.assertEqual(child_actual, child_expected)
        no_grandchildren_mock_child = '1,23'
        no_grandchildren_actual = genetics.NodeString.parse_child(no_grandchildren_mock_child)
        no_grandchildren_expected = '1'
        self.assertEqual(no_grandchildren_actual, no_grandchildren_expected)
        single_mock_child = '23'
        single_actual = genetics.NodeString.parse_child(single_mock_child)
        single_expected = '23'
        self.assertEqual(single_actual, single_expected)

    def test_parse_children(self):
        nested_mock_children_str = '123(2,3(3,4),1),43(1,2),23,4(3,2)'
        nested_actual = genetics.NodeString.parse_children(nested_mock_children_str)
        nested_expected = ['123(2,3(3,4),1)', '43(1,2)', '23', '4(3,2)']
        self.assertListEqual(nested_actual, nested_expected)
        unnested_mock_children_str = '1,23'
        unnested_actual = genetics.NodeString.parse_children(unnested_mock_children_str)
        unnested_expected = ['1', '23']
        self.assertListEqual(unnested_actual, unnested_expected)
        single_mock_children_str = '1'
        single_actual = genetics.NodeString.parse_children(single_mock_children_str)
        single_expected = ['1']
        self.assertListEqual(single_actual, single_expected)
        mock_children_str = '4(5),3(6,7),7'
        actual = genetics.NodeString.parse_children(mock_children_str)
        expected = ['4(5)', '3(6,7)', '7']
        self.assertListEqual(actual, expected)

class TestNodeFromString(unittest.TestCase):
    def setUp(self):
        self.mock_tree = genetics.Node(
            children=[
                genetics.Node(children=[
                    genetics.Node(nodetype=5)
                ], nodetype=4),
                genetics.Node(children=[
                    genetics.Node(nodetype=6),
                    genetics.Node(nodetype=7)
                ], nodetype=3),
                genetics.Node(nodetype=7)
            ], nodetype=1
        )
        self.mock_tree_string = 'Node: 1(4(5),3(6,7),7)'

    def test_str_(self):
        actual = str(self.mock_tree)
        expected = self.mock_tree_string
        self.assertEqual(actual, expected)

    def test_from_string(self):
        actual = genetics.Node.from_string(self.mock_tree_string)
        expected = self.mock_tree
        self.assertEqual(str(actual), str(expected))

class TestNode(unittest.TestCase):
    def test_validate_children(self):
        non_iterable_children = genetics.Node(nodetype=1)
        with self.assertRaises(ValueError):
            genetics.Node(children=non_iterable_children)
        non_node_children = [genetics.Node(nodetype=1), 'a']
        with self.assertRaises(ValueError):
            genetics.Node(children=non_node_children)

    def test_depth(self):
        deepest_not_first = genetics.Node.from_string('1(2,3(4,5(2)),4(2(3),4))')
        deepest_not_first_actual = deepest_not_first.depth()
        deepest_not_first_expected = 4
        self.assertEqual(deepest_not_first_actual, deepest_not_first_expected)

    def test_pop_child(self):
        pop_index = 1
        mock_node = genetics.Node.from_string('1(2,3(4),2(1,2))')
        returned_actual = mock_node.pop_child(pop_index)
        returned_expected = genetics.Node.from_string('3(4)')
        self.assertEqual(str(returned_actual), str(returned_expected))
        expected_mock_node_after = genetics.Node.from_string('1(2,2(1,2))')
        self.assertEqual(mock_node, expected_mock_node_after)

    def test_insert(self):
        insert_index = 1
        child = genetics.Node.from_string('3(4)')
        mock_node = genetics.Node.from_string('1(2,2(1,2))')
        mock_node.insert_child(insert_index, child)
        expected_node_after = genetics.Node.from_string('1(2,3(4),2(1,2))')
        self.assertEqual(mock_node, expected_node_after)
        expected_child_parent = mock_node
        self.assertEqual(child.parent, expected_child_parent)        

    def test_descendents(self):
        mock_node = genetics.Node.from_string('1(2(3,4),5(6(7),8))')
        actual = [descendent.nodetype for descendent in mock_node.descendents()]
        expected = [1, 2, 3, 4, 5, 6, 7, 8]
        self.assertListEqual(actual, expected)

class TestBinaryNodeFromString(unittest.TestCase):
    def setUp(self):
        self.mock_binary_tree = genetics.BinaryNode(
            [
                genetics.BinaryNode(
                    [
                        genetics.BinaryNode(nodetype=1)
                    ], nodetype=4),
                genetics.BinaryNode(
                    [
                        genetics.BinaryNode(
                            [
                                genetics.BinaryNode(nodetype=3),
                                genetics.BinaryNode(nodetype=2)
                            ],nodetype=2)
                    ], nodetype=4)
            ], nodetype=1
        )
        self.mock_binary_tree_str = 'BinaryNode: 1(4(1),4(2(3,2)))'

    def test_from_string(self):
        actual = genetics.BinaryNode.from_string(self.mock_binary_tree_str)
        expected = self.mock_binary_tree_str
        self.assertEqual(str(actual), expected)

    def test_str(self):
        actual = str(self.mock_binary_tree)
        expected = self.mock_binary_tree_str
        self.assertEqual(actual, expected)

class TestBinaryNode(unittest.TestCase):
    def test_validate_children(self):
        non_iterable_children = genetics.Node(nodetype=1)
        with self.assertRaises(ValueError):
            genetics.BinaryNode(children=non_iterable_children)
        non_node_children = [genetics.Node(nodetype=1), 'a']
        with self.assertRaises(ValueError):
            genetics.BinaryNode(children=non_node_children)
        too_long_children = [
            genetics.Node(nodetype=1),
            genetics.Node(nodetype=2),
            genetics.Node(nodetype=3)
        ]
        with self.assertRaises(ValueError):
            genetics.BinaryNode(children=too_long_children)

if __name__ == '__main__':
    unittest.main()
