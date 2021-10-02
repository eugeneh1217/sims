from __future__ import annotations
import numpy as np
import os
import shutil
import time
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
    @classmethod
    @property
    def size(cls):
        return tuple(os.get_terminal_size())

    @classmethod
    def clear(cls):
        os.system('cls' if os.name in ('nt', 'dos') else 'clear')

    @classmethod
    def convert(cls, int_array: np.ndarray):
        converted = np.array(int_array, dtype=object)
        converted[converted == 0] = ' '
        converted[converted == 1] = '-'
        converted[converted == 2] = '|'
        return converted

    @classmethod
    def draw_frame(cls, frame: np.ndarray):
        cls.clear()
        print_frame = '\n'.join([''.join(row) for row in frame])
        print(print_frame)

    @classmethod
    def draw_floor(cls):
        floor_height = cls.size[1] / 5
        floor = '-' * cls.size[0]
        print("\n" * cls.size)

if __name__ == '__main__':
    env = Environment(name="test")
    Cmd.clear()
    # print(Cmd.size)
    while True:
        time.sleep(0.001)
        Cmd.draw_blank()

