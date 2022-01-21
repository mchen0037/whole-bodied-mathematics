from threading import Thread

import cv2
import time

class VideoStreamWidget(object):
    def __init__ (self, id, camera_meta):
        self.id = id
        self.camera_meta = camera_meta
        self.src = camera_meta["src"]
        self.capture = cv2.VideoCapture(self.src)
        self.thread = Thread(target=self.update, args=())
        self.thread.daemon = True
        self.thread.start()

    def update(self):
        while True:
            if self.capture.isOpened():
                self.status, self.img_raw = self.capture.read()
                self.undistorted_img = cv2.undistort(
                    self.img_raw,
                    self.camera_meta["mtx"],
                    self.camera_meta["dist_coeff"],
                    None,
                    self.camera_meta["new_camera_mtx"]
                )
                # save this stream as a video for data collection
                # grab aruco markers separately for position tracking

            time.sleep(0.1)

    def show_frame(self):
        cv2.imshow("camera " + str(self.id), self.undistorted_img)
        key = cv2.waitKey(1)
        if key == ord('q'):
            self.capture.release()
            cv2.destroyAllWindows()
            exit(1)
