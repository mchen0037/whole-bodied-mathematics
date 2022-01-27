from flask import Flask
from MocapSystem import MocapSystem
from VideoStreamWidget import VideoStreamWidget
from flask_sock import Sock
import cv2, time
import os
import json

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
    p_0 = {"x":0,"y":0}
    p_1 = {"x":1,"y":1}
    p_2 = {"x":2,"y":2}
    p_3 = {"x":3,"y":3}
    # p_4 = {"x":4,"y":4}
    l = [p_0, p_1, p_2, p_3]
    data = {"P_2": p_2}
    # print(data)
    # res = jsonify([1, 2, 3, 4, 5])
    while True:
        # send the data of the points over the websocket
        sock.send(data)

        avg_aruco_poses_dict = m.get_average_detected_markers()
        if avg_aruco_poses_dict:
            for aruco_marker in avg_aruco_poses_dict:
                point_key = "P_{" + str(aruco_marker) + "}"
                if point_key in data.keys():
                    data[point_key]["x"] = (
                        avg_aruco_poses_dict[aruco_marker]["tvec"][0]
                    )
                    data[point_key]["y"] = (
                        avg_aruco_poses_dict[aruco_marker]["tvec"][1]
                    )
                else:
                    data[point_key] = {
                        "x": avg_aruco_poses_dict[aruco_marker]["tvec"][0],
                        "y": avg_aruco_poses_dict[aruco_marker]["tvec"][1]
                    }

        time.sleep(0.1)



@app.teardown_appcontext
def teardown(exception):
    print(exception)

if __name__ == "__main__":
    m = MocapSystem(3)
    # os.system('clear')
    app.run()
