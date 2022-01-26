from threading import Thread

import cv2
import time
from cv2 import aruco

MARKER_LENGTH = 3.5
ARUCO_DICT = aruco.getPredefinedDictionary(aruco.DICT_6X6_1000)
ARUCO_PARAMS = aruco.DetectorParameters_create()

class VideoStreamWidget(object):
    def __init__ (self, id, camera_meta):
        self.id = id
        # {
        #     "src": int, the cv2.VideoCapture(#)
        #     "mtx": np.array, the camera matrix to undistort the image
        #     "dist_coeff": np.array, the distance coeffs to undistort the image
        #     "new_camera_mtx": np.array, the new camera matrix to undistort img
        # }
        self.camera_meta = camera_meta # meta info (see MocapSystem)
        self.src = camera_meta["src"] # cv2 camera source id
        self.capture = cv2.VideoCapture(self.src)
        self.status = None # Status of the camera
        self.use_roi = True # roi = Region of Interest
        self.img_raw = None # save for data collection
        self.img_gray = None # img_gray is undistorted
        self.undistorted_img = None # If use_roi is True, crop the img
        self.img_with_aruco = None

        # {
        #     1: { # these are the aruco id value
        #        "camera_id": int the camera_id
        #        "rvec": np.array(3,1) # rotation vector
        #        "tvec": np.array(3,1) # translation vector
        #     }
        # }
        self.detected_aruco_ids_dict = {}

        self.thread = Thread(target=self.update, args=())
        self.thread.daemon = True
        self.thread.start()

    def transform_to_world(self, rvec, tvec):
        # TODO: These should also be moved to an external file.
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
        # TODO: Refactor this to work into files as well, rather than hard-coding it in here.
        # TODO: cameras 2, 3, 4.
        #   Camera 2 and 3 have data collected already, 4 needs measurements
        CAM_MAT = None
        if self.id == 1:
            # Camera Matrices are calculated through test_icp.jl
            CAM_MAT = np.array([
                0.10843942862049338, 0.9831140893315748, -0.1474027736449005, -255.61978107664206,
                -0.899344321905764, 0.03383852478766258, -0.4359297476613141, 46.022855915803895,
                -0.4235807844748427, 0.17983782026577055, 0.8878275043192422, 17.80489732664515,
                0.0, 0.0, 0.0, 1.0]
            ).reshape(4,4)
        elif self.id == 2:
            CAM_MAT = np.array([
                -0.7864529749809144, 0.5746331416772751, 0.2264695799213973, -70.99146586565733,
                0.0820968809519782, 0.4606632412057913, -0.883770038154571, 90.74124962311619,
                -0.6121697642661112, -0.6764511295636071, -0.40946556513398547, 102.83877695747266,
                0.0, 0.0, 0.0, 1.0]
            ).reshape(4,4)
        elif self.id == 3:
            CAM_MAT = np.array([
                -0.9638100398727747, 0.26432766377635747, 0.03465679158510404, 72.76692121846743,
                -0.09259124459007201, -0.20999944619257938, -0.9733072968102474, 98.58049098021205,
                -0.24999413686265098, -0.9412922600135107, 0.22687400197676955, 74.28570741386422,
                0.0, 0.0, 0.0, 1.0]
            ).reshape(4,4)
        elif self.id == 4:
            pass
            
        CAM_ROT_MAT = CAM_MAT[:,0:3][0:3]
        CAM_TRA_MAT = CAM_MAT[:,3][0:3]
        new_tvec = CAM_ROT_MAT @ tvec + CAM_TRA_MAT
        return rvec, new_tvec

    def update(self, keep_old_values=False):
        while True:
            # Reinitialize as an empty dictionary so that we can clear any old
            # data in case the marker is no longer detected.
            # This could be an interesting idea to study to see if it makes
            # pedagogical differences
            marker_id_pose_dict = {}

            if self.capture.isOpened():
                self.status, self.img_raw = self.capture.read()
                self.undistorted_img = cv2.undistort(
                    self.img_raw,
                    self.camera_meta["mtx"],
                    self.camera_meta["dist_coeff"],
                    None,
                    self.camera_meta["new_camera_mtx"]
                )
                if self.use_roi == True:
                    x, y, w, h = self.camera_meta['roi']
                    self.undistorted_img = self.undistorted_img[y:y+h, x:x+w]
                self.img_gray = cv2.cvtColor(
                    self.undistorted_img, cv2.COLOR_RGB2GRAY
                )
                # Detect any AruCo Markers
                corners, detected_aruco_ids, rejected_pts = aruco.detectMarkers(
                    self.img_gray,
                    ARUCO_DICT,
                    parameters=ARUCO_PARAMS
                )
                if len(corners) != 0:
                    # estimate the position of aruco markers in the image frame
                    # https://docs.opencv.org/4.5.3/d9/d6a/group__aruco.html#ga84dd2e88f3e8c3255eb78e0f79571bd1
                    # this returns a list of rotation vectors and a list of translation vectors of where each id is located.
                    rvecs, tvecs, _objPoints = aruco.estimatePoseSingleMarkers(
                        corners,
                        MARKER_LENGTH,
                        self.camera_meta["new_camera_mtx"],
                        self.camera_meta["dist_coeff"],
                        None,
                        None
                    )
                    # If frame is read correctly and we have detected some ids
                    if self.status != 0 and detected_aruco_ids is not None:
                        # Draw the markers onto the image (axis on image)
                        self.undistorted_img = aruco.drawDetectedMarkers(
                            self.undistorted_img,
                            corners,
                            detected_aruco_ids,
                            (0,255,0)
                        )

                        # Go through the detected aruco_ids and assign their
                        # rvec, tvec as a dictionary.
                        # Save that dictionary as a class variable so that
                        # MocapSystem can aggregate across all VideoStreams
                        # to prep for JSON Transfer
                        for i, aruco_id in enumerate(detected_aruco_ids):
                            # Putting [0] here assumes that we only have one
                            # of each aruco marker. For my classroom, this
                            # should be a safe assumption to make.
                            # i.e. we should see at most 1 unique aruco id
                            # per camera.
                            rvec_world, tvec_world = self.transform_to_world(
                                rvecs[i][0],
                                tvecs[i][0]
                            )
                            marker_id_pose_dict[aruco_id[0]] = {
                                "camera_id": self.id,
                                "rvec": rvec_world,
                                "tvec": tvec_world
                            }

            # Depending on the value of keep_old_values, allow for setting the
            # class variable to empty dictionary
            # DeMorgan's Law is wack 1/23/22
            if len(marker_id_pose_dict) != 0 or not keep_old_values:
                self.detected_aruco_ids_dict = marker_id_pose_dict
            print(self.detected_aruco_ids_dict)

            time.sleep(0.1)

    def show_frame(self):
        cv2.imshow("camera " + str(self.id), self.undistorted_img)
        key = cv2.waitKey(1)
        if key == ord('q'):
            self.capture.release()
            cv2.destroyAllWindows()
            exit(1)
