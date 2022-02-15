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
        if time_elapsed >= 1./C.FRAME_RATE:
            prev = time.time()
            sock.send(data)
            avg_aruco_poses_dict = m.get_average_detected_markers()
            if avg_aruco_poses_dict:
                for aruco_marker in avg_aruco_poses_dict:
                    point_key = str(aruco_marker)
                    if point_key in data.keys():
                        if m.mode == 0:
                            data[point_key]["x"] = (
                                avg_aruco_poses_dict[aruco_marker][0]
                            )
                            data[point_key]["y"] = (
                                avg_aruco_poses_dict[aruco_marker][1]
                            )
                        else:
                            data[point_key]["x"] = (
                                avg_aruco_poses_dict[aruco_marker][0]
                            )
                            data[point_key]["y"] = (
                                avg_aruco_poses_dict[aruco_marker][2]
                            )

                    else:
                        if m.mode == 0:
                            data[point_key] = {
                                "x": avg_aruco_poses_dict[aruco_marker][0],
                                "y": avg_aruco_poses_dict[aruco_marker][1]
                            }
                        else:
                            data[point_key] = {
                                "x": avg_aruco_poses_dict[aruco_marker][0],
                                "y": avg_aruco_poses_dict[aruco_marker][2]
                            }

@app.teardown_appcontext
def teardown(exception):
    print(exception)

if __name__ == "__main__":
    mode = ""
    save_video = False
    old_video_path = ""

    parser = argparse.ArgumentParser()
    parser.add_argument("mode", help="Mode can either be xy or xz")
    parser.add_argument("-s", "--save",
        help="Include if you want to save video and pose history",
        action="store_true"
    )
    parser.add_argument("-p", "--path",
        help="Path to the old video you want to replay",
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

    if old_video_path is not None:
        if os.path.exists(old_video_path + "1.avi"):
            m = MocapSystem(
                NUMBER_OF_CAMERAS_IN_SYSTEM=4,
                SAVE_VIDEO = False,
                OLD_VIDEO_PATH = old_video_path
            )
        else:
            print(old_video_path + "1.avi not found.")
            sys.exit()
    else:
        m = MocapSystem(
            NUMBER_OF_CAMERAS_IN_SYSTEM=4,
            SAVE_VIDEO = save_video,
            MODE=mode
        )
    os.system('clear')
    if m.save_video:
        print("NOTE: Saving video stream.")
    else:
        print("NOTE: Not Saving video stream.")
    app.run()
