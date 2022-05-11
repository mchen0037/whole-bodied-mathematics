"""
    This is the mainFlask application which will run a web server to host
    the motion capture system and send pose data via a WebSocket to
    ws://localhost:5000/echo
"""

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
    """
        TODO: This function needs to be replaced by a client side application
        which displays the camera values based on ?id=#.
    """
    while True:
        try:
            for v in m.active_video_streams:
                v.show_frame()
        except AttributeError:
            pass
    return("hello world")

def get_client_value(camera_value, scale, translation, rounding_amount):
    """
        Uses the scaling and translation factors calculated in echo() and
        calculates the new, rounded value. scale, translation, and
        rounding_amount are calculated from the CLI inputs.

        Inputs:
            - camera_value <float>: The expected x, y, or z value, detected by
                the camera

            - scale <float>: The factor we need to multiply to the camera_value
                to convert a real position data to the projected space

            - translation <float>: The factor we need to add to the camera_value
                to convert a real position data to the projected space

            - rounding_amount <float>: The point which we want to round to. For
                example, 15.238 with a rounding_amount of 0.1 will round to 15.2

        Returns:
            - rounded_val <float>: The final x, y, or z value which will be sent
                to the client side.
    """
    val = scale * (camera_value - translation)
    rounded_val = round(val / rounding_amount) * rounding_amount
    return rounded_val

@sock.route("/echo")
def echo(sock):
    print("Connected!")
    # update these with student points from webcam
    data = {}
    prev = 0

    # Calculate final scaling and translation factors to the data,
    # based on the input parameters specified in CLI
    scale_x = (
        abs(m.bounds[0] - m.bounds[1]) /
        abs(C.DEFAULT_BOUNDS[0] - C.DEFAULT_BOUNDS[1])
    )
    scale_y = (
        abs(m.bounds[2] - m.bounds[3]) /
        abs(C.DEFAULT_BOUNDS[2] - C.DEFAULT_BOUNDS[3])
    )

    translate_x = m.origin[0]
    translate_y = m.origin[1]
    translate_z = m.origin[2]

    # send the data of the points over the websocket
    while True:
        # time.time() returns seconds
        time_elapsed = time.time() - prev

        if time_elapsed >= 1./C.MOCAP_OUT_FRAME_RATE:
            prev = time.time()
            sock.send(data)
            avg_aruco_poses_dict = m.get_average_detected_markers()

            if avg_aruco_poses_dict:
                for aruco_marker in avg_aruco_poses_dict:

                    # Calculate the final value before sending it to the client
                    rounded_x = get_client_value(
                        avg_aruco_poses_dict[aruco_marker][0],
                        scale_x,
                        translate_x,
                        m.rounding_amount
                    )
                    rounded_y = get_client_value(
                        avg_aruco_poses_dict[aruco_marker][1],
                        scale_y,
                        translate_y,
                        m.rounding_amount
                    )
                    rounded_z = get_client_value(
                        avg_aruco_poses_dict[aruco_marker][2],
                        scale_y,
                        translate_z,
                        m.rounding_amount
                    )

                    # Check to see if the aruco marker is already sent to the
                    # client before.
                    point_key = str(aruco_marker)
                    if point_key in list(data):
                        # If it is, update the value in the dictionary.
                        if m.mode == 0:
                            data[point_key]["x"] = rounded_x
                            data[point_key]["y"] = rounded_y
                        else:
                            data[point_key]["x"] = rounded_x
                            data[point_key]["y"] = rounded_z

                    else:
                        # If it is not, add it to the dictionary.
                        if m.mode == 0:
                            data[point_key] = {
                                "x": rounded_x,
                                "y": rounded_y
                            }
                        else:
                            data[point_key] = {
                                "x": rounded_x,
                                "y": rounded_z
                            }

@app.teardown_appcontext
def teardown(exception):
    print(exception)

