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

shutil.rmtree(GameSettings.log_path)
os.makedirs(GameSettings.log_path)
logging.basicConfig(
    filename=os.path.join(GameSettings.log_path, 'loop.log'),
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
"""
class Loop:
    step = 0
    uids = uid.UidSystem()
    QUIT_KEY = b'q'
    def __init__(self):
        self.uids.create(self)
        self.lock = threading.Lock()
        self.ran = False

    @classmethod
    def step_forward(cls):
        cls.step += 1
        if cls.step == len(cls.uids.get_uids()):
            cls.step = 0

    def frame(self):
        raise NotImplementedError()

    def check_quit(self):
        raise NotImplementedError()

    def run(self):
        should_break = False
        logging.debug(f'{self.__class__.__name__} thread started')
        while True:
            logging.debug(f'{self.__class__.__name__} loop running')
            if self.frame_step == Loop.step:
                logging.debug(
                    f'{self.__class__.__name__} acquiring "check quit"'
                )
                self.lock.acquire()
                logging.debug(
                    f'"check quit" lock acquired by '
                    f'{self.__class__.__name__}')
                if self.check_quit():
                    should_break = True
                    logging.debug(
                        f'"should_break" detected '
                        f'in {self.__class__.__name__}')
                self.lock.release()
                logging.debug(
                    f'"check quit" lock released by '
                    f'{self.__class__.__name__}')
                if should_break:
                    logging.debug(f'{self.__class__.__name__} breaking')
                    break
                self.frame()
                self.lock.acquire()
                logging.debug(
                    f'"step forward" lock '
                    f'acquired by {self.__class__.__name__}')
                Loop.step_forward()
                self.lock.release()
                logging.debug(
                    f'"step forward" lock '
                    f'released by {self.__class__.__name__}')
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
        self.lock.acquire()
        logging.debug('"userin" lock acquired by UserLoop')
        self.update_userin(new_userin)
        self.lock.release()
        logging.debug('"userin" lock released by UserLoop')

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
    userthread = threading.Thread(target=userloop.run)
    gamethread = threading.Thread(target=gameloop.run)
    userthread.start()
    gamethread.start()
    userthread.join()
    gamethread.join()
    print('loop quit normally')

