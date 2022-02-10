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

class MocapSystem(object):
    def __init__(self, NUMBER_OF_CAMERAS_IN_SYSTEM, SAVE_VIDEO):
        self.num_cameras = NUMBER_OF_CAMERAS_IN_SYSTEM
        self.save_video = SAVE_VIDEO
        # for each camera camera_id_meta_dict carries data on:
        # "1": {
        #     "src": int, the cv2.VideoCapture(#)
        #     "mtx": np.array, the camera matrix to undistort the image
        #     "dist_coeff": np.array, the distance coeffs to undistort the image
        #     "new_camera_mtx": np.array, the new camera matrix to undistort img
        # }
        self.aruco_pose_dict = {} # a dictionary of PoseQueues
        self.camera_id_meta_dict, self.active_video_streams = self.load_cameras()

        self.pose_history_file_name = self.get_pose_history_file_name()

        self.thread = Thread(target=self.update_detected_markers, args=())
        self.thread.daemon = True
        self.thread.start()

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
                camera_meta["save_video"] = self.save_video
                camera_id_meta_dict[int(cam)] = camera_meta

        # After finding all camera matrices, make sure we assert that we have
        # the same amount of real cameras and sources.
        if len(camera_id_meta_dict.keys()) != self.num_cameras:
            raise AssertionError("""
                Camera Sources and Number of Cameras in System mismatched!
            """)

        # All video streams will be appended in a list held in this Class
        for key in camera_id_meta_dict.keys():
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
                    f.write("timestamp, id, x, y, z")
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
        print("Looking for detected Markers!")
        while True:
            for v in self.active_video_streams:
                for aruco_id in v.detected_aruco_ids_dict.keys():
                    if aruco_id in self.aruco_pose_dict:
                        rvec_arr = v.detected_aruco_ids_dict[aruco_id]["rvec"]
                        tvec_arr = v.detected_aruco_ids_dict[aruco_id]["tvec"]
                        self.aruco_pose_dict[aruco_id].push(tvec_arr)
                    else:
                        self.aruco_pose_dict[aruco_id] = PoseQueue(
                            aruco_id,
                            v.detected_aruco_ids_dict[aruco_id]["tvec"]
                        )

            time.sleep(1 / 30)

    def get_average_detected_markers(self):
        # Grabs the expected position from each PoseQueue for each aruco id
        # And returns it for JSON transfer
        expected_aruco_poses_dict = {}
        for aruco_id in self.aruco_pose_dict:
            expected_aruco_poses_dict[aruco_id] = (
                self.aruco_pose_dict[aruco_id].get_expected_pose(
                    save = False,
                    save_location = self.pose_history_file_name
                )
            )

        return expected_aruco_poses_dict











# end
