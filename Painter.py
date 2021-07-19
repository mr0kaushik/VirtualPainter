import cv2
import time
import numpy as np

import module.HandTrackingModule as htm
import module.PainterMenu as PM
import math

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
#####
c1 = (206, 242, 116)
c2 = (85, 191, 32)
c3 = (203, 255, 124)
c4 = (54, 0, 56)
c5 = (186, 186, 12)
c6 = (0, 78, 255)
c7 = (220, 153, 232)

green = (164, 245, 66)
red = (66, 66, 245)
yellow = (66, 242, 245)
blue = (245, 176, 66)
purple = (245, 66, 78)

cap = cv2.VideoCapture(0)
cap.set(3, SCREEN_WIDTH)
cap.set(4, SCREEN_HEIGHT)

menu_items = [
    ('Brush', 'assets/brush.png', PM.MenuMode.paint),
    ('Thickness', 'assets/thickness.png', PM.MenuMode.thickness),
    ('Color', 'assets/palette.png', PM.MenuMode.color),
    ('Eraser', 'assets/eraser.png', PM.MenuMode.eraser),
    ('Hand', 'assets/hand.png', PM.MenuMode.hand)
]

menu = PM.Menu(cv2, menu_items, width=SCREEN_WIDTH, height=SCREEN_HEIGHT)

p_time = 0

hand_detector = htm.HandDetector(min_detection_confidence=0.8)

PRIMARY_HAND_ID = 0
SECONDARY_HAND_ID = 1
THUMB_TIP = 4
INDEX_TIP = 8
MIDDLE_TIP = 12
RING_TIP = 16

ERASER_THICKNESS = 20

MIN_OPTIMAL_THICKNESS = 15
MAX_OPTIMAL_THICKNESS = 150

MAX_BRUSH_THICKNESS = 40
MIN_BRUSH_THICKNESS = 1
DEFAULT_BRUSH_THICKNESS = 15

current_brush_thickness = DEFAULT_BRUSH_THICKNESS

xp, yp = -1, -1

img_canvas = np.zeros((SCREEN_HEIGHT, SCREEN_WIDTH, 3), np.uint8)

while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)

    drawing_color = c7
    erase_color = (0, 0, 0)

    # draw menu
    menu.draw(cv2, img)
    selected_menu_item = menu.current_item

    # 0. Find Hand Landmarks
    img, positions = hand_detector.find_hand(img)
    # print("imgshape", img.shape)
    # print("canvasshape", img_canvas.shape)

    if len(positions) > 0:
        primary_hand = positions[PRIMARY_HAND_ID]

        thumb_x, thumb_y = primary_hand[THUMB_TIP][1:]
        index_finger_x, index_finger_y = primary_hand[INDEX_TIP][1:]
        middle_finger_x, middle_finger_y = primary_hand[MIDDLE_TIP][1:]
        ring_finger_x, ring_finger_y = primary_hand[RING_TIP][1:]

        # 1. drawing mode : index finger is up
        up_fingers = hand_detector.fingers_state()

        if len(up_fingers) == 5 and ~up_fingers[4]:

            if selected_menu_item.mode == PM.MenuMode.thickness:
                cx, cy = (thumb_x + index_finger_x) // 2, (thumb_y + index_finger_y) // 2

                cv2.line(img, (thumb_x, thumb_y), (index_finger_x, index_finger_y), purple, 2)

                cv2.circle(img, (thumb_x, thumb_y), 5, red, cv2.FILLED)
                cv2.circle(img, (index_finger_x, index_finger_y), 5, red, cv2.FILLED)

                length = math.hypot(index_finger_x - thumb_x, index_finger_y - thumb_y)

                cv2.circle(img, (cx, cy), 5, yellow if length > 50 else blue, cv2.FILLED)

                if len(positions) == 2:
                    up_fingers_secondary = hand_detector.fingers_state(hand_id=1)
                    if up_fingers_secondary[1] and up_fingers_secondary[2] and ~up_fingers_secondary[3]:
                        thickness = np.interp(length, [MIN_OPTIMAL_THICKNESS, MAX_OPTIMAL_THICKNESS],
                                              [MIN_BRUSH_THICKNESS, MAX_BRUSH_THICKNESS])
                        current_brush_thickness = int(thickness)
                        secondary_hand = positions[SECONDARY_HAND_ID]
                        secondary_middle_finger_x, secondary_middle_finger_y = secondary_hand[MIDDLE_TIP][1:]
                        cv2.circle(img, (secondary_middle_finger_x, secondary_middle_finger_y), current_brush_thickness,
                                   blue, cv2.FILLED)

            if selected_menu_item.mode == PM.MenuMode.eraser and up_fingers[1] and up_fingers[2] and up_fingers[3]:
                # erase mode
                # menu.select_by_mode(PM.MenuMode.eraser, cv2)
                cx, cy = middle_finger_x, middle_finger_y
                cv2.circle(img, (cx, cy), ERASER_THICKNESS, c4, cv2.FILLED)

                if xp == -1 and yp == -1:
                    xp, yp = cx, cy

                cv2.circle(img, (cx, cy), ERASER_THICKNESS, erase_color, cv2.FILLED)
                cv2.circle(img_canvas, (cx, cy), ERASER_THICKNESS, erase_color, cv2.FILLED)

            elif up_fingers[1] and up_fingers[2]:
                # hold mode
                # menu.select_by_mode(PM.MenuMode.hand, cv2)
                cx, cy = index_finger_x + (middle_finger_x - index_finger_x) // 2, index_finger_y
                xp, yp = -1, -1
                # cv2.circle(img, (cx, cy), 20, c2, cv2.FILLED)

                selected_menu_item = menu.select_menu_item_if_possible(cv2, (middle_finger_x, middle_finger_y))
                menu.select_by_mode(selected_menu_item.mode, cv2)

                cv2.putText(img, f'X: {int(cx)}', (SCREEN_WIDTH - 350, 100), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, c4,
                            2)
                cv2.putText(img, f'Y: {int(cy)}', (SCREEN_WIDTH - 250, 100), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, c4,
                            2)

            elif selected_menu_item.mode == PM.MenuMode.paint and up_fingers[1]:
                # draw mode
                cx, cy = index_finger_x, index_finger_y
                cv2.circle(img, (cx, cy), current_brush_thickness, drawing_color, cv2.FILLED)

                if xp == -1 and yp == -1:
                    xp, yp = cx, cy

                cv2.line(img, (xp, yp), (cx, cy), drawing_color, current_brush_thickness)
                cv2.line(img_canvas, (xp, yp), (cx, cy), drawing_color, current_brush_thickness)
                xp, yp = cx, cy

    img_gray = cv2.cvtColor(img_canvas, cv2.COLOR_BGR2GRAY)
    _, img_inverse = cv2.threshold(img_gray, 127, 255, cv2.THRESH_BINARY_INV)
    imgInverse = cv2.cvtColor(img_inverse, cv2.COLOR_GRAY2BGR)
    img = cv2.bitwise_and(img, imgInverse)
    img = cv2.bitwise_or(img, img_canvas)

    c_time = time.time()
    fps = 1 / (c_time - p_time)
    p_time = c_time

    # cv2.putText(img, f'FPS: {int(fps)}', (SCREEN_WIDTH - 100, 20), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, c4, 2)

    # cv2.putText(img, f'Mode: {selected_menu_item.title}', (SCREEN_WIDTH - 250, 50), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, c4, 2)

    cv2.imshow("Image", img)

    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
