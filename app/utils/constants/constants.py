import numpy as np
from cv2 import aruco

SAVE_VIDEO_STREAM_FILE_PATH = "collected_data_from_cameras/video/"
SAVE_POSE_HISTORY_FILE_PATH = "collected_data_from_cameras/pose_history/"

# 640 x 480 pixels
WEBCAM_FRAME_SIZE = (640, 480)

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
            -0.9812332825642545, -0.053826353154115734, -0.185159306799054, -219.95870938059167,
            0.1263591468626452, 0.5458418498072937, -0.8283055239481965, 367.92058099946263,
            0.14565236418377236, -0.8361575202706009, -0.5287967379840741, 271.0204821192859,
            0.0, 0.0, 0.0, 1.0
        ]).reshape(4,4)
    ),
    2: (np.array([
            -0.9841722266462236, -0.07900782775524805, -0.15862783945957126, -107.27894372513103,
            0.09694975655331366, 0.5092447386650562, -0.8551435790826076, 373.5142758189748,
            0.14834342925275684, -0.8569874907461343, -0.493524738693185, 253.07970116862742,
            0.0, 0.0, 0.0, 1.0
        ]).reshape(4,4)
    ),
    3: (np.array([
            -0.9858001764885023, -0.04585798343218855, -0.16153964649822272, 67.25604976245491,
            0.11336838284985981, 0.5279129677029515, -0.8416979911471038, 370.2184788628875,
            0.12387744671749273, -0.8480595167124744, -0.5152178513096757, 270.93225971740884,
            0.0, 0.0, 0.0, 1.0
        ]).reshape(4,4)
    ),
    4: (np.array([
            -0.9974697263116098, 0.03368978863273059, -0.06260306089740633, 196.10914783212812,
            0.07081835904896618, 0.39360535547160125, -0.916547644242069, 398.2243252561984,
            -0.006237396368208536, -0.9186619738978841, -0.39499528174471843, 245.0466275260443,
            0.0, 0.0, 0.0, 1.0
        ]).reshape(4,4)
    )
}
