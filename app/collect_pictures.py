from utils.VideoStreamWidget import VideoStreamWidget
from utils.MocapSystem import MocapSystem
import time
import os

# I'm taking pictures in every increment of 50 cm..
m = MocapSystem(4, False)
SAVE_PATH = "camera_world_calibration/images/camera_"

# Change this based on which img num you're capturing
img_num = 0
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
        time.sleep(0.1)
    return 0

def save_position(x, y, z, file):
    for v in m.active_video_streams:
        PATH = SAVE_PATH + str(v.id) + "/image_mappings.csv"
        with open(PATH, "a") as f:
            row = (file_name + "," +
                str(int(real_x)) + "," +
                str(int(real_y)) + "," +
                str(int(real_z)) + "\n"
            )
            f.write(row)
        f.close()

for real_z in [27, 100, 200]:
    for real_y in range(-200, 300, 100):
        for real_x in range (-300, 400, 100):
            print("(%d, %d, %d)" % (real_x, real_y, real_z))
            input("Press enter to start taking pictures")
            time.sleep(1)
            for i in range(0, 10):
                file_name = str(img_num) + ".jpg"
                save_images(file_name)
                save_position(real_x, real_y, real_z, file_name)
                img_num = img_num + 1
