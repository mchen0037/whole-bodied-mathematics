from datetime import datetime

class PoseQueue(object):
    def __init__(self, aruco_id, tvec):

        self.aruco_id = aruco_id
        self.MAX_QUEUE_LENGTH = 50
        self.length = 1

        # So we don't get any 0 errors, make sure we put in a dummy value
        # to begin with
        self.pose_history = [{
            "timestamp": datetime.now().timestamp() * 1000, # in Milliseconds
            "tvec": tvec
        }]

    def push(self, tvec):
        dat = {
            "timestamp": datetime.now().timestamp() * 1000, # in Milliseconds
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

    def get_expected_pose(self):
        # Use a geometric which converges to 1 to calculate the probability
        # of each pose based on how old it is.
        # There's probably more advanced math for this but this is the
        # best I got
        # https://www.desmos.com/calculator/fwrz2lwttq
        # This is based on a max_queue_length of 20, will break otherwise
        a_1 = ((-1 * 0.95 / (self.MAX_QUEUE_LENGTH - 1)) * (self.length - 1)) + 1
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
        # print(expected_pose)
        # print(self.pose_history[0]["tvec"])
        # return self.pose_history[0]["tvec"]
        return expected_pose
