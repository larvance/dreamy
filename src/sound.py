import queue
import threading
from time import time, sleep
from typing import Dict, Tuple, List, Optional

import pyo

from src.utils import excite_string, cleanup_plucked, modulate_running_frequencies

update_queue: queue.Queue = queue.Queue()

last = time()
s = pyo.Server()


def sound_worker():
    s = pyo.Server().boot().start()
    last = time()
    plucked: Dict[float, Tuple[List[pyo.Adsr], pyo.Freeverb, Optional[pyo.FreqShift], Optional[pyo.Sine]]] = {}
    last_trigger_time: Dict[float, float] = {}

    positions = []
    while True:
        updates = False
        try:
            while True:
                positions = update_queue.get_nowait()
                updates = True
        except queue.Empty:
            pass
        if positions is None:
            break

        for x, y in positions:
            if x < 0 or x > 1 or y < 0 or y > 1:
                continue
            held_time = time() - last
            brightness = min(0.2, 0.03 + held_time * 0.05) * (1.0 - y) * 4
            excite_string(plucked, last_trigger_time, x, brightness=brightness)
            if updates:
                modulate_running_frequencies(plucked, x)  # might cause problems if more than one hand is used

        last = time()
        cleanup_plucked(plucked, last_trigger_time)

        sleep(0.1)

    s.stop()
    plucked.clear()
    last_trigger_time.clear()


worker_thread: threading.Thread


def enable_sound():
    global worker_thread
    worker_thread = threading.Thread(target=sound_worker, daemon=True)
    worker_thread.start()


def give_string_input(positions: List[Tuple[float, float]]):
    update_queue.put(positions)


def disable_sound():
    update_queue.put(None)
    worker_thread.join()
