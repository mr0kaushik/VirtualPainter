import cv2
import mediapipe as mp
import time


class HandDetector:
    def __init__(self,
                 mode=False,
                 max_num_hands=2,
                 min_detection_confidence=0.5,
                 min_tracking_confidence=0.5):
        self.mode = mode
        self.max_num_hands = max_num_hands
        self.min_detection_confidence = min_detection_confidence
        self.min_tracking_confidence = min_tracking_confidence

        self.tipIds = [4, 8, 12, 16, 20]
        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(self.mode, self.max_num_hands,
                                        self.min_detection_confidence,
                                        self.min_tracking_confidence)
        self.mpDraw = mp.solutions.drawing_utils

    def find_hand_with_points(self, img, draw=True, draw_point=True, points=[]):
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(img_rgb)

        hand_list = []

        if self.results.multi_hand_landmarks:
            for handLMS in self.results.multi_hand_landmarks:
                hand = {}
                for idx, lm in enumerate(handLMS.landmark):
                    if idx in points:
                        height, width, channel = img.shape
                        center_x, center_y = int(lm.x * width), int(lm.y * height)
                        hand[idx] = {"id": idx, "center_x": center_x, "center_y": center_y}

                        if draw_point:
                            cv2.circle(img, (center_x, center_y), 5, (255, 0, 0), cv2.FILLED)

                if len(hand) > 0:
                    hand_list.append(hand)

                if draw:
                    self.mpDraw.draw_landmarks(img, handLMS, self.mpHands.HAND_CONNECTIONS)
        return img, hand_list

    def find_hand(self, img, draw=True):
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(img_rgb)

        self.hand_list = []

        if self.results.multi_hand_landmarks:
            for handLMS in self.results.multi_hand_landmarks:
                hand = []
                for idx, lm in enumerate(handLMS.landmark):
                    height, width, channel = img.shape
                    center_x, center_y = int(lm.x * width), int(lm.y * height)
                    hand.append((idx, center_x, center_y))

                    # if draw:
                    #     cv2.circle(img, (center_x, center_y), 5, (255, 0, 0), cv2.FILLED)

                self.hand_list.append(hand)

                if draw:
                    self.mpDraw.draw_landmarks(img, handLMS, self.mpHands.HAND_CONNECTIONS)
        return img, self.hand_list

    def fingers_state(self):
        fingers = []
        if len(self.hand_list) > 0:
            hand = self.hand_list[0]
            # thumb
            fingers.append(hand[self.tipIds[0]][1] < hand[self.tipIds[0] - 1][1])
            # rest fingers
            for idx in range(1, 5):
                fingers.append(hand[self.tipIds[idx]][2] < hand[self.tipIds[idx] - 2][2])

        return fingers


def main():
    p_time = 0
    cap = cv2.VideoCapture(0)

    detector = HandDetector(min_detection_confidence=0.8)

    while True:
        success, img = cap.read()
        img, positions = detector.find_hand(img)

        # if len(positions) > 0:
        #     print("Complete", positions)

        fingers = detector.fingers_state()
        print(fingers)

        # img, positions = detector.find_hand_with_points(img, points=[3, 4])
        # if len(positions) > 0:
        #     print("3- >>>", positions[0][3])

        # fps calculation
        c_time = time.time()
        fps = 1 / (c_time - p_time)
        p_time = c_time

        cv2.putText(img, "fps : " + str(int(fps)), (10, 70), cv2.FONT_HERSHEY_PLAIN,
                    1, (255, 255, 255), 1)

        cv2.imshow("Image", img)
        cv2.waitKey(1)


if __name__ == "__main__":
    main()
