"""
    The MocapSystem Class handles the entire camera system as a whole. It
    handles data aggregation across the VideoStreamWidgets and prepares it to be
    sent to the client-side.
"""

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
    """
        A class to describe the entire motion capture system. This object keeps
        track of all data in the system and all boolean flags which are used
        throughout the code.

        Class Variables:
        - num_cameras <int> : how many cameras are going to be read.
            This corresponds to C.NUM_CAMERAS in constants.py

        - save_video <boolean>: Flag which determines if we should save
            VideoStreamWidget data or not. Currently (2/27/22), if this is
            marked True, it will only save data from Camera 3. This is a #FIXME,
            as my computer can't handle recording all cameras at the same time

        - screen_capture: <ScreenCapture> Handles screen capturing if save_video
            is set to True

        - record_start_time <float>: a time.time() value. If save_video is True,
            time the system will start recording at, to help sync up all the
            videos together. #FIXME

        - old_video_path <string>: This path is used to read old VideoStream to
            run the system based on old inputs. Currently (2/27/22) useless,
            since I can't record all four cameras. Example:
            "/media/mighty/research-1/collected_data_from_cameras/video/2022_2_17/2022_2_14_17_32_camera_"

        - rounding_amount <int>: determines how much I round my output to. i.e.
            a rounding_amount of 5 will round 93.141283 to 95.

        - scale_x <float>: Determines what to multiply every value by to scale
            the room up or down for the x value.

        - scale_y <float>: Determines what to multiply every value by to scale
            the room up or down for the y value.

        - mode <int>: which tell us to plot using (x,y) positions in the room
            (0) or (x,z) positions in the room (1)

        - aruco_pose_dict <dictionary>: Each key refers to a particular
            aruco id and the value is a PoseQueue to determine the position.

        - active_video_streams <List<VideoStreamWidget>>: a list of all the
            VideoStreamWidget objects which handle all cameras

        - camera_id_meta_dict <dictionary>: Describes meta data of the camera.
            Example:
            <int> camera_id {
                "src": <int> the cv2.VideoCapture(#)
                "mtx": <np.array> the camera matrix to undistort the image
                "dist_coeff": <np.array> the distance coeffs to undistort image
                "new_camera_mtx": <np.array> the camera matrix to undistort img
                "save_video": <bool> if we should save video or not
            }

        - update_markers_thread <Thread>: Handles restructuring data into JSON
            format

    """
    def __init__(
        self,
        NUMBER_OF_CAMERAS_IN_SYSTEM,
        SAVE_VIDEO=False,
        RECORD_START_TIME=time.time() + 20,
        OLD_VIDEO_PATH=None,
        MODE=0,
        ROUNDING_AMOUNT=10,
        BOUNDS=C.DEFAULT_BOUNDS,
        ORIGIN=C.DEFAULT_ORIGIN,
    ):
        self.num_cameras = NUMBER_OF_CAMERAS_IN_SYSTEM
        self.save_video = SAVE_VIDEO
        self.record_start_time = RECORD_START_TIME
        self.old_video_path = OLD_VIDEO_PATH
        self.rounding_amount = ROUNDING_AMOUNT # How much to round output to
        self.bounds = BOUNDS
        self.origin = ORIGIN
        self.mode = MODE # Graph X-Y (0) or X-Z (1)

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

        self.update_markers_thread = Thread(target=self.update_detected_markers)
        self.update_markers_thread.daemon = True
        self.update_markers_thread.start()


    def load_cameras(self):
        """
            Asks the user which cameras are turned on to create an association
            between the camera_ids and VideoCapture objects. This function is
            used for live MocapSystem data, rather than replaying the history.

            Inputs: None

            Returns:
                - camera_id_meta_dict <dict>: The meta data for each camera.
                    Example in MocapSystem comment

                - active_video_streams <list>: List of VideostreamWidgets for
                    handling the Mocap System
        """
        # This for loop iterates over 100 cv2 Video Capture Sources
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

                # FIXME: Hack-y way to handle this for now. Computer can't keep up
                # with saving all 4 video streams.
                # if int(cam) == 3:
                    # camera_meta["save_video"] = self.save_video
                # else:
                # Never save video for now.
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
        """
            When we're using old video data to replay the MocapSystem outputs,
            this function is called instead of load_cameras.

            Inputs: None

            Returns:
                - camera_id_meta_dict <dict>: The meta data for each camera.
                    Example in MocapSystem comment
                - active_video_streams <list>: List of VideoStreamWidgets for
                    handling the Mocap System
        """
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
        """
            Creates folders and files the prepare saving for the Pose History.

            Inputs: None

            Returns:
                - pose_history_file_name <string>: File path to the CSV file
                    which will save timestamped positions of aruco_ids.
        """
        pose_history_file_name = None
        if self.save_video == True:
            for v in self.active_video_streams:
                # FIXME: Cannot save all camera inputs at the same time right now.
                if v.id == 3:
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
        """
            Accesses the data inside VideoStreamWidget.detected_aruco_ids_dict
            and restructures it for easy access for JSON transfer. This function
            is called repeatedly through the update_markers_thread Thread.

            Inputs: None

            Returns: None
        """
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
                            rvec_arr = (
                                v.detected_aruco_ids_dict[aruco_id]["rvec"]
                            )
                            tvec_arr = (
                                v.detected_aruco_ids_dict[aruco_id]["tvec"]
                            )

                            self.aruco_pose_dict[aruco_id].push(tvec_arr)
                        else:
                            self.aruco_pose_dict[aruco_id] = PoseQueue(
                                aruco_id,
                                v.detected_aruco_ids_dict[aruco_id]["tvec"]
                            )

    def get_average_detected_markers(self):
        """
            Uses the PoseQueue data from update_detected_markers to calculate
            the expected value of each detected marker and then sends it to
            app.py to transfer to the front end

            Inputs: None

            Returns:
                - expected_aruco_poses_dict <dict>: A dictionary with keys of
                    aruco_ids and values of the expected [x, y, z] (list) values
        """
        # Grabs the expected position from each PoseQueue for each aruco id
        # And returns it for JSON transfer
        expected_aruco_poses_dict = {}
        for aruco_id in list(self.aruco_pose_dict):
            expected_pose = self.aruco_pose_dict[aruco_id].get_expected_pose(
                save = self.save_video,
                save_location = self.pose_history_file_name
            )
            expected_aruco_poses_dict[aruco_id] = expected_pose
        return expected_aruco_poses_dict
