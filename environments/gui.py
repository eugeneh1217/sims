import os

import numpy as np

class Cmd:
    """Command Line GUI.
        Note: Everything is scaled by height
    """
    @property
    def size(self):
        return tuple(os.get_terminal_size())

    def clear(self):
        os.system('cls' if os.name in ('nt', 'dos') else 'clear')

    def convert(self, int_array: np.ndarray):
        converted = np.array(int_array, dtype=object)
        converted[converted == 0] = ' '
        converted[converted == 1] = '_'
        converted[converted == 2] = '|'
        return converted

    def draw(self, frame: np.ndarray):
        self.clear()
        print('\n'.join([
            ''.join(row)
            for row in self.convert(frame.T)]))

    def get_empty(self, default=0):
        return np.zeros(self.size) + default
