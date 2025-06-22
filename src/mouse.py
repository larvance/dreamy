import threading
from multiprocessing import Queue, Process
from time import sleep

import pygame

from src.sound import disable_sound, enable_sound, give_string_input
from src.utils import notes_x


class MouseState:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.is_down = False
        self.on = False


mouse_state = MouseState()
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 400


def _pygame_process(caption, queue):
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(caption)
    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        _mx, _my = pygame.mouse.get_pos()
        is_down = pygame.mouse.get_pressed()[0]
        mx = min(SCREEN_WIDTH, max(0, _mx))
        my = min(SCREEN_HEIGHT, max(0, _my))

        queue.put({
            "x": mx,
            "y": my,
            "is_down": is_down
        })

        screen.fill((0, 0, 0))

        for x in notes_x:
            pygame.draw.line(screen, (255, 255, 255), (int(x * SCREEN_WIDTH), 0),
                             (int(x * SCREEN_WIDTH), SCREEN_HEIGHT))

        pygame.draw.circle(screen, (255, 0, 0) if is_down else (0, 255, 0), (mx, my), 10)
        pygame.display.flip()
        clock.tick(60)

    queue.put({"on": False})
    pygame.quit()


def _update_mouse_state(queue):
    while True:
        while not queue.empty():
            data = queue.get()
            for x in data:
                setattr(mouse_state, x, data[x])
        sleep(0.01)


def enable_mouse(caption=""):
    if mouse_state.on:
        return
    mouse_state.on = True

    queue = Queue()
    proc = Process(target=_pygame_process, args=(caption, queue), daemon=True)
    proc.start()

    thread = threading.Thread(target=_update_mouse_state, args=(queue,), daemon=True)
    thread.start()


def disable_mouse():
    pygame.quit()


def main():
    enable_mouse("Dreamy Mouse-Powered")
    enable_sound()

    while mouse_state.on:
        x = mouse_state.x / SCREEN_WIDTH
        y = mouse_state.y / SCREEN_HEIGHT
        if 0 <= x <= 1 and 0 <= y <= 1 and mouse_state.is_down:
            give_string_input([(x, y)])
        else:
            give_string_input([])

        sleep(0.001)

    disable_sound()
    disable_mouse()
