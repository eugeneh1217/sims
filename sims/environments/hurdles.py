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
        # TODO: decouple ui from simulation
        self.ui = vis.Cv(Settings.map_shape, Settings.video_out_path)

    def all_gameobjects(self):
        return [go for gos in self.gameobjects.values() for go in gos]

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
                gameobject.terminate(self.get_state())
        if gameobject.terminated:
            self.remove_gameobject(gameobject)
            print(f"terminated {gameobject.object_name} @ frame {self.frame_number}")
            return

    def run_hurdles(self):
        for hurdle in self.gameobjects[Hurdle.name]:
            self.run_gameobject(hurdle)

    def run_hurdlers(self):
        for hurdler in self.gameobjects[Hurdler.name]:
            self.run_gameobject(hurdler)

    def run_gameobjects(self):
        self.run_hurdlers()
        self.run_hurdles()

    def draw(self):
        frame = self.ui.get_empty()
        for gameobject in self.all_gameobjects():
            frame = gameobject.draw(frame)
        self.frames.append(frame)

    def main(self):
        self.run_gameobjects()
        self.frame_number += 1
        self.draw()

    def run(self, to_video: bool):
        """Runs Hurdles simulation until termination condition. In loop:
            1. Checks for simulation termination
            2. runs main
        """
        print(f'running HURDLES with {len(self.gameobjects[Hurdler.name])} hurdlers...')
        self.frame_number = 0
        while True:
            if self.terminate():
                print(f"HURDLES terminated at frame {self.frame_number}")
                for gameobject in self.all_gameobjects():
                    gameobject.terminate(self.get_state())
                break
            self.main()
        if to_video:
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
    name = None
    terminated = False

    def __init__(self, object_name: str=None):
        self.termination_state = None
        self.displacement = 0
        self.velocity = 0
        self.acceleration = 0
        self.object_name = object_name or 'GameObject'

    @classmethod
    @property
    def name(self):
        return self.__class__.name

    def terminate(self, state: StatePacket):
        self.terminated = True
        self.termination_state = state

class Square(GameObject):
    width = 0
    height = 0

    def __init__(self, object_name: str=None):
        super().__init__(object_name=object_name or 'SquareGameObject')

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
    def __init__(self, history: list=None, object_name: str=None):
        super().__init__(object_name=object_name or 'Hurdler')
        self.history = history or []
        self.displacement = np.array([self.spawn_x, 0], np.float64)

    def isgrounded(self):
        return self.displacement[1] <= 0

    def jump(self):
        if self.isgrounded():
            print(f'{self.object_name} jumped')
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
    def __init__(self, period: int, history: list=None, object_name: str=None):
        super().__init__(history=history, object_name=object_name or 'ConstantHurdler')
        self.period = period

    def act(self, state: StatePacket):
        action = None
        if state.frame_number % self.period == 0 and state.frame_number != 0:
            self.jump()
            action = 'j'
        self.move()
        self.history.append(action)

class ProximityHurdler(Hurdler):
    def __init__(self, threshold: int, history: list=None, object_name: str=None):
        super().__init__(history=history, object_name=object_name or 'ProximityHurdler')
        self.threshold = threshold

    def proximity(self, hurdle: Hurdle):
        return hurdle.displacement[0] - self.displacement[0]

    def closest_hurdle(self, hurdles: list[Hurdle]):
        closest = hurdles[0]
        for hurdle in hurdles:
            if self.proximity(hurdle) < self.proximity(closest):
                closest = hurdle
        return hurdle, self.proximity(closest)
    
    def act(self, state: StatePacket):
        action = None
        _, prox = self.closest_hurdle(state.hurdlers)
        if prox < self.threshold:
            self.jump()
            action = 'j'
        self.move()
        self.history.append(action)

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
    hurdlers = [
        ProximityHurdler(100),
        ]
    hurdle = Simulation(hurdlers=hurdlers, hurdles=[Hurdle()])
    hurdle.run()
