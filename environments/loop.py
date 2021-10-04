from __future__ import annotations
import logging
import msvcrt
import os
import shutil
import time
import threading

from environments import gui
from environments.settings import GameSettings
from environments import uid

if not os.path.isdir(GameSettings.log_path):
    os.makedirs(GameSettings.log_path)
logging.basicConfig(
    filename=os.path.join(GameSettings.log_path, 'loop.log'),
    format='%(asctime)s %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    encoding='utf-8',
    level=logging.DEBUG)

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

NOTE: Potential solution: if waiting for user in,
    create another thread to proceed "step"

TODO: Ensure that only one key is captured per frame (i.e. synchronize threads)
        if want to let the user play
"""
class Loop:
    # step = 0
    uids = uid.UidSystem()
    QUIT_KEY = b'q'
    def __init__(self):
        self.uids.create(self)
        self.lock = threading.Lock()
        self.ran = False

    # @classmethod
    # def step_forward(cls):
    #     logging.debug(f'moving from step {cls.step}')
    #     cls.step += 1
    #     if cls.step == len(cls.uids.get_uids()):
    #         cls.step = 0

    def frame(self):
        raise NotImplementedError()

    def check_quit(self):
        raise NotImplementedError()

    def run(self):
        should_break = False
        logging.debug(f'{self.__class__.__name__} thread started')
        while True:
            logging.debug(f'{self.__class__.__name__} loop running')
            # if self.frame_step == Loop.step:
            self.frame()
            # self.lock.acquire()
            if self.check_quit():
                logging.debug(f'"should break" detected {self.__class__.__name__}')
                should_break = True
            # Loop.step_forward()
            # self.lock.release()
            # if should_break:
            #     logging.debug(f'breaking {self.__class__.__name__}')
            #     break
        logging.debug(f'{self.__class__.__name__} thread killed')

class UserLoop(Loop):
    userin = None
    frame_step = 0

    def __init__(self):
        super().__init__()

    @classmethod
    def update_userin(cls, new):
        cls.userin = new

    def check_quit(self):
        return self.userin == self.QUIT_KEY

    def frame(self):
        new_userin = msvcrt.getch()
        self.update_userin(new_userin)

class GameLoop(Loop):
    frame_step = 1
    def __init__(self, userloop: UserLoop, ui=None):
        super().__init__()
        self.user = userloop
        self.ui = ui

    def check_quit(self):
        return self.user.userin == self.QUIT_KEY

    def frame(self):
        if self.ui is not None:
            time.sleep(1 / GameSettings.live_fps)
            frame = self.ui.get_empty(default=1)
            frame[:10, :10] = 2
            self.ui.draw(frame)

if __name__ == '__main__':
    # env = Environment(name="test")
    userloop = UserLoop()
    gameloop = GameLoop(userloop, ui=gui.Cmd())
    userthread = threading.Thread(target=userloop.run, daemon=True)
    gamethread = threading.Thread(target=gameloop.run)
    userthread.start()
    gamethread.start()
    userthread.join()
    gamethread.join()
    print('loop quit normally')

