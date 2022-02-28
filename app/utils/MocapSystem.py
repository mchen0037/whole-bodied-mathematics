import time
import datetime
import numpy as np
import os

import cv2
from cv2 import aruco

from threading import Thread

from .constants import constants as C

from .VideoStreamWidget import VideoStreamWidget
from .PoseQueue import PoseQueue
from .ScreenCapture import ScreenCapture

class MocapSystem(object):
    def __init__(
        self,
        NUMBER_OF_CAMERAS_IN_SYSTEM,
        SAVE_VIDEO=False,
        RECORD_START_TIME=time.time() + 20,
        OLD_VIDEO_PATH=None,
        MODE=0,
        ROUNDING_AMOUNT=10
    ):
        self.num_cameras = NUMBER_OF_CAMERAS_IN_SYSTEM
        self.save_video = SAVE_VIDEO
        self.record_start_time = RECORD_START_TIME
        self.old_video_path = OLD_VIDEO_PATH
        self.rounding_amount = ROUNDING_AMOUNT # How much to round output to
        self.mode = MODE # Graph X-Y (0) or X-Z (1)

        # for each camera camera_id_meta_dict carries data on:
        # "1": {
        #     "src": int, the cv2.VideoCapture(#)
        #     "mtx": np.array, the camera matrix to undistort the image
        #     "dist_coeff": np.array, the distance coeffs to undistort the image
        #     "new_camera_mtx": np.array, the new camera matrix to undistort img
        # }
        self.aruco_pose_dict = {} # a dictionary of PoseQueues
        self.active_video_streams = []
        self.camera_id_meta_dict = {}

        if self.old_video_path == None:
            self.camera_id_meta_dict, self.active_video_streams = (
                self.load_cameras()
            )
        else:
            self.camera_id_meta_dict, self.active_video_streams = (
                self.load_video_history()
            )

        self.pose_history_file_name = self.get_pose_history_file_name()
        if self.save_video:
            self.screen_capture = ScreenCapture(self.record_start_time)
            print("Screen Capture saving.")
        else:
            print("Screen Capture not being saved.")

        self.threading = Thread(target=self.update_detected_markers)
        self.threading.daemon = True
        self.threading.start()

    def load_cameras(self):
        # This for loop iterates over 200 cv2 Video Capture Sources
        # Doing this because the webcams aren't correlating with what's in
        # /dev/video/*. The Camera number corresponds to the camera id
        # based on my setup. It's just used for calibration and transformation.
        camera_id_meta_dict = {}
        active_video_streams = []
        for src in range(0, 100):
            cap = cv2.VideoCapture(src)
            test, frame = cap.read()
            if test:
                camera_meta = {}
                print("cv2 Camera Source", src, "found.")
                cam = input("Which Camera number?  ")
                camera_meta["src"] = int(src)

                camera_meta["mtx"] = C.CAMERA_CALIBRATION_MATRIX
                camera_meta["dist_coeff"] = C.CAMERA_CALIBRATION_DISTANCE_COEFF

                # Calculate the Camera Matrix from the yaml fgle
                img_gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
                h, w = img_gray.shape[:2]
                # https://docs.opencv.org/3.3.0/d9/d0c/group__calib3d.html#ga7a6c4e032c97f03ba747966e6ad862b1
                new_camera_mtx, roi = cv2.getOptimalNewCameraMatrix(
                    camera_meta["mtx"],
                    camera_meta["dist_coeff"],
                    (w, h),
                    1,
                    (w, h)
                )
                camera_meta["new_camera_mtx"] = new_camera_mtx
                camera_meta["roi"] = roi
                # Hack-y way to handle this for now. Computer can't keep up
                # with saving all 4 video streams.
                if int(cam) == 3:
                    camera_meta["save_video"] = self.save_video
                else:
                    camera_meta["save_video"] = False
                camera_id_meta_dict[int(cam)] = camera_meta

        # After finding all camera matrices, make sure we assert that we have
        # the same amount of real cameras and sources.
        if len(list(camera_id_meta_dict)) != self.num_cameras:
            raise AssertionError("""
                Camera Sources and Number of Cameras in System mismatched!
            """)
        os.system('clear')

        # All video streams will be appended in a list held in this Class
        for key in list(camera_id_meta_dict):
            v = VideoStreamWidget(
                key,
                camera_id_meta_dict[key],
                self.record_start_time
            )
            active_video_streams.append(v)

        return camera_id_meta_dict, active_video_streams

    def load_video_history(self):
        camera_id_meta_dict = {}
        active_video_streams = []

        cap = cv2.VideoCapture(self.old_video_path + "1.avi")
        test, frame = cap.read()

        for i in range(1, self.num_cameras + 1):
            camera_meta = {}
            camera_meta["src"] = self.old_video_path + str(i) + ".avi"
            print(self.old_video_path + str(i) + ".avi")

            camera_meta["mtx"] = C.CAMERA_CALIBRATION_MATRIX
            camera_meta["dist_coeff"] = C.CAMERA_CALIBRATION_DISTANCE_COEFF

            # Calculate the Camera Matrix from the yaml fgle
            img_gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
            h, w = img_gray.shape[:2]
            # https://docs.opencv.org/3.3.0/d9/d0c/group__calib3d.html#ga7a6c4e032c97f03ba747966e6ad862b1
            new_camera_mtx, roi = cv2.getOptimalNewCameraMatrix(
                camera_meta["mtx"],
                camera_meta["dist_coeff"],
                (w, h),
                1,
                (w, h)
            )
            camera_meta["new_camera_mtx"] = new_camera_mtx
            camera_meta["roi"] = roi
            camera_meta["save_video"] = False
            camera_id_meta_dict[i] = camera_meta

        for key in list(camera_id_meta_dict):
            v = VideoStreamWidget(key, camera_id_meta_dict[key])
            active_video_streams.append(v)

        return camera_id_meta_dict, active_video_streams


    def get_pose_history_file_name(self):
        pose_history_file_name = None
        if self.save_video == True:
            for v in self.active_video_streams:
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
                    os.mkdir(C.SAVE_POSE_HISTORY_FILE_PATH + YY_MM_DD_FOLDER)
                except OSError as error:
                    print(error)
                    print("Skipping")

                pose_history_file_name = (C.SAVE_POSE_HISTORY_FILE_PATH +
                    YY_MM_DD_FOLDER +
                    str(current_year) + "_" +
                    str(current_month) + "_" +
                    str(current_day) + "_" +
                    str(current_hour) + "_" +
                    str(current_minute) + "_pose_history.csv"
                )
                try:
                    f = open(pose_history_file_name, "x")
                    f.write("timestamp, id, x, y, z\n")
                    f.close()
                except OSError as error:
                    print(error)
                    print("Skipping")
        else:
            print("Pose History not being saved.")
        return pose_history_file_name

    def update_detected_markers(self):
        # Restructure the data so that we can prep for JSON Transfer
        # Iterate through each camera and their detected aruco markers
        # Append each detected Pose into a PoseQueue object so that we can
        # calculate the running average of its position.
        prev = 0
        while True:
            time_elapsed = time.time() - prev
            if time_elapsed >= 1./C.CAMERA_FRAME_RATE:
                prev = time.time()
                for v in self.active_video_streams:
                    for aruco_id in list(v.detected_aruco_ids_dict):
                        if aruco_id in self.aruco_pose_dict:
                            rvec_arr = v.detected_aruco_ids_dict[aruco_id]["rvec"]
                            tvec_arr = v.detected_aruco_ids_dict[aruco_id]["tvec"]
                            self.aruco_pose_dict[aruco_id].push(tvec_arr)
                        else:
                            self.aruco_pose_dict[aruco_id] = PoseQueue(
                                aruco_id,
                                v.detected_aruco_ids_dict[aruco_id]["tvec"]
                            )
                    # if aruco_id == 1:
                    #     print(v.id, v.detected_aruco_ids_dict[aruco_id]["tvec"])


    def get_average_detected_markers(self):
        # Grabs the expected position from each PoseQueue for each aruco id
        # And returns it for JSON transfer
        expected_aruco_poses_dict = {}
        for aruco_id in list(self.aruco_pose_dict):
            expected_aruco_poses_dict[aruco_id] = (
                self.aruco_pose_dict[aruco_id].get_expected_pose(
                    save = self.save_video,
                    save_location = self.pose_history_file_name
                )
            )

        return expected_aruco_poses_dict











# end
