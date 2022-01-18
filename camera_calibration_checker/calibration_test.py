import cv2
from cv2 import aruco
import yaml
import numpy as np
from pathlib import Path
from tqdm import tqdm

#Provide length of the marker's side
markerLength = 3.5  # Here, measurement unit is centimetre.

# Provide separation between markers
markerSeparation = 0.5   # Here, measurement unit is centimetre.

aruco_dict = aruco.getPredefinedDictionary( aruco.DICT_6X6_1000 )
arucoParams = aruco.DetectorParameters_create()
board = aruco.GridBoard_create(4, 5, markerLength, markerSeparation, aruco_dict)

camera = cv2.VideoCapture(0)
ret, img = camera.read()

with open('calibration_1.yaml') as f:
    loadeddict = yaml.load(f)
mtx_1 = loadeddict.get('camera_matrix')
dist_1 = loadeddict.get('dist_coeff')
mtx_1 = np.array(mtx)
dist_1 = np.array(dist)

img_gray = cv2.cvtColor(img,cv2.COLOR_RGB2GRAY)
h,  w = img_gray.shape[:2]
# camera matrix from the yaml file
newcameramtx, roi=cv2.getOptimalNewCameraMatrix(mtx,dist,(w,h),1,(w,h))

pose_r, pose_t = [], []
while True:
    ret, img = camera.read()
    img_aruco = img
    im_gray = cv2.cvtColor(img,cv2.COLOR_RGB2GRAY)
    h,  w = im_gray.shape[:2]
    # dst is undistorted image
    dst = cv2.undistort(im_gray, mtx, dist, None, newcameramtx)
    corners, ids, rejectedImgPoints = aruco.detectMarkers(dst, aruco_dict, parameters=arucoParams)
    #cv2.imshow("original", img_gray)
    if corners == None:
        print ("pass")
    else:
        ret, rvec, tvec = aruco.estimatePoseBoard(corners, ids, board, newcameramtx, dist, None, None) # For a board
        print ("Rotation\n", rvec)
        print ("Translation\n", tvec)
        if ret != 0:
            img_aruco = aruco.drawDetectedMarkers(dst, corners, ids, (0,255,0))
            img_aruco = aruco.drawAxis(dst, newcameramtx, dist, rvec, tvec, 10)    # axis length 100 can be changed according to your requirement

        if cv2.waitKey(0) & 0xFF == ord('q'):
            break;
    cv2.imshow("World co-ordinate frame axes", img_aruco)

cv2.destroyAllWindows()

# The end of the result, cv2.undistort is the image with straightened out fisheye
