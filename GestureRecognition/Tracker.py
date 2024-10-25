import cv2
import mediapipe as mp
import numpy as np

class PoseTracker():

    def __init__(self):

        self.mp_draw = mp.solutions.drawing_utils
        self.mp_holistic = mp.solutions.holistic #Mediapipe dection model
        self.holistic = self.mp_holistic.Holistic(static_image_mode=True, model_complexity=1,
                                                  min_detection_confidence=0.7, min_tracking_confidence=0.7)

    def detectPresence(self, img):
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB) # Color conversion BGR -> RGB
        img.flags.writeable = False
        results = self.holistic.process(img) # Model prediction
        img.flags.writeable = True
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)  # Color conversion RGB -> BGR
        return results

    def drawLandmarks(self, img, results):
        self.mp_draw.draw_landmarks(img, results.pose_landmarks, self.mp_holistic.POSE_CONNECTIONS, # Draw pose/body connections
                                    self.mp_draw.DrawingSpec((88,219,255), thickness=2, circle_radius=4), #Landmark Colour
                                    self.mp_draw.DrawingSpec((222,222,222), thickness=2, circle_radius=2))  #Connection Colour
        self.mp_draw.draw_landmarks(img, results.right_hand_landmarks, self.mp_holistic.HAND_CONNECTIONS, # Draw hand connections
                                    self.mp_draw.DrawingSpec((88, 219, 255), thickness=2, circle_radius=4),
                                    self.mp_draw.DrawingSpec((255, 255, 255), thickness=2,circle_radius=2))
        self.mp_draw.draw_landmarks(img, results.left_hand_landmarks, self.mp_holistic.HAND_CONNECTIONS,
                                    self.mp_draw.DrawingSpec((88, 219, 255), thickness=2, circle_radius=4),
                                    self.mp_draw.DrawingSpec((255, 255, 255), thickness=2,circle_radius=2))
        return img

    def formatLandmarks(self, results, image=False, pose=True, left=True, right=True):
        pose_lms = [] # Arrays for storing landmarks
        right_lms = []
        left_lms = []
        if image == False:
            if pose:
                if results.pose_landmarks: # Storing pose landmarks
                    for id, lm in enumerate(results.pose_landmarks.landmark):
                        if (id> 10 and id < 23):
                            pose_lms.append([lm.x, lm.y, lm.z, lm.visibility])
                    pose_lms = np.array(pose_lms).flatten()
                else:
                    pose_lms = np.zeros(12*4) # If landmarks aren't present, fill with 0s

            if right:
                if results.right_hand_landmarks: # Storing right hand landmarks
                    for id, lm in enumerate(results.right_hand_landmarks.landmark):
                        right_lms.append([lm.x, lm.y, lm.z])
                    right_lms = np.array(right_lms).flatten()
                else:
                    right_lms = np.zeros(21 * 3) #If landmarks aren't present, fill with 0s

            if left:
                if results.left_hand_landmarks: # Storing left hand landmarks
                    for id, lm in enumerate(results.left_hand_landmarks.landmark):
                        left_lms.append([lm.x, lm.y, lm.z])
                    left_lms = np.array(left_lms).flatten()
                else:
                    left_lms = np.zeros(21*3) #If landmarks aren't present, fill with 0s
            return np.concatenate([pose_lms, right_lms, left_lms])
        else: # Image landmark formatting
            if pose:
                if results.pose_landmarks:  # Storing pose landmarks
                    for id, lm in enumerate(results.pose_landmarks.landmark):
                        if (id > 10 and id < 23):
                            pose_lms.append([lm.x, lm.y, lm.z, lm.visibility])

                else:
                    pose_lms = np.zeros(12 * 4)  # If landmarks aren't present, fill with 0s

            if right:
                if results.right_hand_landmarks:  # Storing right hand landmarks
                    for id, lm in enumerate(results.right_hand_landmarks.landmark):
                        right_lms.append([lm.x,lm.y,lm.z])
                else:
                    right_lms = np.zeros(21 * 3)  # If landmarks aren't present, fill with 0s

            if left:
                if results.left_hand_landmarks:  # Storing left hand landmarks
                    for id, lm in enumerate(results.left_hand_landmarks.landmark):
                        left_lms.append([lm.x, lm.y, lm.z])

                else:
                    left_lms = np.zeros(21 * 3)  # If landmarks aren't present, fill with 0s
            pose_lms = np.array(pose_lms)
            right_lms = np.array(right_lms)
            left_lms = np.array(left_lms)

            concat = np.array([])
            if (pose_lms.size > 0):
                concat = pose_lms

            if (concat.size  < 1):
                concat = right_lms
            elif (right_lms.size > 0):
                concat = np.concatenate([concat, right_lms])

            if (concat.size < 1):
                concat = left_lms
            elif (left_lms.size > 0):
                concat = np.concatenate([concat, left_lms])

            return concat.flatten()