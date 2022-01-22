import cv2
from cv2 import aruco
import yaml
import numpy as np
from VideoStreamWidget import VideoStreamWidget

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
        self.camera_id_meta_dict = {}

        # This for loop iterates over 200 cv2 Video Capture Sources
        # Doing this because the webcams aren't correlating with what's in
        # /dev/video/*. The Camera number corresponds to the camera id
        # based on my setup. It's just used for calibration and transformation.
        for src in range(1, 200):
            cap = cv2.VideoCapture(src)
            test, frame = cap.read()
            if test:
                camera_meta = {}
                print("cv2 Camera Source", src, "found.")
                cam = input("Which Camera number?  ")
                camera_meta["src"] = src

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
                self.camera_id_meta_dict[cam] = camera_meta

        # After finding all camera matrices, make sure we assert that we have
        # the same amount of real cameras and sources.
        if len(self.camera_id_meta_dict.keys()) != self.num_cameras:
            raise AssertionError("""
                Camera Sources and Number of Cameras in System mismatched!
            """)

        # All video streams will be appended in a list held in this Class
        self.active_video_streams = []
        for key in self.camera_id_meta_dict.keys():
            v = VideoStreamWidget(key, self.camera_id_meta_dict[key])
            self.active_video_streams.append(v)
