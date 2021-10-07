from future import __annotations__
import time

import numpy as np

from environment import loop, gui

class HurdleLoop(loop.Loop):
    def __init__(self, fps=30):
        super().__init__()
        self.ui = gui.Cmd()
        self.fps = fps

    @loop.Loop.loop
    def main(self):
        time.sleep(1 / self.fps)
        self.ui.clear()
        self.ui.draw(self.ui.get_empty(default=1))

class HurdleGame:
    def __init__(self):
        self.gameobjects = []
        self.ground = GameObject()

    def isgrounded(self, gameobject: GameObject):
        if

class GameObject:
    def __init__(
        self, width, height
        position: np.ndarray=None,
        velocity: np.ndarray=None,
        acceleration: np.ndarray=None):
        self.width = width
        self.height = height
        self.displacement = displacement
        if self.displacement is None:
            self.displacement = np.zeros(2)
        self.velocity = velocity
        if self.velocity is None:
            self.velocity = np.zeros(2)
        self.acceleration = acceleration
        if self.acceleration is None:
            self.acceleration = np.zeros(2)

    def get_top(self):
        return self.position[1] + self.height

    def get_bottom(self):
        return self.position[1]

    def get_left(self):
        return self.position[0]

    def get_right(self):
        return self.position[0] + self.width

    def is_colliding(self, other: GameObject):
        if self.get_left() > other.get_right() or self.get_right() < other.get_left():
            if self.get_bottom() > other.get_top() or self.get_top() < other.get_bottom():
                return True
        return False

    def is_grounded(self):
        if self.get_bottom() <= self.floor.position[1]:
            return True
        return False

    def move(self):
        self.velocity += self.acceleration
        self.displacement += self.velocity

if __name__ == '__main__':
    hurdle = HurdleLoop()
    hurdle.run()