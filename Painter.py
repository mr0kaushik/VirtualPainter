import cv2
import time
import numpy as np

import module.HandTrackingModule as htm

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

cap = cv2.VideoCapture(0)
cap.set(3, SCREEN_WIDTH)
cap.set(4, SCREEN_HEIGHT)

p_time = 0

hand_detector = htm.HandDetector(min_detection_confidence=0.6)

pen_tip = 8
hold_tip = 12
eraser_tip = 16
BRUSH_THICKNESS = 15
ERASER_THICKNESS = 20
xp, yp = -1, -1

img_canvas = np.zeros((SCREEN_HEIGHT, SCREEN_WIDTH, 3), np.uint8)

while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)

    drawing_color = c7
    erase_color = (0, 0, 0)
    # 0. Find Hand Landmarks
    img, positions = hand_detector.find_hand(img)
    # print("imgshape", img.shape)
    # print("canvasshape", img_canvas.shape)

    if len(positions) > 0:
        pen_x, pen_y = positions[0][pen_tip][1:]
        hold_x, hold_y = positions[0][hold_tip][1:]
        eraser_x, eraser_y = positions[0][eraser_tip][1:]

        # 1. drawing mode : index finger is up
        up_fingers = hand_detector.fingers_state()

        if len(up_fingers) == 5 and up_fingers[4] == False:
            if up_fingers[1] and up_fingers[2] and up_fingers[3]:
                # erase mode
                cx, cy = hold_x, hold_y
                cv2.circle(img, (cx, cy), 60, c4, cv2.FILLED)

                if xp == -1 and yp == -1:
                    xp, yp = cx, cy

                cv2.circle(img, (cx, cy), 60, erase_color, cv2.FILLED)
                cv2.circle(img_canvas, (cx, cy), 60, erase_color, cv2.FILLED)

            elif up_fingers[1] and up_fingers[2]:
                # hold mode
                cx, cy = pen_x + (hold_x - pen_x) // 2, pen_y
                xp, yp = -1, -1
                cv2.circle(img, (cx, cy), 20, c2, cv2.FILLED)

            elif up_fingers[1]:
                # draw mode
                cx, cy = pen_x, pen_y
                cv2.circle(img, (cx, cy), 10, drawing_color, cv2.FILLED)

                if xp == -1 and yp == -1:
                    xp, yp = cx, cy

                cv2.line(img, (xp, yp), (cx, cy), drawing_color, BRUSH_THICKNESS)
                cv2.line(img_canvas, (xp, yp), (cx, cy), drawing_color, BRUSH_THICKNESS)
                xp, yp = cx, cy

    img_gray = cv2.cvtColor(img_canvas, cv2.COLOR_BGR2GRAY)
    _, img_inverse = cv2.threshold(img_gray, 127, 255, cv2.THRESH_BINARY_INV)
    imgInverse = cv2.cvtColor(img_inverse, cv2.COLOR_GRAY2BGR)
    img = cv2.bitwise_and(img, imgInverse)
    img = cv2.bitwise_or(img, img_canvas)

    c_time = time.time()
    fps = 1 / (c_time - p_time)
    p_time = c_time

    cv2.putText(img, f'FPS: {int(fps)}', (20, 20), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, c4, 2)

    cv2.imshow("Image", img)

    cv2.waitKey(1)
