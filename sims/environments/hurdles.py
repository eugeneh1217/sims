from __future__ import annotations

import numpy as np

from settings import Settings
import sims.visualize as vis

class Simulation:
    def __init__(self, hurdlers: list[Hurdler], hurdles: list[Hurdle]):
        self.frame_number = 0
        self.gameobjects = {}
        self.gameobjects[Hurdler.name] = hurdlers
        self.gameobjects[Hurdle.name] = hurdles
        self.frames = []
        self.ui = vis.Cv(Settings.map_shape, Settings.video_out_path)

    def terminate(self) -> int:
        return self.frame_number == Settings.frames

    def remove_gameobject(self, gameobject):
        gameobjects_list = self.gameobjects[gameobject.name]
        gameobjects_list.remove(gameobject)

    def get_state(self) -> StatePacket:
        return StatePacket(self.frame_number, self.gameobjects[Hurdle.name], self.gameobjects[Hurdler.name])

    def run_gameobject(self, gameobject: GameObject):
        """Run gameobject.
            1. Calls gameobject's act function with state.
            2. Checks for Hurdler to Hrudle collsisions
            3. Terminates if terminated

        Args:
            gameobject (GameObject): gameobject
        """
        state = self.get_state()
        gameobject.act(state)
        if isinstance(gameobject, Hurdler):
            if gameobject.check_hurdle_collisions(self.gameobjects[Hurdle.name]):
                gameobject.terminate()
        if gameobject.terminated:
            self.remove_gameobject(gameobject)
            print(f"terminated {gameobject.__class__.name} @ frame {self.frame_number}")
            return

    def run_hurdles(self):
        for hurdle in self.gameobjects[Hurdle.name]:
            self.run_gameobject(hurdle)

    def run_hurdlers(self):
        actions = []
        for hurdler in self.gameobjects[Hurdler.name]:
            actions.append(self.run_gameobject(hurdler))
        return actions

    def run_gameobjects(self):
        self.run_hurdlers()
        self.run_hurdles()

    def draw(self):
        frame = self.ui.get_empty()
        for gameobject in [go for gos in self.gameobjects.values() for go in gos]:
            frame = gameobject.draw(frame)
        self.frames.append(frame)

    def main(self):
        self.run_gameobjects()
        self.frame_number += 1
        self.draw()

    def run(self):
        """Runs Hurdles simulation until termination condition. In loop:
            1. Checks for simulation termination
            2. runs main
        """
        print('running HURDLES...')
        while True:
            if self.terminate():
                print(f"HURDLES terminated at frame {self.frame_number}")
                break
            self.main()
        print('video processing...')
        self.ui.to_video(self.frames, Settings.video_fps)
        print('video processing finished')

class StatePacket:
    def __init__(self, frame_number: int, hurdlers: list[Hurdler], hurdles: list[Hurdle]):
        self.frame_number = frame_number
        self.hurdlers = hurdlers
        self.hurdles = hurdles

# NOTE: Rectangular objects are centered at bottom left
class GameObject:
    name = NotImplemented
    terminated = False

    def __init__(self):
        self.displacement = 0
        self.velocity = 0
        self.acceleration = 0

    @classmethod
    @property
    def name(self):
        return self.__class__.name

    def terminate(self):
        self.terminated = True

class Square(GameObject):
    width = 0
    height = 0

    def top(self):
        return self.displacement[1] + self.height - 1

    def bottom(self):
        return self.displacement[1]

    def right(self):
        return self.displacement[0] + self.width - 1

    def left(self):
        return self.displacement[0]

    def collision(self, other: Square):
        if (
            (other.top() < self.bottom())
            or (other.bottom() > self.top())
            or (other.right() < self.left())
            or (other.left() > self.right())):
                return False
        return True

class Hurdler(Square):
    name = 'Hurdler'
    color = 2
    spawn_x = Settings.hurdler_x_spawn
    width = Settings.hurdler_width
    height = Settings.hurdler_height
    def __init__(self):
        super().__init__()
        self.displacement = np.array([self.spawn_x, 0], np.float64)

    def isgrounded(self):
        return self.displacement[1] <= 0

    def jump(self):
        if self.isgrounded():
            print('jumped')
            self.velocity += np.array([0, Settings.hurdler_jump_speed], dtype=np.float64)

    def act(self, state: StatePacket):
        raise NotImplementedError()

    def move(self):
        self.acceleration = 0
        if not self.isgrounded():
            self.acceleration = Settings.gravity
        self.velocity += self.acceleration
        self.displacement += self.velocity
        if self.isgrounded():
            self.displacement = np.array([self.displacement[0], 0], dtype=np.float64)

    def check_hurdle_collisions(self, hurdles: list[Hurdle]):
        for hurdle in hurdles:
            if self.collision(hurdle):
                return True
        return False

    def draw(self, frame: np.ndarray) -> np.ndarray:
        frame_copy = np.array(frame)
        frame_copy[
            int(self.displacement[0]): int(self.displacement[0]) + self.width,
            int(self.displacement[1]): int(self.displacement[1]) + self.height] = self.color
        return frame_copy

class ConstantHurdler(Hurdler):
    def __init__(self, period):
        super().__init__()
        self.period = period

    def act(self, state: StatePacket):
        action = None
        if state.frame_number % self.period == 0 and state.frame_number != 0:
            self.jump()
            action = 'j'
        self.move()
        return action

class Hurdle(Square):
    name = 'Hurdle'
    color = 3
    width = Settings.hurdle_width
    height = Settings.hurdle_height
    spawn_x = Settings.hurdle_spawn_x
    def __init__(self):
        super().__init__()
        self.displacement = np.array([self.spawn_x, 0])

    def act(self, state: StatePacket):
        self.move()

    def move(self):
        self.displacement += Settings.hurdle_drift
        if self.displacement[0] < 0:
            self.displacement[0] = self.spawn_x

    def draw(self, frame: np.ndarray) -> np.ndarray:
        frame_copy = np.array(frame)
        frame_copy[
            self.displacement[0]: self.displacement[0] + self.width,
            self.displacement[1]: self.displacement[1] + self.height] = self.color
        return frame_copy

if __name__ == '__main__':
    constant_hurdlers = [
        ConstantHurdler(10),
        ConstantHurdler(20),
        ConstantHurdler(25),
        ConstantHurdler(30),
        ConstantHurdler(40),
        ConstantHurdler(50),
        ]
    hurdle = Simulation(hurdlers=constant_hurdlers, hurdles=[Hurdle()])
    hurdle.run()
