import cv2
import mediapipe as mp

from src.sound import enable_sound, give_string_input, disable_sound
from src.utils import notes_x

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1)
mp_drawing = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)

import math
import time

vibration_amplitude = 5
vibration_threshold = 0.05

start_time = time.time()

def main():
    enable_sound()
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb)

        positions = []
        hand_list = results.multi_hand_landmarks or ()
        for hand in hand_list:
            mp_drawing.draw_landmarks(frame, hand, mp_hands.HAND_CONNECTIONS)
            index = hand.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
            x, y, z = index.x, index.y, index.z
            x = (x - 0.1) / 0.8
            y = (y - 0.1) / 0.8
            if x < 0 or x > 1 or y < 0 or y > 1:
                continue
            cv2.circle(frame, (int(index.x * frame.shape[1]), int(index.y * frame.shape[0])), 10, (0, 255, 0), -1)
            positions.append((x, y))
            note_x = min(notes_x, key=lambda note: abs(note - x))
            line_x = note_x * 0.8 + 0.1
            px = int(line_x * frame.shape[1])
            dist = abs(line_x - x)
            offset = int(
                vibration_amplitude * math.sin(20 * (time.time() - start_time) * (vibration_threshold - dist) * 20))
            cv2.line(frame, (px + offset, 0), (px + offset, frame.shape[0]), (255, 255, 255))

        give_string_input(positions)

        for note_x in notes_x + [0]:
            line_x = note_x * 0.8 + 0.1
            px = int(line_x * frame.shape[1])
            cv2.line(frame, (px, 0), (px, frame.shape[0]), (255, 255, 255))

        cv2.imshow("Dreamy Hand-Powered", frame)
        if cv2.waitKey(1) & 0xFF == 27:
            break

    disable_sound()
