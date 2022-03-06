import numpy as np
from cv2 import aruco

NUM_CAMERAS = 4

SAVE_VIDEO_STREAM_FILE_PATH = "/media/mighty/research-1/collected_data_from_cameras/video/"
SAVE_POSE_HISTORY_FILE_PATH = "/media/mighty/research-1/collected_data_from_cameras/pose_history/"
SAVE_SCREEN_STREAM_FILE_PATH = "/media/mighty/research-1/collected_data_from_cameras/screen/"

# Frame Rate needs to be set manually
# https://stackoverflow.com/a/54444910
# Determines the frame rate for saving the video and taking new pictures
CAMERA_FRAME_RATE = 10
# Only use about 10 FPS for screen capture because pyscreenshot can't take
# screenshots that fast
SCREEN_CAPTURE_FRAME_RATE = 10

# The frame rate of web socket data so that we don't overload Desmos
MOCAP_OUT_FRAME_RATE = 15

# 640 x 480 pixels
CAMERA_FRAME_SIZE = (640, 480)
SCREEN_CAPTURE_SIZE = (1680,1050)

# The default bounds in real world in cm
DEFAULT_BOUNDS = [-300, 300, -200, 200]
DEFAULT_ORIGIN = [0, 0, 0]

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
            -0.9989347040720827, -0.02170560509265326, -0.04072252089424574, -169.04591654142874,
            0.018658673563218892, 0.6171297266139563, -0.7866401683299963, 315.68278689736627,
            0.042205579030286176, -0.7865619919859753, -0.6160673030292817, 274.493611105896,
            0.0, 0.0, 0.0, 1.0
        ]).reshape(4,4)
    ),
    2: (np.array([
            -0.9968622012417856, -0.05178168339173933, -0.05986993402786095, 1.0095419223299054,
            0.013142141666580565, 0.6375826319897255, -0.7702698692649679, 291.7081646893152,
            0.07805790061100978, -0.7686397365802609, -0.6349015037799406, 283.50893219138504,
            0.0, 0.0, 0.0, 1.0
        ]).reshape(4,4)
    ),
    3: (np.array([
            -0.998873876831504, -0.011001710261349083, -0.04615127901723616, 166.98760322439284,
            0.029645008100024264, 0.6147475300603926, -0.7881666370631252, 329.36772326429883,
            0.03704256576360433, -0.7886472193927853, -0.613729102834204, 259.63936280050814,
            0.0, 0.0, 0.0, 1.0
        ]).reshape(4,4)
    ),
    4: (np.array([
            -0.9941910928789585, 0.04102837517516757, 0.09950247871600322, 270.46685527548567,
            -0.049527612030108595, 0.6463959811556325, -0.7613929676536572, 329.93361201978087,
            -0.09555671868967679, -0.7618982267838229, -0.6406090894897832, 276.5826569945272,
            0.0, 0.0, 0.0, 1.0
        ]).reshape(4,4)
    )
}
