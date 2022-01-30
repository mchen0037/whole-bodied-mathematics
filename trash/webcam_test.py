import cv2
vid_2 = cv2.VideoCapture(2)
vid_4 = cv2.VideoCapture(4)
vid_6 = cv2.VideoCapture(6)
vid_8 = cv2.VideoCapture(7)

# while True:
#     ret_8, frame_8 = vid_8.read()
#     cv2.imshow("frame_8", frame_8)
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break

while(True):
    ret_2, frame_2 = vid_2.read()
    ret_4, frame_4 = vid_4.read()
    ret_6, frame_6 = vid_6.read()
    ret_8, frame_8 = vid_8.read()

    # frame = cv2.resize(frame, None, fx=0.4, fy=0.4)
    # frame_2_small = cv2.resize(frame_2, None, fx=0.4, fy=0.4)
    # frame_4_small = cv2.resize(frame_4, None, fx=0.4, fy=0.4)
    # frame_6_small = cv2.resize(frame_6, None, fx=0.4, fy=0.4)
    # frame_8_small = cv2.resize(frame_8, None, fx=0.4, fy=0.4)

    cv2.imshow("frame_2", frame_2)
    cv2.imshow("frame_4", frame_4)
    cv2.imshow("frame_6", frame_6)
    cv2.imshow("frame_8", frame_8)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
