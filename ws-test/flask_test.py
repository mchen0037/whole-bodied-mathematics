from flask import Flask
from MocapSystem import MocapSystem
from VideoStreamWidget import VideoStreamWidget
import cv2, time
import os

app = Flask(__name__)

@app.route("/")
def hello_world():
    while True:
        try:
            for v in m.active_video_streams:
                v.show_frame()
        except AttributeError:
            pass
    return("hello world")


@app.teardown_appcontext
def teardown(exception):
    print(exception)

m = MocapSystem(2)

os.system('clear')
app.run()
