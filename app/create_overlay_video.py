"""
This file is depricated for now because the camera videos do not sync up with
each other. If there is a way to make sure everything is synced up correctly,
I can use this script again. 2022/04/20
"""

import cv2
from utils.constants import constants as C
import time

DATA_FILE_PATH = "/media/mighty/research-1/collected_data_from_cameras"
DATE = "2022_2_17/2022_2_17_14_57_"
video_file_name = "test.avi"

screen_capture = cv2.VideoCapture("%s/screen/%sscreen.avi" % (DATA_FILE_PATH, DATE))
video_captures_list = []

for i in range(1,C.NUM_CAMERAS + 1):
    vc = cv2.VideoCapture("%s/video/%scamera_%s.avi" % (DATA_FILE_PATH, DATE, i))
    video_captures_list.append(vc)

video_writer = cv2.VideoWriter(video_file_name,
    cv2.VideoWriter_fourcc(*'MJPG'),
    C.CAMERA_FRAME_RATE,
    C.SCREEN_CAPTURE_SIZE
)

while True:
    ret, background = screen_capture.read()

    num_sources = len(video_captures_list)
    padding = 50 #50px

    bg_h = background.shape[0]
    bg_w = background.shape[1]

    f_w = C.CAMERA_FRAME_SIZE[0]
    f_h = C.CAMERA_FRAME_SIZE[1]

    scale = 0.55

    f_w_resize = int(f_w * scale)
    f_h_resize = int(f_h * scale)

    spacing = int((bg_w - (num_sources * f_w_resize)) / (num_sources + 1))

    for idx, vc in enumerate(video_captures_list):
        ret_2, foreground = vc.read()
        if ret_2:
            foreground = cv2.resize(foreground, (0,0), fx=scale, fy=scale)
            background[bg_h - f_h_resize - padding : bg_h - padding, bg_w - f_w_resize - (spacing * (idx + 1)) - (f_w_resize * idx) : bg_w - (spacing * (idx + 1)) - (f_w_resize * idx),:] = foreground

    video_writer.write(background)
