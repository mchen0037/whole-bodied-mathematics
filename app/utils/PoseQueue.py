import time
from threading import Thread

class PoseQueue(object):
    """
        A PoseQueue collects translation vectors over time so that we can
        apply a probablistic model to where the expected position is of an
        aruco marker.

        - aruco_id <int>: the aruco_id associated with the Pose

        - MAX_QUEUE_LENGTH <int>: the length of the PoseQueue. It store no more
            than this number

        - length <int>: Current length of the PoseQueue.

        - pose_history <list<dict>>: Stores positions as a list of dictionaries
            {
                "timestamp": <float> time.time() value of when this value was recorded
                "tvec": <np.array> 1x3 array which gives the x, y, z value of
                    the detected aruco marker
            }

    """
    def __init__(self, aruco_id, tvec):

        self.aruco_id = aruco_id
        self.MAX_QUEUE_LENGTH = 30
        self.length = 1

        # So we don't get any 0 errors, make sure we put in a dummy value
        # to begin with
        self.pose_history = [{
            "timestamp": time.time(), # in Milliseconds
            "tvec": tvec
        }]

        clear_old_values_thread = Thread(target=self.clear_old_values, args=())
        clear_old_values_thread.daemon = True
        clear_old_values_thread.start()

    def clear_old_values(self):
        """
            When a value in the PoseQueue is older than 3 seconds, we remove it
            from the pose_history. This will clear any old values and make
            the point disappear when the value is too old. This function is run
            on the clear_old_values_thread.

            Inputs: None

            Returns: None
        """
        while True:
            if self.length >= 1 and self.pose_history[0]["timestamp"] + 3 <= time.time():
                self.pose_history.pop(0)
                self.length = self.length - 1

            time.sleep(0.1)


    def push(self, tvec):
        """
            Pushes a value into the PoseQueue. If this goes beyond the
            MAX_QUEUE_LENGTH, we pop the oldest value.

            Inputs:
                - tvec <np.array>: Translation vector which gives the x, y, z
                    value of a detected aruco marker

            Returns: None
        """
        dat = {
            "timestamp": time.time(), # in Milliseconds
            "tvec": tvec
        }
        if len(self.pose_history) >= self.MAX_QUEUE_LENGTH:
            # If the pose_history is too big, then we need to clear
            # one of the tvecs to put it in the pose history
            self.pose_history.pop(0)
            self.pose_history.append(dat)
        else:
            self.pose_history.append(dat)
            self.length = self.length + 1

    def get_expected_pose(self, save=False, save_location=None):
        """
            Calculates the Expected Value for each x, y, z based on the
            pose_history values in the PoseQueue. Uses a running average.

            Inputs:
                - save <bool>: determines if we should save the Pose into a CSV file
                - save_location <string>: the path to the CSV file

            Returns:
                - expected_pose <list>: [x, y, z] values of where we expect the
                    aruco marker to be
        """
        if self.length == 0:
            return None

        sum_x = 0
        sum_y = 0
        sum_z = 0
        for tvec_dict in self.pose_history:
            sum_x = sum_x + tvec_dict["tvec"][0]
            sum_y = sum_y + tvec_dict["tvec"][1]
            sum_z = sum_z + tvec_dict["tvec"][2]
        avg_x = sum_x / self.length
        avg_y = sum_y / self.length
        avg_z = sum_z / self.length

        expected_pose = [avg_x, avg_y, avg_z]

        if save == True:
            if save_location:
                try:
                    # timestamp, id, x, y, z
                    f = open(save_location, "a")
                    timestamp = time.time()  # in ms
                    id = self.aruco_id
                    x = expected_pose[0]
                    y = expected_pose[1]
                    z = expected_pose[2]
                    line = (
                        str(timestamp) + "," +
                        str(id) + "," +
                        str(x) + "," +
                        str(y) + "," +
                        str(z) + "\n"
                    )
                    f.write(line)
                    f.close()
                except:
                    print("Error in saving Pose")

        return expected_pose
