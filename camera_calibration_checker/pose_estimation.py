import numpy as np
import cv2
from cv2 import aruco
import glob

import yaml

# Provide length of the marker's side (cm)
# TODO: When you print out large ones for people to put on their shirt
# you need to change this
markerLength = 3.5

# Load Aruco
aruco_dict = aruco.getPredefinedDictionary( aruco.DICT_6X6_1000 )
arucoParams = aruco.DetectorParameters_create()

camera = cv2.VideoCapture(4)
ret, img = camera.read()

# load calibration files
with open('calibration.yaml') as f:
    loadeddict = yaml.load(f)
mtx = loadeddict.get('camera_matrix')
dist = loadeddict.get('dist_coeff')
mtx = np.array(mtx)
dist = np.array(dist)

# turn image to grayscale
img_gray = cv2.cvtColor(img,cv2.COLOR_RGB2GRAY)
h,  w = img_gray.shape[:2]

# camera matrix from the yaml file
newcameramtx, roi=cv2.getOptimalNewCameraMatrix(mtx,dist,(w,h),1,(w,h))

while True:
    ret, img = camera.read()
    img_gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    h, w = img_gray.shape[:2]

    # undistort the image
    dst = cv2.undistort(img_gray, mtx, dist, None, newcameramtx)
    img_aruco = dst
    # detect any aruco markers in the image
    corners, ids, rejectedImgPoints = aruco.detectMarkers(
        dst, aruco_dict, parameters=arucoParams
    )
    # print(corners)

    if corners == None:
        print("pass")
    else:
        # estimate the position of aruco markers in the image frame
        # https://docs.opencv.org/4.5.3/d9/d6a/group__aruco.html#ga84dd2e88f3e8c3255eb78e0f79571bd1
        # this returns a list of rotation vectors and a list of translation vectors of where each id is located.
        rvecs, tvecs, _objPoints = aruco.estimatePoseSingleMarkers(corners, markerLength, newcameramtx, dist, None, None)
        id_pose_dict = {}
        if ret != 0:
            if ids is not None:
                # go through each detected aruco marker and draw the axis and
                # put the data in a dictionary, prepped for JSON transfer
                for i, id in enumerate(ids):
                    id_pose_dict[id[0]] = {"rvec": rvecs[i], "tvec": tvecs[i]}
                    img_aruco = aruco.drawAxis(dst, newcameramtx, dist, rvecs[i], tvecs[i], 3)
                    print("rvec", rvecs[i])
                    print("tvec", tvecs[i])
            # draw the detected markers (squares) around each aruco marker
            img_aruco = aruco.drawDetectedMarkers(dst, corners, ids, (0,255,0))

            # if any aruco markers are detected, print out
            # a dictionary of their locations (for debugging)

            if id_pose_dict:
                # print(id_pose_dict)
                pass
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    # show the image
    cv2.imshow('img_aruco',img_aruco)
