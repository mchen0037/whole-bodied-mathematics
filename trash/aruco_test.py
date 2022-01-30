import cv2
import cv2.aruco as aruco
import numpy as np
import os

# vid = cv2.VideoCapture(2)
vid_2 = cv2.VideoCapture(2)
vid_4 = cv2.VideoCapture(4)
vid_6 = cv2.VideoCapture(6)
vid_8 = cv2.VideoCapture(7)

def midpoint(bboxs):
    return (np.mean(bboxs[:,0]), np.mean(bboxs[:,1]))

def findArucoMarkers(img, img_name, marker_size=6, total_markers=250, draw=True):
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # based on marker_size and total_markers on the given input
    key = getattr(aruco, f'DICT_{marker_size}X{marker_size}_{total_markers}')
    aruco_dict = aruco.Dictionary_get(key)

    aruco_param = aruco.DetectorParameters_create()
    bboxs, ids, rejected = aruco.detectMarkers(
        img_gray, aruco_dict, parameters=aruco_param
    )
    # bounding box

    # print(ids, bboxs)
    if draw:
        if ids is not None:
            for i, id in enumerate(ids):
                print(img_name, id, midpoint(bboxs[i]))
        aruco.drawDetectedMarkers(img, bboxs)
        cv2.imshow(img_name, img)

    return [bboxs, ids]


while(True):
    ret_2, frame_2 = vid_2.read()
    ret_4, frame_4 = vid_4.read()
    ret_6, frame_6 = vid_6.read()
    ret_8, frame_8 = vid_8.read()
    # frame = cv2.resize(frame, None, fx=0.4, fy=0.4)
    findArucoMarkers(frame_2, "frame_2")
    findArucoMarkers(frame_4, "frame_4")
    findArucoMarkers(frame_6, "frame_6")
    findArucoMarkers(frame_8, "frame_8")

    # the 'q' button is set as the
    # quitting button you may use any
    # desired button of your choice
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# After the loop release the cap object
vid.release()
# Destroy all the windows
cv2.destroyAllWindows()
