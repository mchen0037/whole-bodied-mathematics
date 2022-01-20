import cv2
import yaml
import numpy as np
from VideoStreamWidget import VideoStreamWidget

class MocapSystem(object):
    def __init__(self, NUMBER_OF_CAMERAS_IN_SYSTEM):
        self.num_cameras = NUMBER_OF_CAMERAS_IN_SYSTEM
        self.camera_src_dict = {}
        for src in range(1, 200):
            cap = cv2.VideoCapture(src)
            test, frame = cap.read()
            if test:
                cam_meta_dict = {}
                print("cv2 Camera Source", src, "found.")
                cam = input("Which Camera number?  ")
                cam_meta_dict["src"] = int(cam)

                # Get the information from calibration matrices
                # Put the matrix in camera_src_dict
                file_name = "./camera_calibration_matrices/calibration_" + cam + ".yaml"
                try:
                    with open(file_name) as f:
                        loadeddict = yaml.load(f, Loader=yaml.FullLoader)
                    mtx_1 = np.array(loadeddict.get('camera_matrix'))
                    dist_1 = np.array(loadeddict.get('dist_coeff'))
                except:
                    print(file_name, "not found")

                self.camera_src_dict[cam] = cam_meta_dict

        if len(self.camera_src_dict.keys()) != self.num_cameras:
            raise AssertionError("""
                Camera Sources and Number of Cameras in System mismatched!
            """)

        self.active_video_streams = []
        for key in self.camera_src_dict.keys():
            v = VideoStreamWidget(self.camera_src_dict[key]["src"])
            self.active_video_streams.append(v)
