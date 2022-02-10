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
            -0.9868746536818611, -0.0707676265914565, -0.1451563327826914, -256.5232819771118,
            0.07203671840024117, 0.6115629052694793, -0.78790959132408, 390.28770756767113,
            0.14453072034149567, -0.7880245909392464, -0.5984380627538679, 257.1897812302522,
            0.0, 0.0, 0.0, 1.0
        ]).reshape(4,4)
    ),
    2: (np.array([
            -0.9985051218931273, -0.020036918157044857, -0.05085315588987321, -34.85710445561407,
            0.026404829149723183, 0.6377883594907976, -0.7697589190750648, 383.73128467239894,
            0.04785714733209439, -0.7699509922123654, -0.6363058722347525, 274.85892393740295,
            0.0, 0.0, 0.0, 1.0
        ]).reshape(4,4)
    ),
    3: (np.array([
            -0.997647635363059, -0.029059757620277793, -0.06208644088324335, 161.56550997060427,
            0.0252378462917318, 0.6863825453373894, -0.7268026228424896, 370.8142905174674,
            0.06373575738196482, -0.7266598461062906, -0.6840345176142283, 274.99437256330555,
            0.0, 0.0, 0.0, 1.0
        ]).reshape(4,4)
    ),
    4: (np.array([
            -0.9849573841987447, 0.0856941280037051, 0.15005155026873848, 342.75697629220406,
            -0.05411222155088333, 0.6717259441075809, -0.738820765471307, 388.5243055247516,
            -0.16410612051716797, -0.7358265912825281, -0.6569843291664885, 279.4857339323828,
            0.0, 0.0, 0.0, 1.0
        ]).reshape(4,4)
    )
}
