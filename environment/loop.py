from __future__ import annotations
import logging
import msvcrt
import os
import shutil
import time
import threading
import queue

from environment import gui
from environment.settings import GameSettings
from environment import uid

if not os.path.isdir(GameSettings.log_path):
    os.makedirs(GameSettings.log_path)
logging.basicConfig(
    filename=os.path.join(GameSettings.log_path, 'loop.log'),
    format='%(asctime)s %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    encoding='utf-8',
    level=logging.DEBUG)

class Loop:
    QUIT_SYMBOL = b'q'

    def __init__(self, listen_userin: bool=True):
        self._userin = None
        self.userin_queue = queue.Queue()
        self.threads = [
            threading.Thread(target=self.main, daemon=False),
            threading.Thread(target=self.user_queue_worker, daemon=True)]
        if listen_userin:
            self.threads.append(threading.Thread(target=self.listen_userin, daemon=True))

    # raw access to _userin ok because
    # userin checked very often by non listening threads
    @property
    def userin(self):
        return self._userin

    def _update_userin(self, new):
        self._userin = new

    @userin.setter
    def userin(self, new):
        return self.userin_queue.put((self._update_userin, new))

    def user_queue_worker(self):
        while True:
            if self.check_quit():
                break
            task = self.userin_queue.get()
            if hasattr(task, '__iter__'):
                task[0](*task[1:])
            else:
                task()
            self.userin_queue.task_done()

    def check_quit(self):
        return self.userin == QUIT_SYMBOL

    def run(self, join=True):
        for thread in self.threads:
            thread.start()
        if join:
            for thread in self.threads:
                thread.join()

    def listen_userin(self):
        while True:
            if self.check_quit():
                break
            self.userin = msvcrt.getch()

    def main(self):
        while True:
            if self.check_quit():
                break

if __name__ == '__main__':
    pass