if __name__ == "__main__":
    """
        Parse the input from the CLI to tweak settings for the Mocap System.

        Variables:
            - mode <string>: Should be "xy" or "xz", depending on how you want
                real positions should affect the projected graph. "xy" should be
                most cases, while "xz" will use real world height to project as
                the y-axis on the graph.

            - save_video <boolean>: Determines if the VideoStream data should be
                saved or not. This is a #FIXME, as my computer can't handle
                recording all four cameras at the same time, consistently

            - old_video_path <string>: DEPRICATED Was used to "replay" old data.
                This is on hold until I can save all four cameras in sync.

            - round_by <float>: Used to determine the precision of the values
                sent to the client. For example, 15.238 with a rounding_amount
                of 0.1 will round to 15.2.

            - bounds <list>: Used to describe the [min-x, max-x, min-y, max-y]
                values which will be projected on the graph. Default bounds are
                described in the Constants file.

    """
    mode = ""
    save_video = False
    old_video_path = ""
    round_by = 1.0
    bounds = []

    parser = argparse.ArgumentParser()
    parser.add_argument("mode", help="Mode can either be xy or xz")
    parser.add_argument("-s", "--save",
        help="Include if you want to save video and pose history",
        action="store_true"
    )
    parser.add_argument("-b", "--bounds",
        help="Describe bounds for the space using min_x, max_x, min_y, max_y",
        nargs="*"
    )
    parser.add_argument("-o", "--origin",
        help="Where you want to shift the origin in real life to",
        nargs="*"
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
    if args.bounds:
        if len(args.bounds) != 4:
            print("Need 4 inputs for --bounds [min-x, max-x, min-y, max-y]")
            sys.exit()
        else:
            args.bounds[0] = int(args.bounds[0])
            args.bounds[1] = int(args.bounds[1])
            args.bounds[2] = int(args.bounds[2])
            args.bounds[3] = int(args.bounds[3])

            if args.bounds[0] >= args.bounds[1]:
                print("Max X needs to be larger than Min X.")
                sys.exit()

            if args.bounds[2] >= args.bounds[3]:
                print("Max Y needs to be larger than Min Y.")
                sys.exit()

    if args.origin:
        if len(args.origin) != 3:
            print("Need 3 inputs for --origin [x, y, z]")
            sysm.exit()
        else:
            args.origin[0] = int(args.origin[0])
            args.origin[1] = int(args.origin[1])
            args.origin[2] = int(args.origin[2])

    bounds = args.bounds if args.bounds else C.DEFAULT_BOUNDS
    origin = args.origin if args.origin else C.DEFAULT_ORIGIN

    if old_video_path is not None:
        # This function is current depricated, since I have no way of recording
        # all four video streams at the same time.
        if os.path.exists(old_video_path + "1.avi"):
            print("This function is depcriated.")
            sys.exit()
            m = MocapSystem(
                NUMBER_OF_CAMERAS_IN_SYSTEM=C.NUM_CAMERAS,
                SAVE_VIDEO=False,
                MODE=mode,
                OLD_VIDEO_PATH=old_video_path,
                ROUNDING_AMOUNT=round_by,
                BOUNDS=bounds,
                ORIGIN=origin
            )
        else:
            print("This function is depcriated.")
            sys.exit()
            print(old_video_path + "1.avi not found.")
    else:
        print("Initiating Mocap System...")
        m = MocapSystem(
            NUMBER_OF_CAMERAS_IN_SYSTEM=C.NUM_CAMERAS,
            SAVE_VIDEO = save_video,
            # Give a 20 second buffer before start recording
            RECORD_START_TIME = (time.time() + 20),
            MODE=mode,
            ROUNDING_AMOUNT=round_by,
            BOUNDS=bounds,
            ORIGIN=origin
        )
    if m.save_video:
        print("NOTE: Saving video stream.")
    else:
        print("NOTE: Not Saving video stream.")
    app.run()
