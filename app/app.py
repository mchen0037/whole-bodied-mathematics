import os
import time
import json

import cv2

from flask import Flask
from flask_sock import Sock

from utils.MocapSystem import MocapSystem
from utils.VideoStreamWidget import VideoStreamWidget

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
    # print(data)
    # res = jsonify([1, 2, 3, 4, 5])
    while True:
        # send the data of the points over the websocket
        # print(data)
        sock.send(data)

        avg_aruco_poses_dict = m.get_average_detected_markers()
        if avg_aruco_poses_dict:
            for aruco_marker in avg_aruco_poses_dict:
                point_key = str(aruco_marker)
                if point_key in data.keys():
                    data[point_key]["x"] = (
                        avg_aruco_poses_dict[aruco_marker][0]
                    )
                    data[point_key]["y"] = (
                        avg_aruco_poses_dict[aruco_marker][1]
                    )
                else:
                    data[point_key] = {
                        "x": avg_aruco_poses_dict[aruco_marker][0],
                        "y": avg_aruco_poses_dict[aruco_marker][1]
                    }
        # print(data)
        # {
        #     '2': {'x': 2, 'y': 2},
        #     '3': {'x': -61.92587027200489, 'y': 141.64982423922115},
        #     '4': {'x': -112.89539842713651, 'y': 108.76427080426924}
        # }


        time.sleep(0.1)



@app.teardown_appcontext
def teardown(exception):
    print(exception)

if __name__ == "__main__":
    m = MocapSystem(
        NUMBER_OF_CAMERAS_IN_SYSTEM=4,
        SAVE_VIDEO = False,
        OLD_VIDEO_PATH = "collected_data_from_cameras/video/2022_2_10/2022_2_10_15_23_camera_"
    )
    # os.system('clear')
    app.run()
