# Collects images from all cameras at the same time so that we can collect data
# a bit faster

import cv2
from cv2 import aruco
from VideoStreamWidget import VideoStreamWidget
from MocapSystem import MocapSystem
import time

import csv

# I'm taking pictures in every increment of 50 cm..
m = MocapSystem(4)
SAVE_PATH = "callibration_transformation_data_images/camera_"

def save_images(file_name):
    while True:
        res = 0
        for v in m.active_video_streams:
            PATH = SAVE_PATH + str(v.id) + "/" + file_name
            res = res + v.save_image(PATH, "GRAY")
        if res == 4:
            return 1
        time.sleep(0.25)
    return 0

def save_position(x, y, z, file):
    fields = ["file_name", "real_x", "real_y", "real_z"]
    for v in m.active_video_streams:
        PATH = SAVE_PATH + str(v.id) + "/image_mappings.csv"
        with open(PATH, "a") as f:
            row = (file_name + "," +
                str(real_x) + "," +
                str(real_y) + "," +
                str(real_z) + "\n"
            )
            f.write(row)
        f.close()


img_num = 156
while True:
    real_x = input("x: ")
    real_y = input("y: ")
    real_z = input("z: ")

    file_name = str(img_num) + ".jpg"
    save_images(file_name)
    save_position(real_x, real_y, real_z, file_name)

    img_num = img_num + 1
