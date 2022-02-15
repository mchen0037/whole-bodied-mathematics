import cv2
from cv2 import aruco

import csv
import time
import numpy as np

from utils.constants import constants as C

# Change this as we go through each camera
camera_id = 4

READ_PATH = "camera_world_calibration/images/camera_" + str(camera_id) + "/"
SAVE_PATH = "camera_world_calibration/camera_" + str(camera_id) + "_data.csv"
print(READ_PATH)

camera_meta = {}
camera_meta["mtx"] = C.CAMERA_CALIBRATION_MATRIX
camera_meta["dist_coeff"] = C.CAMERA_CALIBRATION_DISTANCE_COEFF

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
    # This clears the file and then regenerates the file
    with open(SAVE_PATH, "w") as f:
        f.write(
            "real_x, real_y, real_z, detected_x, detected_y, detected_z\n"
        )
    f.close()
    for idx, row in enumerate(reader):

        if idx == 0:
            continue

        print(READ_PATH + row[0])
        img_gray = cv2.imread(READ_PATH + row[0])

        # cv2.imshow("img", img_gray)

        corners, detected_aruco_ids, rejected_pts = aruco.detectMarkers(
            img_gray,
            C.ARUCO_DICT,
            parameters=C.ARUCO_PARAMS
        )

        if len(corners) != 0:
            rvecs, tvecs, _objPoints = aruco.estimatePoseSingleMarkers(
                corners,
                C.MARKER_LENGTH,
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
