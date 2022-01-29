import cv2
from cv2 import aruco
import os
import csv
import time
import yaml
import numpy as np

MARKER_LENGTH = 18 # decimeters
ARUCO_DICT = aruco.getPredefinedDictionary(aruco.DICT_6X6_1000)
ARUCO_PARAMS = aruco.DetectorParameters_create()

# Change this as we go through each camera
camera_id = 3

READ_PATH = "callibration_transformation_data_images/camera_" + str(camera_id) + "/"

camera_meta = {}

calibration_yaml = "camera_calibration_matrices/calibration_2.yaml"

with open(calibration_yaml) as f:
    loadeddict = yaml.load(f, Loader=yaml.FullLoader)
camera_meta["mtx"] = np.array(
    loadeddict.get('camera_matrix')
)
camera_meta["dist_coeff"] = np.array(
    loadeddict.get('dist_coeff')
)

img_gray = cv2.imread(READ_PATH + "0.jpg")
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



def save_row(real_x, real_y, real_z, detected_x, detected_y, detected_z):
    fields = ["real_x", "real_y", "real_z", "detected_x", "detected_y", "detected_z"]
    SAVE_PATH = "camera_transformation_data/camera_" + str(camera_id) + "/data.csv"
    row = [real_x, real_y, real_z, detected_x, detected_y, detected_z]
    with open(SAVE_PATH, "a") as f:
        row = ( str(real_x) + "," +
            str(real_y) + "," +
            str(real_z) + "," +
            str(detected_x) + "," +
            str(detected_y) + "," +
            str(detected_z) + "\n"
        )
        f.write(row)
    f.close()

with open(READ_PATH + "image_mappings.csv") as csvfile:
    # file_name, real_x, real_y, real_z
    reader = csv.reader(csvfile, delimiter=",")
    for idx, row in enumerate(reader):

        if idx == 0:
            continue

        print(READ_PATH + row[0])
        img_gray = cv2.imread(READ_PATH + row[0])

        # cv2.imshow("img", img_gray)

        corners, detected_aruco_ids, rejected_pts = aruco.detectMarkers(
            img_gray,
            ARUCO_DICT,
            parameters=ARUCO_PARAMS
        )

        if len(corners) != 0:
            rvecs, tvecs, _objPoints = aruco.estimatePoseSingleMarkers(
                corners,
                MARKER_LENGTH,
                camera_meta["new_camera_mtx"],
                camera_meta["dist_coeff"],
                None,
                None
            )

            detected_x = tvecs[0][0][0]
            detected_y = tvecs[0][0][1]
            detected_z = tvecs[0][0][2]

            save_row(
                row[1],
                row[2],
                row[3],
                detected_x,
                detected_y,
                detected_z
            )
