import time
import unittest
from unittest import mock
import threading

from environment import loop

class MockLoop(loop.Loop):
    def __init__(self, listen_userin: bool=True):
        super().__init__(listen_userin=listen_userin)
        self.threads.append(threading.Thread(target=self.last))

    def check_quit(self):
        result = self.userin == "LAST"
        return result

    def last(self):
        self.userin = "LAST"

    def main(self):
        self.userin = "FIRST"
        time.sleep(1)

class TestLoop(unittest.TestCase):
    def setUp(self):
        self.loop = MockLoop(listen_userin=False)

    def test_user_queue_worker_set_in_order(self):
        self.loop.run()
        self.assertEqual(self.loop.userin, 'LAST')

    @mock.patch('environment.loop.msvcrt.getch')
    def test_listen_userin_quit(self, mock_getch):
        mock_getch.return_value = b'q'
        self.loop = loop.Loop()

if __name__ == '__main__':
    unittest.main()