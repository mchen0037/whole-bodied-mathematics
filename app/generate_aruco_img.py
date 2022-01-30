import cv2
from cv2 import aruco
import time
from utils.constants import constants as C

SIDE_PIXELS = 600

for id in range(0, 10):
    file_name = "aruco_img/" + str(SIDE_PIXELS) + "_" + str(id) + ".jpg"
    img = aruco.drawMarker(C.ARUCO_DICT, id, SIDE_PIXELS)
    cv2.imwrite(file_name, img)
