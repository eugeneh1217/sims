from __future__ import annotations
import logging
import msvcrt
import os
import threading

import numpy as np

from sims.settings import GameSettings

if not os.path.isdir(GameSettings.log_path):
    os.makedirs(GameSettings.log_path)
logging.basicConfig(
    filename=os.path.join(GameSettings.log_path, 'loop.log'),
    format='%(asctime)s %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    encoding='utf-8',
    level=logging.DEBUG)

class Cmd:
    """This class implements utilities to use the command line as a graphical interface
        Note: everything is scaled by height
    """
    @property
    def size(self):
        return tuple(os.get_terminal_size())

    def clear(self):
        os.system('cls' if os.name in ('nt', 'dos') else 'clear')

    def convert(self, int_array: np.ndarray) -> np.ndarray:
        """Maps an array of supported integers to symbols

        Args:
            int_array (np.ndarray): integer array to convert

        Returns:
            np.ndarray: symbol array
        """
        converted = np.array(int_array, dtype=object)
        converted[converted == 0] = ' '
        converted[converted == 1] = '_'
        converted[converted == 2] = '|'
        return converted

    def draw(self, frame: np.ndarray):
        """Draws array on commandline

        Args:
            frame (np.ndarray): array to draw
        """
        self.clear()
        print('\n'.join([
            ''.join(row)
            for row in self.convert(frame.T)]))

    def get_empty(self, default=0) -> np.ndarray:
        """Generates an array with same shape as screen.

        Args:
            default (int, optional): Value to fill empty array with. Defaults to 0.

        Returns:
            np.ndarray: empty array
        """
        return np.zeros(self.size) + default

class Loop:
    """This abstract class defines an object that runs several loops in parallel.
        Usage: Override main loop. Custom loops can be defined with the @loop decorator.
            Custom loops define what occurs in each cycle of the loop.
            If custom loops are defined, run method must be overriden to run the custom loop.

    Raises:
        NotImplementedError: main loop is not overriden, but called
    """
    TERMINATE_SYMBOL = b'q'
    def __init__(self):
        self._last_key = None
        self.lock = threading.Lock()

    @property
    def last_key(self):
        with self.lock:
            last = self._last_key
        return last

    @last_key.setter
    def last_key(self, new):
        with self.lock:
            self._last_key = new

    def loop(func: function) -> function:
        """Decorator to run method in a loop that terminates with terminate method.

        Args:
            func (function): function to decorate
        """
        def inner(self, *args, **kwargs):
            while True:
                if self.terminate():
                    break
                func(self, *args, **kwargs)
        return inner

    def terminate(self) -> bool:
        """Returns True if loops should terminate, False if otherwise

        Returns:
            bool: should terminate
        """
        return self.last_key == self.TERMINATE_SYMBOL

    @loop
    def user(self):
        """Default loop to listen for user input.
        """
        self.last_key = msvcrt.getch()
        logging.debug(f'key {self.last_key} detected')

    @loop
    def main(self):
        """Default method to run every frame. Should be overriden.

        Raises:
            NotImplementedError: main not overriden
        """
        raise NotImplementedError()

    def run(self):
        """Starts and waits for loops user and main loops run on separate threads, and joins them.
            Should be overriden if custom loops are defined.
        """
        logging.debug(f'starting {self.__class__.__name__} loop')
        main_thread = threading.Thread(target=self.main)
        user_thread = threading.Thread(target=self.user, daemon=True)
        main_thread.start()
        user_thread.start()
        main_thread.join()
        user_thread.join()

class TestLoop(Loop):
    @Loop.loop
    def main(self):
        print(self.last_key)

if __name__ == '__main__':
    test = TestLoop()
    test.run()
