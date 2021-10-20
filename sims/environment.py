from __future__ import annotations
import logging
import os

import cv2 as cv
import numpy as np

from settings import Settings
from sims.hurdles import common

if not os.path.isdir(Settings.log_path):
    os.makedirs(Settings.log_path)
logging.basicConfig(
    filename=os.path.join(Settings.log_path, 'environment.log'),
    format='%(asctime)s %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    encoding='utf-8',
    level=logging.DEBUG)

class Ui:
    def __init__(self, size):
        self.size = size

    def display_orientation(self, frame):
        return np.flip(frame.T, axis=0)

    def draw(self):
        raise NotImplementedError()

    def get_empty(self):
        raise NotImplementedError()

class Headless(Ui):
    def __init__(self, size, save_dir):
        super().__init__(size)
        self.save_dir = save_dir
        common.build_path(self.save_dir)

    def draw(self, frame: np.ndarray, state) -> None:
        np.save(os.path.join(self.save_dir, f'{state.frame_number}.npy'), frame.astype(int))

    def get_empty(self):
        return np.zeros(self.size, dtype=object)

class Cv(Ui):
    PIXEL_MAP = [(235, 64, 52),]
    def __init__(self, size, load_dir, out_path):
        super().__init__(size)
        self.load_dir = load_dir
        self.out_path = out_path
        common.build_path(self.load_dir)
        common.build_path(self.out_path)

    def convert(self, frame: np.ndarray):
        converted = np.zeros((*frame.shape, 3))
        for i in range(len(self.PIXEL_MAP)):
            converted[frame == i] = self.PIXEL_MAP[i]
        return converted

    def to_video(self, frame_size, fps):
        writer = cv.VideoWriter(
            os.path.join(self.out_path, 'output.avi'),
            cv.VideoWriter_fourcc(*"FMP4"),
            fps,
            frame_size)
        for frame_num in range(Settings.frames):
            print(f"processing: frame {frame_num}")
            loaded_frame = np.load(os.path.join(self.load_dir, f"{frame_num}.npy"))
            loaded_frame = self.convert(loaded_frame)
            loaded_frame = np.flip(loaded_frame.transpose((1, 0, 2)), axis=0)
            loaded_frame = cv.resize(loaded_frame, frame_size)
            loaded_frame = cv.cvtColor(loaded_frame.astype(np.uint8), cv.COLOR_RGB2BGR)
            writer.write(loaded_frame)
        writer.release()
