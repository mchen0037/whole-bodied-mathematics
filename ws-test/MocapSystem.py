import yaml
import time
import numpy as np

import cv2
from cv2 import aruco

from threading import Thread

from VideoStreamWidget import VideoStreamWidget
from PoseQueue import PoseQueue

class MocapSystem(object):
    def __init__(self, NUMBER_OF_CAMERAS_IN_SYSTEM):
        self.num_cameras = NUMBER_OF_CAMERAS_IN_SYSTEM
        # for each camera camera_id_meta_dict carries data on:
        # "1": {
        #     "src": int, the cv2.VideoCapture(#)
        #     "mtx": np.array, the camera matrix to undistort the image
        #     "dist_coeff": np.array, the distance coeffs to undistort the image
        #     "new_camera_mtx": np.array, the new camera matrix to undistort img
        # }
        self.camera_id_meta_dict, self.active_video_streams = self.load_cameras()
        self.aruco_pose_dict = {} # a dictionary of PoseQueues

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
        for src in range(0, 2):
            cap = cv2.VideoCapture(src)
            test, frame = cap.read()
            if test:
                camera_meta = {}
                print("cv2 Camera Source", src, "found.")
                cam = input("Which Camera number?  ")
                camera_meta["src"] = int(src)

                # Get the information from calibration matrices
                # Put the matrix in camera_id_meta_dict
                # TODO: should I just use one camera calibration matrix or
                # multiple?
                file_name = ("./camera_calibration_matrices/calibration_" +
                    # cam +
                    str(2) +
                    ".yaml"
                )
                try:
                    with open(file_name) as f:
                        loadeddict = yaml.load(f, Loader=yaml.FullLoader)
                    camera_meta["mtx"] = np.array(
                        loadeddict.get('camera_matrix')
                    )
                    camera_meta["dist_coeff"] = np.array(
                        loadeddict.get('dist_coeff')
                    )
                except:
                    print(file_name, "not found")


                # Calculate the Camera Matrix from the yaml file
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

    def update_detected_markers(self):
        # Restructure the data so that we can prep for JSON Transfer
        # Iterate through each camera and their detected aruco markers
        print("Looking for detected Markers!")
        while True:
            # {
            #     1 (aruco id): {
            #         "rvec": np.array(3x,),
            #         "tvec": np.array(3x,)
            #     }
            # }
            # aruco_pose_dict = {}
            for v in self.active_video_streams:
                # TODO: Aggregate the aruco ids detected from each camera and
                # change the data structure to id->camera->rvec,tvec
                for aruco_id in v.detected_aruco_ids_dict.keys():
                    if aruco_id in self.aruco_pose_dict:
                        rvec_arr = v.detected_aruco_ids_dict[aruco_id]["rvec"]
                        tvec_arr = v.detected_aruco_ids_dict[aruco_id]["tvec"]
                        self.aruco_pose_dict[aruco_id].push(tvec_arr)
                        # self.aruco_pose_dict[aruco_id]["rvec"] = np.append(
                        #     rvec_arr, self.aruco_pose_dict[aruco_id]["rvec"]
                        # )
                        # self.aruco_pose_dict[aruco_id]["tvec"] = np.append(
                        #     tvec_arr, self.aruco_pose_dict[aruco_id]["tvec"]
                        # )
                    else:
                        self.aruco_pose_dict[aruco_id] = PoseQueue(
                            aruco_id,
                            v.detected_aruco_ids_dict[aruco_id]["tvec"]
                        )
                        # aruco_pose_dict[aruco_id] = (
                        #     v.detected_aruco_ids_dict[aruco_id]
                        # )
                        pass

            # self.aruco_pose_dict = aruco_pose_dict
            if self.aruco_pose_dict:
                print(self.aruco_pose_dict[0].get_expected_pose())
            time.sleep(0.1)

    def get_average_detected_markers(self):
        # Calculates the average of the detected markers and returns
        # a singular list for each aruco_id
        # Take the average across all aruco markers detected
        avg_aruco_poses_dict = {}
        for aruco_marker in self.aruco_pose_dict:
            vec_len = self.aruco_pose_dict[aruco_marker]['tvec'].shape[0]
            reshaped_rvec = (
                self.aruco_pose_dict[aruco_marker]['rvec'].reshape(
                    vec_len // 3, 3
                )
            )
            reshaped_tvec = (
                self.aruco_pose_dict[aruco_marker]['tvec'].reshape(
                    vec_len // 3, 3
                )
            )
            avg_aruco_poses_dict[aruco_marker] = {
                "rvec": np.mean(reshaped_rvec, axis=0),
                "tvec": np.mean(reshaped_tvec, axis=0)
            }
        return avg_aruco_poses_dict











# end
