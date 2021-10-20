from __future__ import annotations
import logging
import msvcrt
import os
import threading
import time
import matplotlib.pyplot as plt

import cv2 as cv
import numpy as np

from settings import Settings

if not os.path.isdir(Settings.log_path):
    os.makedirs(Settings.log_path)
logging.basicConfig(
    filename=os.path.join(Settings.log_path, 'environment.log'),
    format='%(asctime)s %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    encoding='utf-8',
    level=logging.DEBUG)

class Ui:
    def __init__(self, size=None):
        self.size = size
        if self.size is None:
            self.size = np.array([1000, 1000])

    def display_orientation(self, frame):
        return np.flip(frame.T, axis=0)

    def draw(self):
        raise NotImplementedError()

    def get_empty(self):
        raise NotImplementedError()

class Headless(Ui):
    def __init__(self, size=None, save_dir=None):
        super().__init__(size=size)
        self.save_dir = save_dir
        if self.save_dir is None:
            self.save_dir = Settings.frame_save_path
        if not os.path.isdir(self.save_dir):
            os.makedirs(self.save_dir)

    def draw(self, frame: np.ndarray, state) -> None:
        np.save(os.path.join(self.save_dir, f'{state.frame_number}.npy'), frame.astype(int))

    def get_empty(self, *args, **kwargs):
        return np.zeros(self.size, dtype=object)

class Cv(Ui):
    PIXEL_MAP = [(235, 64, 52),]
    def __init__(self, size=None, load_dir=None, out_path=None):
        super().__init__(size=size)
        self.load_dir = load_dir
        if self.load_dir is None:
            self.load_dir = Settings.frame_save_path
        self.out_path = out_path
        if self.out_path is None:
            self.out_path = Settings.video_out_path
        if not os.path.isdir(self.out_path):
            os.makedirs(self.out_path)

    def convert(self, frame: np.ndarray):
        converted = np.zeros((*frame.shape, 3))
        for i in range(len(self.PIXEL_MAP)):
            converted[frame == i] = self.PIXEL_MAP[i]
        return converted

    def to_video(self, resolution=(500, 500)):
        writer = cv.VideoWriter(os.path.join(self.out_path, 'output.avi'), cv.VideoWriter_fourcc(*"FMP4"), 10, resolution)
        for frame_file_name in os.listdir(self.load_dir):
            loaded_frame = np.load(os.path.join(self.load_dir, frame_file_name))
            loaded_frame = self.convert(loaded_frame)
            loaded_frame = np.flip(loaded_frame.transpose((1, 0, 2)), axis=0)
            loaded_frame = cv.resize(loaded_frame, resolution)
            loaded_frame = cv.cvtColor(loaded_frame.astype(np.uint8), cv.COLOR_RGB2BGR)
            writer.write(loaded_frame)
        writer.release()

class Cmd(Ui):
    """This class implements utilities to use the command line as a graphical interface
        Note: everything is scaled by height
    """
    PIXEL_MAP = [' ', '-', '|', '*', 'x']
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
        for num in range(len(self.PIXEL_MAP)):
            converted[converted == num] = self.PIXEL_MAP[num]
        return converted

    def draw(self, frame: np.ndarray, state) -> None:
        """Draws array on commandline

        Args:
            frame (np.ndarray): array to draw
        """
        self.clear()
        print('\n'.join([
            ''.join(row)
            for row in np.array(self.convert(self.display_orientation(frame)), dtype=object)]))

    def get_empty(self, default=0) -> np.ndarray:
        """Generates an array with same shape as screen.

        Args:
            default (int, optional): Value to fill empty array with. Defaults to 0.

        Returns:
            np.ndarray: empty array
        """
        return np.array(np.zeros(self.size) + default, dtype=object)

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
        self.lock = threading.RLock()

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
    # test = TestLoop()
    # test.run()
    # cv.imshow('test', np.zeros((500, 500)))
    # while cv.getWindowProperty('test', cv.WND_PROP_VISIBLE) > 0:
    #     cv.waitKey(50)
    ui = Cv()
    ui.to_video()
