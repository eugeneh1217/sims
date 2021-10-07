import time

from environment import loop, gui

class HurdleLoop(loop.Loop):
    def __init__(self, fps=30):
        super().__init__()
        self.ui = gui.Cmd()
        self.fps = fps

    @loop.Loop.loop
    def main(self):
        time.sleep(1 / self.fps)
        self.ui.clear()
        self.ui.draw(self.ui.get_empty(default=1))

if __name__ == '__main__':
    hurdle = HurdleLoop()
    hurdle.run()