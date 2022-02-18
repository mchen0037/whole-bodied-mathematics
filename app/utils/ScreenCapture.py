import os
import datetime
import time

import cv2
import numpy as np
import pyscreenshot as ImageGrab
from multiprocessing import Process

from .constants import constants as C

class ScreenCapture(object):
    def __init__(self):
        self.video_result = self.get_video_result()

        self.process = Process(target=self.update, args=())
        self.process.daemon = True
        self.process.start()


    def get_video_result(self):
        current_datetime = datetime.datetime.now()
        current_year = current_datetime.year
        current_month = current_datetime.month
        current_day = current_datetime.day
        current_hour = current_datetime.hour
        current_minute = current_datetime.minute

        YY_MM_DD_FOLDER = (
            str(current_year) + "_" +
            str(current_month) + "_" +
            str(current_day) + "/"
        )

        try:
            os.mkdir(C.SAVE_SCREEN_STREAM_FILE_PATH + YY_MM_DD_FOLDER)
        except OSError as error:
            print(error)
            print("Skipping")

        video_file_name = (C.SAVE_SCREEN_STREAM_FILE_PATH +
            YY_MM_DD_FOLDER +
            str(current_year) + "_" +
            str(current_month) + "_" +
            str(current_day) + "_" +
            str(current_hour) + "_" +
            str(current_minute) + "_screen.avi"
        )

        return cv2.VideoWriter(video_file_name,
            cv2.VideoWriter_fourcc(*'MJPG'),
            C.CAMERA_FRAME_RATE,
            C.SCREEN_CAPTURE_SIZE
        )

    def update(self):
        prev = 0
        while True:
            # ImageGrab uses PIL, which saves as RGB, OpenCV uses BGR.
            screenshot = np.array(
                ImageGrab.grab(
                    backend="mss", childprocess=False
                )
            )
            cv_img = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)
            time_elapsed = time.time() - prev
            if time_elapsed >= 1./C.CAMERA_FRAME_RATE:
                prev = time.time()
                self.video_result.write(cv_img)
