import os
import datetime
import time

import cv2
import numpy as np
import pyscreenshot as ImageGrab
from multiprocessing import Process

from .constants import constants as C

class ScreenCapture(object):
    """
        ScreenCapture handles all the screen capturing capability of the MocapSystem
        When MocapSystem.save_video is True, we save the Screen Capture.

        - video_result <cv2.VideoWriter>: VideoWriter object which handles
            saving a .avi file on the file system

        - record_start_time <float>: A value from time.time() which indicates
            when to start recording the screen.

        - update_process <Process>: Throws saving the video saving into a new
            process to optimize runtime.
    """
    def __init__(self, record_start_time):
        self.video_result = self.get_video_result()
        self.record_start_time = record_start_time

        self.update_process = Process(target=self.update, args=())
        self.update_process.daemon = True
        self.update_process.start()


    def get_video_result(self):
        """
            Creates the folder and the .avi file for screen recording.

            Inputs: None

            Returns:
                - video_result <cv2.VideoWriter> VideoWriter object which handles
                    saving a .avi file on the file system
        """
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

        video_result = cv2.VideoWriter(video_file_name,
            cv2.VideoWriter_fourcc(*'MJPG'),
            C.SCREEN_CAPTURE_FRAME_RATE,
            C.SCREEN_CAPTURE_SIZE
        )

        return video_result

    def update(self):
        """
            Grabs a screenshot from the display and then writes it to the
            video_result object. This function is being run on a separate
            Proces and has limited access to variables.

            Inputs: None

            Returns: None
        """
        prev = 0
        while True:
            if time.time() > self.record_start_time:
                time_elapsed = time.time() - prev
                # ImageGrab uses PIL, which saves as RGB, OpenCV uses BGR.
                if time_elapsed >= 1./C.SCREEN_CAPTURE_FRAME_RATE:
                    prev = time.time()
                    screenshot = np.array(
                        ImageGrab.grab(
                            backend="mss", childprocess=False
                        )
                    )
                    cv_img = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)
                    self.video_result.write(cv_img)
