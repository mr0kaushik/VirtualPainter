import cv2
import time
import HandTrackingModule as htm

p_time = 0
cap = cv2.VideoCapture(0)

detector = htm.HandDetector()

while True:
    success, img = cap.read()
    img, positions = detector.find_hand(img)

    if len(positions) > 0:
        print("Complete", positions)

    # fps calculation
    c_time = time.time()
    fps = 1 / (c_time - p_time)
    p_time = c_time

    cv2.putText(img, "fps : " + str(int(fps)), (10, 70), cv2.FONT_HERSHEY_PLAIN,
                1, (255, 255, 255), 1)

    cv2.imshow("Image", img)
    cv2.waitKey(1)
