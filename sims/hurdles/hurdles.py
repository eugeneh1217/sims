from __future__ import annotations


import numpy as np

from sims import environment as env
from settings import Settings

class HurdleLoop:
    def __init__(self):
        super().__init__()
        self.ui = env.Cv(Settings.map_size, Settings.frame_save_path, Settings.video_out_path)
        self.writer = env.Headless(Settings.map_size, Settings.frame_save_path)
        self.gameobjects = {Ground.name: Ground(Settings.ground_height)}
        self.gameobjects[Hurdler.name] = [Hurdler(self.gameobjects['ground']), ]
        self.gameobjects[Hurdle.name] = [
            Hurdle(self.gameobjects['ground'], Settings.hurdle_spawn_x), ]
        self.frame_number = -1
        self.frame = self.writer.get_empty()

    def terminate(self):
        return self.frame_number == Settings.frames

    def remove_gameobject(self, gameobject):
        gameobjects_list = self.gameobjects[gameobject.name]
        gameobjects_list.remove(gameobject)

    def get_state(self) -> StatePacket:
        return StatePacket(self.frame_number)

    def run_gameobject(self, gameobject):
        state = self.get_state()
        gameobject.act(state)
        if gameobject.terminated:
            self.remove_gameobject(gameobject)
            print(f"terminated {gameobject.name}")
            return
        if isinstance(gameobject, Hurdler):
            if gameobject.check_hurdle_collisions(self.gameobjects[Hurdle.name]):
                gameobject.terminate()
        gameobject.draw(self.frame)

    def main(self):
        self.frame = self.writer.get_empty()
        for gameobject_type in self.gameobjects.values():
            if hasattr(gameobject_type, '__iter__'):
                for gameobject in gameobject_type:
                    self.run_gameobject(gameobject)
            else:
                self.run_gameobject(gameobject_type)
        self.frame_number += 1
        self.writer.draw(self.frame, self.get_state())

    def run(self):
        print('running hurdles...')
        while True:
            if self.terminate():
                print(f"HURDLES terminated at frame {self.frame_number}")
                break
            self.main()
        print('video processing...')
        self.ui.to_video(Settings.map_size, Settings.video_fps)
        print('video processing finished')

class StatePacket:
    def __init__(self, frame_number):
        self.frame_number = frame_number

# NOTE: Rectangular objects are centered at bottom left
class GameObject:
    terminated = False
    def __init__(self):
        self.displacement = 0
        self.velocity = 0
        self.acceleration = 0

    def terminate(self):
        self.terminated = True

    def top(self):
        return self.displacement[1] + self.height - 1

    def bottom(self):
        return self.displacement[1]

    def right(self):
        return self.displacement[0] + self.width - 1

    def left(self):
        return self.displacement[0]

    def draw(self, frame: np.ndarray):
        raise NotImplementedError()

class Hurdler(GameObject):
    color = 2
    name = 'hurdler'
    spawn_x = Settings.hurdler_x_spawn
    width = Settings.hurdler_width
    height = Settings.hurdler_height
    def __init__(self, ground):
        super().__init__()
        self.ground = ground
        self.displacement = np.array([self.spawn_x, self.ground.top()], np.float64)

    def isgrounded(self):
        return self.displacement[1] - self.ground.top() <= 0

    def jump(self):
        if self.isgrounded():
            print('jumped')
            self.velocity += np.array([0, Settings.hurdler_jump_speed], dtype=np.float64)

    def act(self, state: StatePacket):
        if state.frame_number % Settings.jump_interval == 0 and state.frame_number != 0:
            self.jump()
        self.move()

    def move(self):
        self.acceleration = 0
        if not self.isgrounded():
            self.acceleration = Settings.gravity
        self.velocity += self.acceleration
        self.displacement += self.velocity
        if self.isgrounded():
            self.displacement = np.array([self.displacement[0], self.ground.top()], dtype=np.float64)

    def hurdle_collision(self, hurdle: Hurdle):
        if hurdle.top() < self.bottom() or hurdle.bottom() > self.top() or hurdle.right() < self.left() or hurdle.left() > self.right():
                return False
        print('reason: ', hurdle.top() < self.bottom(), hurdle.bottom() > self.top(), hurdle.right() < self.left(), hurdle.left() > self.right())
        return True

    def check_hurdle_collisions(self, hurdles: list):
        for hurdle in hurdles:
            if self.hurdle_collision(hurdle):
                return True
        return False

    def draw(self, frame: np.ndarray):
        frame[
            int(self.displacement[0]): int(self.displacement[0]) + self.width,
            int(self.displacement[1]): int(self.displacement[1]) + self.height] = self.color

class Hurdle(GameObject):
    name = 'hurdle'
    color = 3
    width = Settings.hurdle_width
    height = Settings.hurdle_height
    def __init__(self, ground: Ground, spawn_x: int):
        super().__init__()
        self.spawn_x = spawn_x
        self.ground = ground
        self.displacement = np.array([self.spawn_x, self.ground.top()])

    def act(self, state: StatePacket):
        self.move()

    def move(self):
        self.displacement += Settings.hurdle_drift
        if self.displacement[0] < 0:
            self.displacement[0] = self.spawn_x

    def draw(self, frame: np.ndarray):
        frame[
            self.displacement[0]: self.displacement[0] + self.width,
            self.displacement[1]: self.displacement[1] + self.height] = self.color

class Ground(GameObject):
    name = 'ground'
    color = 1
    def __init__(self, ground_height):
        self.displacement = np.array([0, ground_height])

    def top(self):
        return self.displacement[1] + 1

    def act(self, state: StatePacket):
        pass

    def draw(self, frame: np.ndarray):
        frame[:, self.displacement[1]] = self.color

if __name__ == '__main__':
    hurdle = HurdleLoop()
    hurdle.run()
