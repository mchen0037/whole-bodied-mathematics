import time
import numpy as np
import datetime
import os

import cv2
from cv2 import aruco

from multiprocessing import Process
from threading import Thread

from .constants import constants as C

class VideoStreamWidget(object):
    """
        VideoStreamWidget handles everything at the camera level, primarily
            - reading the camera
            - undistoring images
            - detecting aruco markers
            - saving video #FIXME: cannot record multiple streams right now

        - id <int>: the camera id in the real world

        - camera_meta <dict>: Meta info passed in from MocapSystem
            {
                "src": int, the cv2.VideoCapture(#)
                "mtx": np.array, the camera matrix to undistort the image
                "dist_coeff": np.array, the distance coeffs to undistort the image
                "new_camera_mtx": np.array, the new camera matrix to undistort img
                "save_video" : bool, if we should save video or not
            }

        - capture <cv2.VideoCapture>: the VideoCapture object for reading the camera

        - status <bool>: Status of the camera, returned from cv2.VideoCapture.read()

        - use_roi <bool>: When calling cv2.undistort(), we get a region of interest (ROI)
            box. use_roi determines if we want to crop our image based on that ROI

        - img_raw <np.array>: the raw image from the camera, without any processing done

        - img_gray <np.array>: the raw image turned into gray scale

        - undistorted_img <np.array>: The image, undistorted. If use_roi is True,
            this image is cropped.

        - img_with_aruco <np.array>: The image with drawn boxes around aruco
            markers

        - video_result <cv2.VideoWriter>: The VideoWriter object which is used
            for saving video #FIXME: cannot record multiple streams right now

        - record_start_time <float>: time.time() value which determines when
            to start saving video

        - detected_aruco_ids_dict <dict>: Dictionary gives the detected
            id position, based on the camera. This is an intrinsic camera value.
            {
                1: { # these are the aruco id value
                   "camera_id": <int> the camera_id
                   "rvec": <np.array(3,1)> rotation vector
                   "tvec": <np.array(3,1)> translation vector
                }
            }

        - update_thread <Thread>: Thread to handle reading the cameras, undistorting
            the image, and detecting aruco markers. # TODO: Is there value in
            putting this in a Process instead of a Thread?

        - save_video_thread <Thread>: Handles saving video in a separate thread
    """
    def __init__ (self, id, camera_meta, record_start_time):
        self.id = id # camera id
        self.camera_meta = camera_meta # meta info (see MocapSystem)
        self.src = camera_meta["src"] # cv2 camera source id or video history location
        self.capture = cv2.VideoCapture(self.src)
        self.status = None # Status of the camera
        self.use_roi = False # roi = Region of Interest
        self.img_raw = None # save for data collection
        self.img_gray = None # img_gray is undistorted
        self.undistorted_img = None # If use_roi is True, crop the img
        self.img_with_aruco = None
        self.video_result = self.get_video_result()
        self.record_start_time = record_start_time

        self.detected_aruco_ids_dict = {}

        self.update_thread = Thread(target=self.update, args=())
        self.update_thread.daemon = True
        self.update_thread.start()

        # Saving video on all cameras is too intensive for my computer.
        # Default is going to be false and I'll try to capture just 1 for data collection
        if camera_meta["save_video"]:
            self.save_video_thread = Thread(target=self.save_video, args=())
            self.save_video_thread.daemon = True
            self.save_video_thread.start()


    def get_video_result(self):
        """
            Creates the folder and the .avi file for video recording.

            Inputs: None

            Returns:
                - video_result <cv2.VideoWriter> VideoWriter object which handles
                    saving a .avi file on the file system
        """
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
            return cv2.VideoWriter(video_file_name,
                cv2.VideoWriter_fourcc(*'MJPG'),
                C.CAMERA_FRAME_RATE,
                C.CAMERA_FRAME_SIZE
            )
        else:
            return None


    def save_video(self):
        """
            Handles writing the raw image into a video file. This function is
            run in save_video_thread for optimization.

            Inputs: None

            Returns: None
        """
        prev = 0
        while True:
            if time.time() > self.record_start_time:
                time_elapsed = time.time() - prev
                if time_elapsed >= 1./C.CAMERA_FRAME_RATE:
                    # print(time_elapsed)
                    prev = time.time()
                    self.video_result.write(self.img_raw)


    def save_image(self, file_path, type="RAW"):
        """
            Saves a singular image to a file path.

            Inputs:
                - file_path <string>: The file path to where to save the image
                - type <string>: Which type of image the user wants to save.

            Returns:
                - success <bool>: Indicates if the saving was successful or not
        """
        success = False
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
            success = True
            return success

        return success


    def transform_to_world(self, rvec, tvec):
        """
            Applies a matrix transformation to convert from the camera's
            intrinsic position to the world's extrinsic position. These
            matrices are held in constants.py and are calculated through
            Guoxiang's Posegraph.jl.

            Inputs:
                - rvec <np.array> Intrinsic Rotation vector
                - tvec <np.array> Intrinsic Translation vector

            Returns:
                - rvec <np.array> The same input rotation vector
                    # TODO: Will we ever need to calculate the new rotation vec?
                - new_tvec <np.array> Extrinsic translation vector
        """
        # Matrix Multiply to calculate the tvec of where the aruco marker is in
        # the world.
        CAM_MAT = None
        if self.id in list(C.CAMERA_EXTRINSIC_MATRIX_DICT):
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


    def update(self):
        """
            Reads the VideoCapture object to get the most recent camera image,
            processes the image, and updates detected_aruco_ids_dict for
            any new detected aruco_ids. This function is ran on update_thread
            for optimization.

            Inputs: None

            Returns: None
        """
        while True:
            # Reinitialize as an empty dictionary so that we can clear any old
            # data in case the marker is no longer detected.
            # This could be an interesting idea to study to see if it makes
            # pedagogical differences
            marker_id_pose_dict = {}

            if self.capture.isOpened():
                self.status, self.img_raw = self.capture.read()

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

            # if len(marker_id_pose_dict) != 0:
            self.detected_aruco_ids_dict = marker_id_pose_dict
            time.sleep(1./C.CAMERA_FRAME_RATE)


    def show_frame(self):
        """
            Shows the frame using cv2 UI. This function needs to be updated into
            a front-end application instead. #TODO

            Inputs: None

            Returns: None
        """
        cv2.imshow("camera " + str(self.id), self.undistorted_img)
        if cv2.waitKey(25) & 0xFF == ord('q'):
            self.capture.release()
            cv2.destroyAllWindows()
            exit(1)
