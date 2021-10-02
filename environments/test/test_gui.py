import unittest
from unittest import mock
import numpy as np

from environments import gui

@mock.patch(
        'environments.gui.os.get_terminal_size', mock.Mock(return_value=(2, 2)))
class TestCmd(unittest.TestCase):
    def setUp(self):
        self.cmd = gui.Cmd()
        self.test_frame = np.array([
            np.arange(3),
            np.arange(3)])

    def test_get_empty(self):
        np.testing.assert_array_equal(
            self.cmd.get_empty(default=10),
            np.array([[10, 10], [10, 10]]))

    def test_convert(self):
        np.testing.assert_array_equal(
            self.cmd.convert(self.test_frame),
            np.array([[' ', '_', '|'], [' ', '_', '|']]))

    @mock.patch('builtins.print')
    def test_draw(self, mock_print):
        self.cmd.draw(self.test_frame)
        mock_print.assert_called_with('  \n__\n||')

if __name__ == '__main__':
    unittest.main()
