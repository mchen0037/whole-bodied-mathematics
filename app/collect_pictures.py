from utils.VideoStreamWidget import VideoStreamWidget
from utils.MocapSystem import MocapSystem
import time
import os

# I'm taking pictures in every increment of 50 cm..
m = MocapSystem(4, False)
SAVE_PATH = "camera_world_calibration/images/camera_"

# Change this based on which img num you're capturing
img_num = 97
# For new files:
# Need to create a file in collected_data_from_cameras/camera_<id>/image_mappings.csv
# for v in m.active_video_streams:
#     os.system("rm " + SAVE_PATH + str(v.id) + "/" + "image_mappings.csv")
#     f = open(SAVE_PATH + str(v.id) + "/" + "image_mappings.csv", "x")
#     f.write("file_name, real_x, real_y, real_z\n")
#     f.close()

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
    for v in m.active_video_streams:
        PATH = SAVE_PATH + str(v.id) + "/image_mappings.csv"
        with open(PATH, "a") as f:
            row = (file_name + "," +
                str(int(real_x) * 100) + "," +
                str(int(real_y) * 100) + "," +
                str(int(real_z) * 100) + "\n"
            )
            f.write(row)
        f.close()

while True:
    real_x = input("x: ")
    real_y = input("y: ")
    real_z = input("z: ")

    file_name = str(img_num) + ".jpg"
    save_images(file_name)
    save_position(real_x, real_y, real_z, file_name)

    img_num = img_num + 1
