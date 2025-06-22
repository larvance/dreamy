import math
import time

import cv2
import mediapipe as mp

from src.sound import enable_sound, give_string_input, disable_sound
from src.utils import notes_x

mp_hands = mp.solutions.hands
mp_face_mesh = mp.solutions.face_mesh
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1)
face_mesh = mp_face_mesh.FaceMesh(static_image_mode=False, max_num_faces=1)
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

cap = cv2.VideoCapture(0)

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

        results_hands = hands.process(rgb)
        results_face = face_mesh.process(rgb)

        black_bg = 0 * frame

        for face_landmarks in results_face.multi_face_landmarks or ():
            mp_drawing.draw_landmarks(
                black_bg,
                face_landmarks,
                mp_face_mesh.FACEMESH_TESSELATION,
                landmark_drawing_spec=mp_drawing.DrawingSpec(color=(255, 255, 255), thickness=1, circle_radius=0),
                connection_drawing_spec=mp_drawing.DrawingSpec(color=(255, 255, 255), thickness=1, circle_radius=0)
            )

        positions = []
        for hand_landmarks in results_hands.multi_hand_landmarks or ():
            mp_drawing.draw_landmarks(
                black_bg,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS,
                mp_drawing_styles.get_default_hand_landmarks_style(),
                mp_drawing_styles.get_default_hand_connections_style()
            )
            index = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
            x, y, z = index.x, index.y, index.z
            x = (x - 0.1) / 0.8
            y = (y - 0.1) / 0.8
            if x < 0 or x > 1 or y < 0 or y > 1:
                continue
            cv2.circle(black_bg, (int(index.x * black_bg.shape[1]), int(index.y * black_bg.shape[0])), 10, (0, 255, 0),
                       -1)
            positions.append((x, y))
            note_x = min(notes_x, key=lambda note: abs(note - x))
            line_x = note_x * 0.8 + 0.1
            width = int(line_x * black_bg.shape[1])
            dist = abs(line_x - x)
            offset = int(
                vibration_amplitude * math.sin(20 * (time.time() - start_time) * (vibration_threshold - dist) * 20))
            cv2.line(black_bg, (width + offset, 0), (width + offset, black_bg.shape[0]), (255, 255, 255))

        give_string_input(positions)

        for note_x in notes_x + [0]:
            line_x = note_x * 0.8 + 0.1
            width = int(line_x * black_bg.shape[1])
            cv2.line(black_bg, (width, 0), (width, black_bg.shape[0]), (255, 255, 255))

        cv2.imshow("Dreamy Hand-Powered", black_bg)
        if cv2.waitKey(1) & 0xFF == 27:
            break

    disable_sound()
