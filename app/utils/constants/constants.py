import numpy as np
from cv2 import aruco

SAVE_VIDEO_STREAM_FILE_PATH = "/media/mighty/research-1/collected_data_from_cameras/video/"
SAVE_POSE_HISTORY_FILE_PATH = "/media/mighty/research-1/collected_data_from_cameras/pose_history/"

# Frame Rate needs to be set manually
# https://stackoverflow.com/a/54444910
# Determines the frame rate for saving the video and taking new pictures
CAMERA_FRAME_RATE = 24

# The frame rate of web socket data so that we don't overload GGB
MOCAP_OUT_FRAME_RATE = 10

# 640 x 480 pixels
CAMERA_FRAME_SIZE = (640, 480)

# These are the calibration we get by taking several pictures of the checkerboard.
# These need to be changed if you swap out the type of camera.
# I make the assumption here that all cameras will be the same, but if they are not
# they need to be separated.
CAMERA_CALIBRATION_MATRIX = np.array([
    [589.2678740465893, 0.0, 360.7562954333174],
    [0.0, 588.3283124033934, 229.65330113945927],
    [0.0, 0.0, 1.0]
])

CAMERA_CALIBRATION_DISTANCE_COEFF = np.array([[
    -0.4003160209939034, 0.057038417288267244, -0.00021952153111566165,
    -0.002627009754899686, 0.1850395020517708
]])

# All printed aruco markers must be 18x18 cm. (I used MS Word to print them out)
MARKER_LENGTH = 18 # cm

ARUCO_DICT = aruco.getPredefinedDictionary(aruco.DICT_6X6_1000)
ARUCO_PARAMS = aruco.DetectorParameters_create()

# Dictionary of extrinsic matrices so that we can calculate the world position
# based on the camera id. These are generated using Guoxiang's Posegraph julia code
CAMERA_EXTRINSIC_MATRIX_DICT = {
    1: (np.array([
            -0.9803085845391921, -0.08998554515090676, -0.17577736129166313, -233.9595018934706,
            0.08041298209435765, 0.6310859969182715, -0.7715336783345003, 390.9771610948868,
            0.18035750993362673, -0.7704758699385502, -0.6114230143304847, 280.8299878687395,
            0.0, 0.0, 0.0, 1.0
        ]).reshape(4,4)
    ),
    2: (np.array([
            -0.9936636399720464, -0.018362085518804392, -0.11088464462180515, 3.0846911635829493,
            0.07953499515315617, 0.5822044240320479, -0.809142875630441, 386.70947514073373,
            0.07941508133529383, -0.8128350647289474, -0.5770549388087733, 279.21367030656126,
            0.0, 0.0, 0.0, 1.0
        ]).reshape(4,4)
    ),
    3: (np.array([
            -0.992422773240586, -0.03970745104058697, -0.11627707205345489, 196.31813699586982,
            0.07140295221808453, 0.5837688148442411, -0.8087741274483826, 380.48166385015,
            0.09999328761475387, -0.8109483887074505, -0.5765102369297389, 262.3725907281088,
            0.0, 0.0, 0.0, 1.0
        ]).reshape(4,4)
    ),
    4: (np.array([
            -0.9982391776405697, 0.04374276227656844, 0.04006388613071116, 387.77516904090584,
            -0.009708376429354949, 0.5458259995464554, -0.8378423035668577, 412.79423056114535,
            -0.058517447403188344, -0.8367559673928405, -0.5444402257198548, 276.7120959156982,
            0.0, 0.0, 0.0, 1.0
        ]).reshape(4,4)
    )
}
