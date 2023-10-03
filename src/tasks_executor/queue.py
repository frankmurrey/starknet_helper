from multiprocessing import Queue
from queue import Empty


def clear_queue(queue: Queue):
    try:
        while True:
            queue.get_nowait()
    except Empty:
        pass
