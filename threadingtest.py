import threading
import queue
import time
import msvcrt
import os
import logging

from environment.settings import GameSettings

if not os.path.isdir(GameSettings.log_path):
    os.makedirs(GameSettings.log_path)
log_file_path = os.path.join(GameSettings.log_path, 'threadtest.log')
if os.path.isfile(log_file_path):
    os.remove(log_file_path)
logging.basicConfig(
    filename=log_file_path,
    format='%(asctime)s %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    encoding='utf-8',
    level=logging.DEBUG)

"""NOTE
- Simple example of daemon threads stalling execution during a process.
- Daemon threads normally will exit if there are no more non-daemon threads,
    but daemon threads CANNOT exit while executing a process like time.sleep!!
- This means that, at least, if there is only ONE user thread,
    which can tell itself to exit before it starts listening for new user input,
    taking user input on a concurrent thread and having the thread terminate daemonically
    is possible :)
        - Even if there are more user threads (for some reason)
            more experimentation is required
"""

# def sleep_long():
#     time.sleep(5)

# def sleep_short():
#     time.sleep(1)

# long = threading.Thread(target=sleep_long, daemon=True)
# short = threading.Thread(target=sleep_short)
# start_time = time.perf_counter()
# long.start()
# short.start()
# long.join()
# short.join()
# end_time = time.perf_counter()
# print(f'done after: {end_time - start_time}')

"""NOTE
- Simple example of implementation of threading.Event's
- Threading event offers a basic, but safe way to communicate between threads
- In this example, press 'q' to exit both threads
"""

# def pr(e: threading.Event):
#     a = -1
#     while not e.is_set():
#         a += 1
#         print(f'hi x{a}')
#         # time.sleep(1)

# def get_in(e: threading.Event):
#     while not e.is_set():
#         new_in = msvcrt.getch()
#         logging.debug(f'"{new_in}" input detected')
#         if new_in == b'q':
#             logging.debug('"q" detected')
#             e.set()

# should_exit = threading.Event()
# logging.debug(f'"should_exit" event created -> {should_exit.is_set()}')
# print_thread = threading.Thread(target=pr, args=(should_exit,))
# in_thread = threading.Thread(target=get_in, args=(should_exit,))
# print_thread.start()
# in_thread.start()
# logging.debug(f'loops started')

"""NOTE
- More complex example using queues.
- Queues allow for safe, more complex (list), communication between threads.
"""
q = queue.Queue()

def worker():
    while True:
        item = q.get()
        logging.debug(f"working on {item}")
        item()
        logging.debug(f"finished work on {item}")
        q.task_done()

def print_hello():
    logging.debug('hello')

threading.Thread(target=worker, daemon=True).start()

for i in range(30):
    q.put(print_hello)
logging.debug(f'put all tasks')

q.join()
print('all tasks complete')
