import numpy as np
camera_aruco_pose_dict = {
  "A": {
    "camera_id": 1,
    "aruco_markers": {
      1: {
        "rvec": np.array([2, 2, 1]),
        "tvec": np.array([3.2, 5.2, 8.2])
      },
      2: {
        "rvec": np.array([1.3, 1.9, 1.2]),
        "tvec": np.array([3.1, 1.9, 4.2])
      }
    }
  },
  "B": {
    "camera_id": 2,
    "aruco_markers": {
      2: {
        "rvec": np.array([3, 2, 1]),
        "tvec": np.array([3.2, 1.2, 4.2])
      },
      3: {
        "rvec": np.array([1.3, 1.9, 1.2]),
        "tvec": np.array([4.1, 7.9, 2])
      }
    }
  },
  "C": {
    "camera_id": 3,
    "aruco_markers": {
      3: {
        "rvec": np.array([1, 2, 1]),
        "tvec": np.array([4, 7.2, 2.2])
      },
      1: {
        "rvec": np.array([1.3, 1.9, 1.2]),
        "tvec": np.array([3.1, 4.9, 8.2])
      }
    }
  },
}

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
        pass
    elif camera_id == 2:
        pass
    elif camera_id == 3:
        pass
    elif camera_id == 4:
        pass
    return (rvec, tvec)

# camera_aruco_pose_dict = test_struct
aruco_camera_pose_dict = {}
for camera_key in camera_aruco_pose_dict:
    for aruco_marker_key in camera_aruco_pose_dict[camera_key]["aruco_markers"]:
        aruco_marker_data = camera_aruco_pose_dict[camera_key]["aruco_markers"][aruco_marker_key]
        # print(aruco_marker_key, aruco_marker_data)
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

# print(aruco_camera_pose_dict)
for aruco_marker in aruco_camera_pose_dict:
    len = aruco_camera_pose_dict[aruco_marker]['tvec'].shape[0]
    reshaped_tvec = aruco_camera_pose_dict[aruco_marker]['tvec'].reshape(int(len/3), 3)
    reshaped_rvec = aruco_camera_pose_dict[aruco_marker]['rvec'].reshape(int(len/3), 3)
    aruco_camera_pose_dict[aruco_marker]['rvec'] = np.mean(reshaped_rvec, axis=0)
    aruco_camera_pose_dict[aruco_marker]['tvec'] = np.mean(reshaped_tvec, axis=0)
print(aruco_camera_pose_dict)

# For calculating average rvec and tvec
# average_rvec_world = np.array([0.,0.,0.])
# average_tvec_world = np.array([0.,0.,0.])
# for camera_id_dict in aruco_id_dict['camera_data']:
#     # Transform to world coordinates, then find the running average of
#     # rvecs and tvecs from all cameras
#     rvec_world, tvec_world = transform_to_world(
#         camera_id_dict['camera_id'],
#         camera_id_dict['rvec'],
#         camera_id_dict['tvec']
#     )
#     average_rvec_world += rvec_world
#     average_tvec_world += tvec_world
# average_rvec_world = average_rvec_world / len(aruco_id_dict['camera_data'])
# print(average_rvec_world)
