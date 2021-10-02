import numpy as np

class GeneticSettings:
    REPRODUCTION_RATE = 0.1
    GROWTH_RATE = 0.1
    FLIP_RATE = 0.1
    CROSSOVER_RATE = 0.1

class HurdleSettings:
    REPLAY_FPS = 20
    LIVE_FPS = 10
    MIN_MAPSIZE = (500, 500)
    FLOOR_HEIGHT = 100
    MAP_SPEED = 10
    AGENT_SPAWN = np.array([200, FLOOR_HEIGHT + 1])
    GRAVITY = np.array([0, -10])