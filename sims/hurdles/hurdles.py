from __future__ import annotations

import numpy as np

from sims import environment as env
from settings import Settings

class HurdleLoop(env.Loop):
    def __init__(self, ui=None):
        super().__init__()
        if ui == 'CMD':
            self.ui = env.Cmd()
        if ui is None:
            self.ui = env.Headless()
        self.gameobjects = {Ground.name: Ground(Settings.ground_height)}
        self.gameobjects[Hurdler.name] = [Hurdler(self.gameobjects['ground']), ]
        self.gameobjects[Hurdle.name] = [Hurdle(self.gameobjects['ground'], Settings.hurdle_spawn_x), ]
        self.frame_number = 0
        self.frame = self.ui.get_empty()

    def terminate(self):
        return self.frame_number == 100

    def remove_gameobject(self, gameobject):
        gameobjects_list = self.gameobjects[gameobject.name]
        gameobjects_list.remove(gameobject)

    def get_state(self) -> StatePacket:
        return StatePacket(self.frame_number, self.last_key)

    def run_gameobject(self, gameobject):
        state = self.get_state()
        gameobject.act(state)
        if gameobject.terminated:
            self.remove_gameobject(gameobject)
            return
        gameobject.draw(self.frame)

    @env.Loop.loop
    def main(self):
        self.frame = self.ui.get_empty(default=0)
        with self.lock:
            for gameobject_type in self.gameobjects.values():
                if hasattr(gameobject_type, '__iter__'):
                    for gameobject in gameobject_type:
                        self.run_gameobject(gameobject)
                else:
                    self.run_gameobject(gameobject_type)
            self.frame_number += 1
            if self.last_key != self.TERMINATE_SYMBOL:
                self.last_key = None
        self.ui.draw(self.frame, self.get_state())

class StatePacket:
    def __init__(self, frame_number, userin):
        self.frame_number = frame_number
        self.userin = userin

class GameObject:
    terminated = False
    def __init__(self):
        self.displacement = 0
        self.velocity = 0
        self.acceleration = 0

    def terminate(self):
        self.terminated = True

    def draw(self, frame: np.ndarray):
        raise NotImplementedError()

class Hurdler(GameObject):
    name = 'hurdler'
    def __init__(self, ground):
        super().__init__()
        self.ground = ground
        self.displacement = np.array([10, self.ground.top()])

    def isgrounded(self):
        return self.displacement[1] - self.ground.top() <= 0

    def jump(self):
        if self.isgrounded():
            self.velocity += np.array([0, Settings.hurdler_jump_speed])

    def act(self, state: StatePacket):
        if state.frame_number % 25 == 0:
            self.jump()
        self.move()

    def move(self):
        if not self.isgrounded():
            self.acceleration = Settings.gravity
        self.velocity += self.acceleration
        self.displacement += self.velocity
        if self.isgrounded():
            self.displacement = np.array([self.displacement[0], self.ground.top()])

    def draw(self, frame: np.ndarray):
        frame[
            self.displacement[0]: self.displacement[0] + Settings.hurdler_width,
            self.displacement[1]: self.displacement[1] + Settings.hurdler_height] = 3

class Hurdle(GameObject):
    name = 'hurdle'
    def __init__(self, ground: Ground, spawn_x: int):
        super().__init__()
        self.ground = ground
        self.displacement = np.array([spawn_x, self.ground.top()])

    def act(self, state: StatePacket):
        self.move()

    def move(self):
        self.displacement += Settings.hurdle_drift
        if self.displacement[0] < 0:
            self.terminate()

    def draw(self, frame: np.ndarray):
        frame[
            self.displacement[0]: self.displacement[0] + Settings.hurdle_width,
            self.displacement[1]: self.displacement[1] + Settings.hurdle_height] = 4

class Ground(GameObject):
    name = 'ground'
    def __init__(self, ground_height):
        self.displacement = np.array([0, ground_height])

    def top(self):
        return self.displacement[1] + 1

    def act(self, state: StatePacket):
        pass

    def draw(self, frame: np.ndarray):
        frame[:, self.displacement[1]] = 1

if __name__ == '__main__':
    hurdle = HurdleLoop()
    hurdle.run()
    env.Cv().to_video()
