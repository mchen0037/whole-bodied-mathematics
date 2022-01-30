from flask import Flask, render_template
from flask_sock import Sock
from flask import jsonify
import time
import random

import numpy as np
import cv2
from cv2 import aruco
import glob

import yaml

import threading

app = Flask(__name__)
sock = Sock(app)

img_dict = []
camera_aruco_pose_dict = {}
aruco_camera_pose_dict = {}

def update_pose_dicts():
    img_dict = get_camera_images(cameras)

    # Update the State of the camera images
    # get the camera images and esimate the positions of each
    # aruco marker based on the images
    # This giant for loop updates aruco_camera_pose_dict

    for key in img_dict:
        image = img_dict[key]["dst"]
        newcameramtx = img_dict[key]["newcameramtx"]
        dist = img_dict[key]["dist"]
        ret = img_dict[key]["ret"]
        # detect any aruco markers in the image
        corners, detected_aruco_ids, rejectedImgPoints = aruco.detectMarkers(
            image, aruco_dict, parameters=arucoParams
        )
        if len(corners) == 0:
            # print("pass")
            pass
        else:
            # estimate the position of aruco markers in the image frame
            # https://docs.opencv.org/4.5.3/d9/d6a/group__aruco.html#ga84dd2e88f3e8c3255eb78e0f79571bd1
            # this returns a list of rotation vectors and a list of translation vectors of where each id is located.

            rvecs, tvecs, _objPoints = aruco.estimatePoseSingleMarkers(
                corners,
                markerLength,
                newcameramtx,
                dist,
                None,
                None
            )

            # ret
            if ret != 0:
                if detected_aruco_ids is not None:
                    # draw the detected markers (squares) around each aruco marker
                    image = aruco.drawDetectedMarkers(
                        image,
                        corners,
                        detected_aruco_ids,
                        (0,255,0)
                    )
                    # go through each detected aruco marker and draw the axis and
                    # put the data in a dictionary, prepped for JSON transfer
                    marker_id_pose_dict = {}

                    for i, aruco_id in enumerate(detected_aruco_ids):
                        if aruco_id[0] in marker_id_pose_dict.keys():
                            marker_id_pose_dict[aruco_id[0]]["tvec"] = tvecs[i].tolist()
                            marker_id_pose_dict[aruco_id[0]]["rvec"] = rvecs[i].tolist()
                        else:
                            rvec_world, tvec_world = transform_to_world(
                                key,rvecs[i][0],tvecs[i][0]
                            )
                            marker_id_pose_dict[aruco_id[0]] = {
                                "rvec": rvec_world,
                                "tvec": tvec_world
                            }
                    # if key not in camera_aruco_pose_list.keys():
                    camera_aruco_pose_dict[key] = marker_id_pose_dict
        # Rearrange the dictionary so that aruco markers take priority
        aruco_camera_pose_dict = get_aruco_camera_poses(camera_aruco_pose_dict)
        # print(aruco_camera_pose_dict)
        # print(aruco_camera_pose_dict)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        # show the image
        cv2.imshow("img_dict" + str(key),image)

    #  left off here
    # Calculate the average rvec and tvec of each aruco marker, from each camera.
    for aruco_marker in aruco_camera_pose_dict:
        vec_len = aruco_camera_pose_dict[aruco_marker]['tvec'].shape[0]
        reshaped_tvec = aruco_camera_pose_dict[aruco_marker]['tvec'].reshape(vec_len//3, 3)
        reshaped_rvec = aruco_camera_pose_dict[aruco_marker]['rvec'].reshape(vec_len//3, 3)
        aruco_camera_pose_dict[aruco_marker]['rvec'] = np.mean(reshaped_rvec, axis=0)
        aruco_camera_pose_dict[aruco_marker]['tvec'] = np.mean(reshaped_tvec, axis=0)



@app.before_first_request
def state_thread():
    def run_state():
        global img_dict
        global camera_aruco_pose_dict
        global aruco_camera_pose_dict
        while True:
            update_pose_dicts()

    thread_state = threading.Thread(target=run_state)
    thread_state.start()

# Provide length of the marker's side (cm)
# TODO: When you print out large ones for people to put on their shirt
# you need to change this
markerLength = 3.5

# Load Aruco
aruco_dict = aruco.getPredefinedDictionary( aruco.DICT_6X6_1000 )
arucoParams = aruco.DetectorParameters_create()


camera_1 = cv2.VideoCapture(0)
camera_2 = cv2.VideoCapture(4)

with open('camera_calibration_matrices/calibration_1.yaml') as f:
    loadeddict = yaml.load(f, Loader=yaml.FullLoader)
mtx_1 = loadeddict.get('camera_matrix')
dist_1 = loadeddict.get('dist_coeff')
mtx_1 = np.array(mtx_1)
dist_1 = np.array(dist_1)

with open('camera_calibration_matrices/calibration_2.yaml') as f:
    loadeddict = yaml.load(f,Loader=yaml.FullLoader)
mtx_2 = loadeddict.get('camera_matrix')
dist_2 = loadeddict.get('dist_coeff')
mtx_2 = np.array(mtx_2)
dist_2 = np.array(dist_2)

ret_2, img_1 = camera_1.read()
ret_2, img_2 = camera_2.read()

# turn image to grayscale
img_gray_1 = cv2.cvtColor(img_1,cv2.COLOR_RGB2GRAY)
h_1,  w_1 = img_gray_1.shape[:2]

img_gray_2 = cv2.cvtColor(img_2,cv2.COLOR_RGB2GRAY)
h_2,  w_2 = img_gray_2.shape[:2]

# camera matrix from the yaml file
newcameramtx_1, roi=cv2.getOptimalNewCameraMatrix(mtx_1,dist_1,(w_1,h_1),1,(w_1,h_1))
newcameramtx_2, roi=cv2.getOptimalNewCameraMatrix(mtx_2,dist_2,(w_2,h_2),1,(w_2,h_2))

# Update this for the amount of cameras that you have.
cameras = [
    # {
    #     "id": 1,
    #     "data": camera_1,
    #     "mtx": mtx_1,
    #     "dist": dist_1,
    #     "newcameramtx": newcameramtx_1
    # },
    {
        "id": 2,
        "data": camera_2,
        "mtx": mtx_2,
        "dist": dist_2,
        "newcameramtx": newcameramtx_2
    },
]

def get_camera_images(cameras):
    grayscale_undistorted_images_dict = {}
    for camera_dict in cameras:
        mtx = camera_dict["mtx"]
        dist = camera_dict["dist"]
        newcameramtx = camera_dict["newcameramtx"]
        camera = camera_dict["data"]
        # ret is a boolean value which tells me if the frame is read correctly
        ret, img = camera.read()
        img_gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        # undistort the image
        dst = cv2.undistort(img_gray, mtx, dist, None, newcameramtx)
        d = {
            "dst": dst,
            "newcameramtx": newcameramtx,
            "dist": dist,
            "ret": ret
        }
        grayscale_undistorted_images_dict[camera_dict["id"]] = d
    return grayscale_undistorted_images_dict

def transform_to_world(camera_id, rvec, tvec):
    # TODO: Take in current rvec, tvec of camera, and camera_id
    # and apply the appropriate matrix multiplication.
    # then, return the rvec, tvec of the marker in the world.
    # Extrinsic Matrix is the matrix we will multiply to get to world coord
    # 1. Repeat 20 [
    #   Take a few pictures with aruco marker on a box
    #   Run detection on these pictures (run the detection later)
    #   measure world coord (in ref to X)
    #   Create a mapping between the pictures and the world coord
    #   image_1: [0, 2, 3], (x, y, z)
        #   ignore rotation for now. (don't need it for calibration)
        #   we solve for the rotation of the camera by solving this set of linear equations
    # ]
    # 2. Feed mappings into Posegraph
    if camera_id == 1:
        # Camera Matrices are calculated through test_icp.jl
        CAM_1_MAT = np.array([
            0.10843942862049338, 0.9831140893315748, -0.1474027736449005, -255.61978107664206,
            -0.899344321905764, 0.03383852478766258, -0.4359297476613141, 46.022855915803895,
            -0.4235807844748427, 0.17983782026577055, 0.8878275043192422, 17.80489732664515,
            0.0, 0.0, 0.0, 1.0]
        ).reshape(4,4)
        CAM_1_ROT_MAT = CAM_1_MAT[:,0:3][0:3]
        CAM_1_TRA_MAT = CAM_1_MAT[:,3][0:3]
        new_tvec = CAM_1_ROT_MAT @ tvec + CAM_1_TRA_MAT
    elif camera_id == 2:
        pass
    elif camera_id == 3:
        pass
    elif camera_id == 4:
        pass
    return rvec, tvec

def get_aruco_camera_poses(camera_aruco_pose_dict):
    # Restructures the data structure.
    # Iterate through each camera and find the aruco markers detected by them
    # Group by the aruco_ids and append each rvec detected by the camera
    aruco_camera_pose_dict = {}
    for camera_key in camera_aruco_pose_dict:
        #
        for aruco_marker_key in camera_aruco_pose_dict[camera_key]:
            aruco_marker_data = camera_aruco_pose_dict[camera_key][aruco_marker_key]
            # If the aruco marker is already detected, update the existing dictionary
            # Else, assign a new dictionary to the dictionary.
            if aruco_marker_key in aruco_camera_pose_dict.keys():
                rvec_arr = aruco_camera_pose_dict[aruco_marker_key]['rvec']
                tvec_arr = aruco_camera_pose_dict[aruco_marker_key]['tvec']
                aruco_camera_pose_dict[aruco_marker_key]['rvec'] = np.append(
                    rvec_arr, aruco_marker_data['rvec']
                )
                aruco_camera_pose_dict[aruco_marker_key]['tvec'] = np.append(
                    tvec_arr, aruco_marker_data['tvec']
                )

            else:
                aruco_camera_pose_dict[aruco_marker_key] = aruco_marker_data
    return aruco_camera_pose_dict

@sock.route("/echo")
def echo(sock):
    # update these with student points from webcam
    p_0 = {"x":0,"y":0}
    p_1 = {"x":1,"y":1}
    p_2 = {"x":2,"y":2}
    p_3 = {"x":3,"y":3}
    # p_4 = {"x":4,"y":4}
    l = [p_0, p_1, p_2, p_3]
    data = {"P_2": p_2}
    global aruco_camera_pose_dict
    # print(data)
    # res = jsonify([1, 2, 3, 4, 5])
    while True:
        # send the data of the points over the websocket
        sock.send(data)

        if aruco_camera_pose_dict:
            for aruco_marker in aruco_camera_pose_dict:
                point_key = "P_" + str(aruco_marker)
                if point_key in data.keys():
                    data[point_key]["x"] = aruco_camera_pose_dict[aruco_marker]["tvec"][0]
                    data[point_key]["y"] = aruco_camera_pose_dict[aruco_marker]["tvec"][1]
                else:
                    data[point_key] = {
                        "x": aruco_camera_pose_dict[aruco_marker]["tvec"][0],
                        "y": aruco_camera_pose_dict[aruco_marker]["tvec"][1]
                    }

        time.sleep(0.1)

app.run()
