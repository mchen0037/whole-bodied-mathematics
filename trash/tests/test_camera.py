import cv2
import yaml
import numpy as np

camera_1 = cv2.VideoCapture(4)
with open('camera_calibration_matrices/calibration_3.yaml') as f:
    loadeddict = yaml.load(f)
mtx_1 = loadeddict.get('camera_matrix')
dist_1 = loadeddict.get('dist_coeff')
mtx_1 = np.array(mtx_1)
dist_1 = np.array(dist_1)

ret_2, img_1 = camera_1.read()

img_gray_1 = cv2.cvtColor(img_1,cv2.COLOR_RGB2GRAY)
h_1,  w_1 = img_gray_1.shape[:2]

newcameramtx_1, roi=cv2.getOptimalNewCameraMatrix(mtx_1,dist_1,(w_1,h_1),1,(w_1,h_1))

while True:
    ret_1, img_1 = camera_1.read()
    img_gray_1 = cv2.cvtColor(img_1, cv2.COLOR_RGB2GRAY)
    # undistort the image
    dst = cv2.undistort(img_gray_1, mtx_1, dist_1, None, newcameramtx_1)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    # show the image
    cv2.imshow("img_dict" + str(1),dst)
