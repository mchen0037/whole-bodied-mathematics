from threading import Thread

import cv2
import time

class VideoStreamWidget(object):
    def __init__ (self, src=0):
        self.capture = cv2.VideoCapture(src)
        self.src = src
        self.thread = Thread(target=self.update, args=())
        self.thread.daemon = True
        self.thread.start()

    def update(self):
        while True:
            if self.capture.isOpened():
                (self.status, self.frame) = self.capture.read()
                # save this stream as a video for data collection
                # grab aruco markers separately for position tracking
            time.sleep(0.1)

    def show_frame(self):
        cv2.imshow("frame" + str(self.src), self.frame)
        key = cv2.waitKey(1)
        if key == ord('q'):
            self.capture.release()
            cv2.destroyAllWindows()
            exit(1)
