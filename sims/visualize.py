from __future__ import annotations
import logging
import os

import cv2 as cv
import numpy as np

from settings import Settings
from sims.environments import common

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
        self.shape = size

    def display_orientation(self, frame):
        return np.flip(frame.T, axis=0)

    def draw(self):
        raise NotImplementedError()

    def get_empty(self):
        raise NotImplementedError()

    def get_empty(self):
        return np.zeros(self.shape, dtype=object)

class Cv(Ui):
    PIXEL_MAP = [(179, 232, 211), (0, 0, 0), (84, 98, 107), (209, 196, 50)]
    def __init__(self, size, out_path):
        super().__init__(size)
        self.out_path = out_path
        common.build_path(self.out_path)

    def convert(self, frame: np.ndarray):
        converted = np.zeros((*frame.shape, 3))
        for i in range(len(self.PIXEL_MAP)):
            converted[frame == i] = self.PIXEL_MAP[i]
        return converted

    def to_video(self, frames, fps, frame_size=None):
        if frame_size is None:
            frame_size = self.shape
        writer = cv.VideoWriter(
            os.path.join(self.out_path, 'cv_visual.avi'),
            cv.VideoWriter_fourcc(*"FMP4"),
            fps,
            frame_size)
        for frame_index in range(len(frames)):
            print(f'processing frame {frame_index}')
            loaded_frame = np.array(frames[frame_index])
            loaded_frame = self.convert(loaded_frame)
            loaded_frame = np.flip(loaded_frame.transpose((1, 0, 2)), axis=0)
            loaded_frame = cv.resize(loaded_frame, frame_size)
            loaded_frame = cv.cvtColor(loaded_frame.astype(np.uint8), cv.COLOR_RGB2BGR)
            writer.write(loaded_frame)
        writer.release()
