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
        print("clearoldvalues")
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
            pose_history values in the PoseQueue.

            Inputs:
                - save <bool>: determines if we should save the Pose into a CSV file
                - save_location <string>: the path to the CSV file

            Returns:
                - expected_pose <list>: [x, y, z] values of where we expect the
                    aruco marker to be
        """
        # Use a geometric which converges to 1 to calculate the probability
        # of each pose based on how old it is.
        # There's probably more advanced math for this but this is the
        # best I got
        # https://www.desmos.com/calculator/fwrz2lwttq
        # This is based on a max_queue_length of 20, will break otherwise
        # expected pose is [x, y, z]
        a_1 = ((-1 * 0.65 / (self.MAX_QUEUE_LENGTH)) * (self.length - 1)) + 1
        r = 1 - a_1
        sum_prob = 0
        expected_pose = None

        for idx, tvec_dict in enumerate(self.pose_history):
            i = idx + 1
            prob = a_1 * (r ** (i - 1))
            sum_prob = sum_prob + prob

            if expected_pose is None:
                expected_pose = prob * self.pose_history[idx]["tvec"]
            else:
                expected_pose = (
                    expected_pose + prob * self.pose_history[idx]["tvec"]
                )

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
