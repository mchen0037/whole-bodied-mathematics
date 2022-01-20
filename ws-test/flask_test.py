from flask import Flask
from VideoStreamWidget import VideoStreamWidget
import cv2, time

app = Flask(__name__)

# Initialize the cameras
NUMBER_OF_CAMERAS_IN_SYSTEM = 1
CAMERA_SRC_DICT = {}
for src in range(0, 200):
    cap = cv2.VideoCapture(src)
    test, frame = cap.read()
    if test:
        print("Source", src, "found.")
        cam = input("Which Camera number?  ")
        CAMERA_SRC_DICT[cam] = src

if len(CAMERA_SRC_DICT.keys()) != NUMBER_OF_CAMERAS_IN_SYSTEM:
    raise AssertionError("""
        Camera Sources and Number of Cameras in System mismatched!
    """)

active_video_streams = []
for key in CAMERA_SRC_DICT.keys():
    v = VideoStreamWidget(CAMERA_SRC_DICT[key])
    active_video_streams.append(v)

@app.route("/")
def hello_world():
    while True:
        try:
            for v in active_video_streams:
                v.show_frame()
        except AttributeError:
            pass
    return("hello world")


@app.teardown_appcontext
def teardown(exception):
    print(exception)

app.run()
