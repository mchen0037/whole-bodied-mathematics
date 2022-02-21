import os
import time
import json
import argparse
import sys


from flask import Flask
from flask_sock import Sock

import random

app = Flask(__name__)
sock = Sock(app)


@sock.route("/echo")
def echo(sock):
    print("Connected!")
    # update these with student points from webcam
    data = {
        "0": {
            "x": random.randint(-300,300),
            "y": random.randint(-300,300)
        },
        "1": {
            "x": random.randint(-300,300),
            "y": random.randint(-300,300)
        }
    }
    prev = 0
    while True:
        # send the data of the points over the websocket
        # print(data)
        time_elapsed = time.time() - prev # time.time() returns seconds
        if time_elapsed >= 1./10:
            prev = time.time()
            sock.send(data)
            data = {
                "0": {
                    "x": data["0"]["x"] + 10 * random.random() - 5,
                    "y": data["0"]["y"] + 10 * random.random() - 5
                },
                "1": {
                    "x": data["1"]["x"] + 10 * random.random() - 5,
                    "y": data["1"]["y"] + 10 * random.random() - 5
                }
            }



if __name__ == "__main__":
    app.run()
