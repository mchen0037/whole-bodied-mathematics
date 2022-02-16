import time
import numpy as np
import datetime
import os

import cv2
from cv2 import aruco

from threading import Thread

from .constants import constants as C

class VideoStreamWidget(object):
    def __init__ (self, id, camera_meta):
        self.id = id # camera id
        # {
        #     "src": int, the cv2.VideoCapture(#)
        #     "mtx": np.array, the camera matrix to undistort the image
        #     "dist_coeff": np.array, the distance coeffs to undistort the image
        #     "new_camera_mtx": np.array, the new camera matrix to undistort img
        #     "save_video" : bool, if we should save video or not
        # }
        self.camera_meta = camera_meta # meta info (see MocapSystem)
        self.src = camera_meta["src"] # cv2 camera source id or video history location
        self.capture = cv2.VideoCapture(self.src)
        self.status = None # Status of the camera
        self.use_roi = True # roi = Region of Interest
        self.img_raw = None # save for data collection
        self.img_gray = None # img_gray is undistorted
        self.undistorted_img = None # If use_roi is True, crop the img
        self.img_with_aruco = None

        if self.camera_meta["save_video"]:
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
                os.mkdir(C.SAVE_VIDEO_STREAM_FILE_PATH + YY_MM_DD_FOLDER)
            except OSError as error:
                print(error)
                print("Skipping")

            video_file_name = (C.SAVE_VIDEO_STREAM_FILE_PATH +
                YY_MM_DD_FOLDER +
                str(current_year) + "_" +
                str(current_month) + "_" +
                str(current_day) + "_" +
                str(current_hour) + "_" +
                str(current_minute) + "_camera_" +
                str(self.id) + ".avi"
            )
            print(video_file_name)
            self.video_result = cv2.VideoWriter(video_file_name,
                cv2.VideoWriter_fourcc(*'MJPG'),
                C.CAMERA_FRAME_RATE,
                C.CAMERA_FRAME_SIZE
            )
        else:
            self.video_result = None

        # {
        #     1: { # these are the aruco id value
        #        "camera_id": int the camera_id
        #        "rvec": np.array(3,1) # rotation vector
        #        "tvec": np.array(3,1) # translation vector
        #     }
        # }
        self.detected_aruco_ids_dict = {}

        self.thread = Thread(target=self.update, args=())
        self.thread.daemon = True
        self.thread.start()

    def save_image(self, file_path, type="RAW"):
        img_to_save = None
        if type == "RAW":
            img_to_save = self.img_raw
        elif type == "GRAY":
            img_to_save = self.img_gray
        elif type == "ARUCO":
            img_to_save = self.img_with_aruco
        else:
            print("Something went wrong in VideoStreamWidget.py save_image()")

        if img_to_save is not None:
            cv2.imwrite(file_path, img_to_save)
            print("Saved an image to", file_path)
            return 1

        return 0


    def transform_to_world(self, rvec, tvec):
        # Matrix Multiply to calculate the tvec of where the aruco marker is in
        # the world.
        CAM_MAT = None
        if self.id in C.CAMERA_EXTRINSIC_MATRIX_DICT.keys():
            CAM_MAT = C.CAMERA_EXTRINSIC_MATRIX_DICT[self.id]
        else:
            print("""
                WARNING: Camera Matrix not found in Dict.
                Using camera coordinates.
            """)
            return rvec, tvec

        CAM_ROT_MAT = CAM_MAT[:,0:3][0:3]
        CAM_TRA_MAT = CAM_MAT[:,3][0:3]
        new_tvec = CAM_ROT_MAT @ tvec + CAM_TRA_MAT
        return rvec, new_tvec

    def update(self, keep_old_values=False):
        prev = 0
        while True:
            # Reinitialize as an empty dictionary so that we can clear any old
            # data in case the marker is no longer detected.
            # This could be an interesting idea to study to see if it makes
            # pedagogical differences
            marker_id_pose_dict = {}

            if self.capture.isOpened():
                time_elapsed = time.time() - prev
                self.status, self.img_raw = self.capture.read()

                # Saving video stream for data collection
                if self.status and self.camera_meta["save_video"]:
                    if time_elapsed >= 1./C.CAMERA_FRAME_RATE:
                        prev = time.time()
                        self.video_result.write(self.img_raw)

                # undistort the image using the pre-loaded calibration file
                self.undistorted_img = cv2.undistort(
                    self.img_raw,
                    self.camera_meta["mtx"],
                    self.camera_meta["dist_coeff"],
                    None,
                    self.camera_meta["new_camera_mtx"]
                )

                # region of interest
                if self.use_roi == True:
                    x, y, w, h = self.camera_meta['roi']
                    self.undistorted_img = self.undistorted_img[y:y+h, x:x+w]
                self.img_gray = cv2.cvtColor(
                    self.undistorted_img, cv2.COLOR_RGB2GRAY
                )
                # Detect any AruCo Markers
                corners, detected_aruco_ids, rejected_pts = aruco.detectMarkers(
                    self.img_gray,
                    C.ARUCO_DICT,
                    parameters=C.ARUCO_PARAMS
                )
                if len(corners) != 0:
                    # estimate the position of aruco markers in the image frame
                    # https://docs.opencv.org/4.5.3/d9/d6a/group__aruco.html#ga84dd2e88f3e8c3255eb78e0f79571bd1
                    # this returns a list of rotation vectors and a list of
                    # translation vectors of where each id is located.
                    rvecs, tvecs, _objPoints = aruco.estimatePoseSingleMarkers(
                        corners,
                        C.MARKER_LENGTH,
                        self.camera_meta["new_camera_mtx"],
                        self.camera_meta["dist_coeff"],
                        None,
                        None
                    )
                    # If frame is read correctly and we have detected some ids
                    if self.status != 0 and detected_aruco_ids is not None:
                        # Draw the markers onto the image (axis on image)
                        self.undistorted_img = aruco.drawDetectedMarkers(
                            self.undistorted_img,
                            corners,
                            detected_aruco_ids,
                            (0,255,0)
                        )

                        # Go through the detected aruco_ids and assign their
                        # rvec, tvec as a dictionary.
                        # Save that dictionary as a class variable so that
                        # MocapSystem can aggregate across all VideoStreams
                        # to prep for JSON Transfer
                        for i, aruco_id in enumerate(detected_aruco_ids):
                            # Putting [0] here assumes that we only have one
                            # of each aruco marker. For my classroom, this
                            # should be a safe assumption to make.
                            # i.e. we should see at most 1 unique aruco id
                            # per camera.
                            rvec_world, tvec_world = self.transform_to_world(
                                rvecs[i][0],
                                tvecs[i][0]
                            )
                            marker_id_pose_dict[aruco_id[0]] = {
                                "camera_id": self.id,
                                "rvec": rvec_world,
                                "tvec": tvec_world
                            }

            # Depending on the value of keep_old_values, allow for setting the
            # class variable to empty dictionary
            # DeMorgan's Law is wack 1/23/22
            if len(marker_id_pose_dict) != 0 or not keep_old_values:
                self.detected_aruco_ids_dict = marker_id_pose_dict

    def show_frame(self):
        cv2.imshow("camera " + str(self.id), self.undistorted_img)
        if cv2.waitKey(25) & 0xFF == ord('q'):
            self.capture.release()
            cv2.destroyAllWindows()
            exit(1)
