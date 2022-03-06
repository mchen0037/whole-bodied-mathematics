import os
import time
import json
import argparse
import sys

import cv2

from flask import Flask
from flask_sock import Sock

from utils.MocapSystem import MocapSystem
from utils.VideoStreamWidget import VideoStreamWidget
from utils.constants import constants as C

app = Flask(__name__)
sock = Sock(app)

@app.route("/show_frames")
def hello_world():
    while True:
        try:
            for v in m.active_video_streams:
                v.show_frame()
        except AttributeError:
            pass
    return("hello world")

@sock.route("/echo")
def echo(sock):
    print("Connected!")
    # update these with student points from webcam
    data = {}
    prev = 0
    while True:
        # send the data of the points over the websocket
        # print(data)
        time_elapsed = time.time() - prev # time.time() returns seconds
        if time_elapsed >= 1./C.MOCAP_OUT_FRAME_RATE:
            prev = time.time()
            sock.send(data)
            avg_aruco_poses_dict = m.get_average_detected_markers()
            if avg_aruco_poses_dict:
                for aruco_marker in avg_aruco_poses_dict:
                    if avg_aruco_poses_dict[aruco_marker] is not None:
                        point_key = str(aruco_marker)
                        rounded_x = (
                            round(
                                avg_aruco_poses_dict[aruco_marker][0] / m.rounding_amount
                            ) * m.rounding_amount
                        )
                        rounded_y = (
                            round(
                                avg_aruco_poses_dict[aruco_marker][1] / m.rounding_amount
                            ) * m.rounding_amount
                        )
                        rounded_z = (
                            round(
                                avg_aruco_poses_dict[aruco_marker][2] / m.rounding_amount
                            ) * m.rounding_amount
                        )
                        if point_key in list(data):
                            if m.mode == 0:
                                data[point_key]["x"] = rounded_x
                                data[point_key]["y"] = rounded_y
                            else:
                                data[point_key]["x"] = rounded_x
                                data[point_key]["y"] = rounded_z

                        else:
                            if m.mode == 0:
                                print("send xy")
                                data[point_key] = {
                                    "x": rounded_x,
                                    "y": rounded_y
                                }
                            else:
                                print("send xz")
                                data[point_key] = {
                                    "x": rounded_x,
                                    "y": rounded_z
                                }
                    else:
                        data[point_key]["x"] = -9999
                        data[point_key]["y"] = -9999

@app.teardown_appcontext
def teardown(exception):
    print(exception)

if __name__ == "__main__":
    mode = ""
    save_video = False
    old_video_path = ""
    round_by = 10

    parser = argparse.ArgumentParser()
    parser.add_argument("mode", help="Mode can either be xy or xz")
    parser.add_argument("-s", "--save",
        help="Include if you want to save video and pose history",
        action="store_true"
    )
    parser.add_argument("-p", "--path",
        help="Path to the old video you want to replay",
    )
    parser.add_argument("-r", "--round",
        help="Increment you want to round by (default 10)",
    )
    args = parser.parse_args()
    if args.mode == "xy":
        mode = 0
    elif args.mode == "xz":
        mode = 1
    else:
        print("invalid input for mode")
        sys.exit()
    save_video = args.save
    old_video_path = args.path

    round_by = float(args.round) if args.round else round_by

    if old_video_path is not None:
        # This function is current depricated, since I have no way of recording
        # all four video streams at the same time.
        if os.path.exists(old_video_path + "1.avi"):
            m = MocapSystem(
                NUMBER_OF_CAMERAS_IN_SYSTEM=C.NUM_CAMERAS,
                SAVE_VIDEO = False,
                MODE=mode,
                OLD_VIDEO_PATH = old_video_path,
                ROUNDING_AMOUNT=round_by,
            )
        else:
            print(old_video_path + "1.avi not found.")
            sys.exit()
    else:
        m = MocapSystem(
            NUMBER_OF_CAMERAS_IN_SYSTEM=C.NUM_CAMERAS,
            SAVE_VIDEO = save_video,
            # Give a 20 second buffer before start recording
            RECORD_START_TIME = (time.time() + 20),
            MODE=mode,
            ROUNDING_AMOUNT=round_by
        )
    if m.save_video:
        print("NOTE: Saving video stream.")
    else:
        print("NOTE: Not Saving video stream.")
    app.run()
