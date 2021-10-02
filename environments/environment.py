from __future__ import annotations
import msvcrt
import numpy as np
import os
import shutil
import time
import threading
import weakref

from hurdles.settings import HurdleSettings

"""TODO:
1. figure out basics of cmd visualization
2. figure out user input (threading)
    https://www.tutorialspoint.com/python/python_multithreading.htm
3. figure out how to visualize rectangles
4. figure out moving
5. figure out moving + physics
"""

class GameObject:
    last_goid = None

    @classmethod
    def incr_goid(cls):
        cls.last_goid += 1

    @classmethod
    def generate_goid(cls):
        return last_goid + 1

    def __init__(self,
                 position: np.ndarray,
                 environment: Environment,
                 mass: float,
                 active=True,
                 gravity=True):
        # if goid in GameObject.object_list.keys():
        #     raise ValueError(f"Object with id {goid} already exists")
        self.goid = self.generate_goid()
        self.environment = environment
        self.incr_goid()
        self.mass = mass
        self.position = position
        self.velocity = np.zeros(2)
        self.acceleration = np.zeros(2)
        self.forces = {}
        self.active = active
        self.gravity = gravity

    def recieve_force(self, other: "GameObject", delta: np.ndarray):
        if other.goid in self.forces.keys():
            self.forces[other.goid] += delta
        self.forces[weakref.ref(other)] = delta

    def apply_force(self, other: "GameObject", delta: np.ndarray):
        other.recieve_force(delta, self)

    def move(self):
        final_acceleration = np.array(self.acceleration)
        final_velocity = np.array(self.velocity)
        final_position = np.array(self.position)
        if self.gravity is True and not self.grounded():
            final_acceleration -= HurdleSettings.GRAVITY
        self.acceleration += sum(self.forces.values()) / self.mass
        if self.grounded() and self.acceleration[1] < 0:
            self.acceleration[1] = 0
        final_velocity += self.acceleration
        final_position += final_velocity

    def grounded(self):
        raise NotImplementedError()

    def intersects(self, other: "GameObject"):
        raise NotImplementedError()

    def act():
        raise NotImplementedError()

class RectangleGameObject(GameObject):
    def __init__(self, position: np.ndarray, height: int, width: int):
        super().__init__(position) # position is bottom left of agent
        self.height = height
        self.width = width

    @property
    def bottom(self):
        return self.position[1]

    @property
    def top(self):
        return self.position[1] + self.height

    @property
    def left(self):
        return self.position[0]

    @property
    def right(self):
        return self.position[0] + self.width

    def intersects(self, other: "GameObject"):
        if isinstance(other, RectangleGameObject):
            if ((self.right < other.left or self.left > other.right) and
                (self.top < other.bottom or self.bottom > other.top)):
                return False
            return True
        raise NotImplementedError()

    def grounded(self):
        return self.bottom - 1 <= HurdleSettings.FLOOR_HEIGHT

class Agent(RectangleGameObject):
    def __init__(self, position):
        super().__init__(position)

    def act():
        pass


class Hurdle(RectangleGameObject):
    def __init__(self, position):
        super().__init__(position)

class Environment:
    def __init__(self, name: str=None):
        self.name = name
        self.gameobjects = {}
        self.agents = {}
        self.hurdles = {}
        self.frame = 0
        self.mapsize = (0, 0)

    def add(self, gameobject):
        if not isinstance(gameobject, GameObject):
            raise ValueError(
                f"attemped to add non-GameObject to {self.name} environment")
        if gameobject.goid in self.gameobjects.keys():
            raise ValueError(
                f"GameObject {gameobject.goid} "
                f"already exists in {self.name} environment")
        self.gameobject.append(weakref.ref(gameobject))
        if isinstance(gameobject, Hurdle):
            self.hurdles[gameobject.goid] = (weakref.ref(gameobject))
        if isinstance(gameobject, Agent):
            self.agents[gameobject.goid] = (weakref.ref(gameobject))

    def step(self):
        """Step simulation one frame forward
            Order of action:
                - move screen back
                - apply gravity

        """
        # for gameobject in GameObject.object_list:
        #     self.position -= HurdleSettings.MAP_SPEED
        
        # for agent in self.agents:
        #     agent.move()
        #     agent.acceleartion += 9.8
        # frame += 1

    def draw(self):
        pass

class Cmd:
    """Command Line GUI
        Everything is scaled by height
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
            for row in self.convert(frame).T]))

    def get_empty(self, default=0):
        return np.zeros(self.size) + default

    # @classmethod
    # def draw_floor(self):
    #     floor_height = self.size[1] / 5
    #     floor = '-' * self.size[0]
    #     print("\n" * self.size)
"""NOTE:
- when creating a loop:
    - add to Loop.loops
    - self.ran = False

- every frame:
    - if all loops in step have run, increment step
    - every loop:
        - if step is my step, run & attempt step ++ & self.ran = True

- every step reset:
    - if reset:
        step = 0
        all objects: self.ran = False
"""
class Loop:
    step = 0
    uerin = None
    _loops = {}
    def __init__(self, ui=None):
        self.ran = False
        self.ui = ui
        self.add(self)

    @classmethod
    def add(cls, new):
        cls._loops.append(weakref.ref(new))

    @classmethod
    def step(cls):
        cls.step += 1
        if cls.step == len(cls.loops):
            cls.step = 0

    def run(self):
        raise NotImplementedError()

class UserLoop(Loop):
    def run(self):
        global userin
        userin = msvcrt.getch()
        super().step()

class GameLoop(Loop):
    def run(self):
        global userin
        while True:
            if userin == 'q':
                break
            if self.ui is not None:
                time.sleep(1 / HurdleSettings.LIVE_FPS)
                frame = self.ui.get_empty(default=1)
                frame[:10, :10] = 2
                self.ui.draw(frame)

if __name__ == '__main__':
    # env = Environment(name="test")
    gameloop = GameLoop(ui=Cmd())
    userloop = UserLoop()
    userthread = threading.Thread(target=userloop.run)
    gameloop = threading.Thread(target=gameloop.run)
    userthread.start()
    gameloop.start()