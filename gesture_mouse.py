import cv2
import mediapipe as mp
import pyautogui
import time
import math

pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0

camera_width = 640
camera_height = 480

# Movement settings
sensitivity = 4.0
dead_zone = 3

# Left click settings
still_start_time = None
last_left_click_time = 0
left_click_hold_time = 0.6
left_click_cooldown = 1.0
still_threshold = 6

# Right click settings
right_click_start_time = None
last_right_click_time = 0
right_click_hold_time = 0.4
right_click_cooldown = 1.2
right_click_distance = 35

# Smoothing buffer
smooth_positions = []
smooth_window = 5

prev_finger_x = None
prev_finger_y = None

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.75,
    min_tracking_confidence=0.75
)
mp_draw = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cap.set(3, camera_width)
cap.set(4, camera_height)

while True:
    success, frame = cap.read()
    if not success:
        print("Failed to access webcam")
        break

    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)

    if results.multi_hand_landmarks:
        hand_landmarks = results.multi_hand_landmarks[0]
        mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

        index_tip = hand_landmarks.landmark[8]
        middle_tip = hand_landmarks.landmark[12]

        raw_x = int(index_tip.x * camera_width)
        raw_y = int(index_tip.y * camera_height)

        middle_x = int(middle_tip.x * camera_width)
        middle_y = int(middle_tip.y * camera_height)

        # Smooth index finger position
        smooth_positions.append((raw_x, raw_y))
        if len(smooth_positions) > smooth_window:
            smooth_positions.pop(0)

        index_x = int(sum(p[0] for p in smooth_positions) / len(smooth_positions))
        index_y = int(sum(p[1] for p in smooth_positions) / len(smooth_positions))

        cv2.circle(frame, (index_x, index_y), 12, (0, 255, 0), -1)
        cv2.circle(frame, (middle_x, middle_y), 10, (255, 0, 0), -1)
        cv2.line(frame, (index_x, index_y), (middle_x, middle_y), (0, 255, 255), 2)

        current_time = time.time()

        # Distance between index and middle fingers
        index_middle_distance = math.hypot(index_x - middle_x, index_y - middle_y)
        right_click_gesture = index_middle_distance < right_click_distance

        if prev_finger_x is not None and prev_finger_y is not None:
            dx = index_x - prev_finger_x
            dy = index_y - prev_finger_y
            movement_distance = math.hypot(dx, dy)

            # Move cursor only when not doing right-click gesture
            if not right_click_gesture:
                move_dx = dx if abs(dx) >= dead_zone else 0
                move_dy = dy if abs(dy) >= dead_zone else 0

                if move_dx != 0 or move_dy != 0:
                    mouse_x, mouse_y = pyautogui.position()
                    pyautogui.moveTo(
                        mouse_x + move_dx * sensitivity,
                        mouse_y + move_dy * sensitivity,
                        duration=0
                    )

            # RIGHT CLICK: index + middle close and held still
            if right_click_gesture:
                still_start_time = None  # prevent left click
                if right_click_start_time is None:
                    right_click_start_time = current_time

                held_time = current_time - right_click_start_time

                cv2.putText(
                    frame,
                    f"Right Hold: {held_time:.1f}s",
                    (20, 110),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (255, 0, 255),
                    2
                )

                if held_time >= right_click_hold_time and (current_time - last_right_click_time) > right_click_cooldown:
                    pyautogui.rightClick()
                    last_right_click_time = current_time
                    right_click_start_time = None

                    cv2.putText(
                        frame,
                        "RIGHT CLICK",
                        (20, 150),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1,
                        (255, 0, 255),
                        2
                    )

            else:
                right_click_start_time = None

                # LEFT CLICK: hold index still
                if movement_distance < still_threshold:
                    if still_start_time is None:
                        still_start_time = current_time

                    held_time = current_time - still_start_time

                    cv2.putText(
                        frame,
                        f"Left Hold: {held_time:.1f}s",
                        (20, 80),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        (0, 255, 255),
                        2
                    )

                    if held_time >= left_click_hold_time and (current_time - last_left_click_time) > left_click_cooldown:
                        pyautogui.click()
                        last_left_click_time = current_time
                        still_start_time = None

                        cv2.putText(
                            frame,
                            "LEFT CLICK",
                            (20, 120),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            1,
                            (0, 255, 0),
                            2
                        )
                else:
                    still_start_time = None

        prev_finger_x = index_x
        prev_finger_y = index_y

    else:
        prev_finger_x = None
        prev_finger_y = None
        still_start_time = None
        right_click_start_time = None
        smooth_positions.clear()

    cv2.putText(
        frame,
        "Index=Move | Hold=Left Click | Index+Middle Close=Right Click | ESC=Exit",
        (15, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.52,
        (0, 255, 255),
        2
    )

    small_frame = cv2.resize(frame, (480, 360))
    cv2.imshow("Gesture Mouse Controller", small_frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()   
cv2.destroyAllWindows()