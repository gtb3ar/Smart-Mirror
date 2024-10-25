# This houses a function used to record datasets for training deep learning models.

import cv2
import os
import numpy as np

def recordDataset(self, collection_mode, dataset_name, number_of_frames=30, number_of_videos=30, actions=[''],
                  pose=True, left=True, right=True):
    if (actions == ['']):
        print('No actions to record')
        exit()
    actions = np.array(actions)
    dataset_folder = 'Datasets'

    # Setting up folders for collection mode
    if (dataset_name != ''):
        if (collection_mode == 1):  # Image Collection Mode
            for action in actions:
                try:
                    os.makedirs(os.path.join(dataset_folder, dataset_name, action))
                except:
                    pass
        elif (collection_mode == 2):  # Video Collection Mode
            for action in actions:
                for video in range(number_of_videos):
                    try:
                        os.makedirs(os.path.join(dataset_folder, dataset_name, action, str(video)))
                    except:
                        pass

    # Setting camera up
    wCam, hCam = 640, 480
    cap = cv2.VideoCapture(0)
    cap.set(3, wCam)
    cap.set(4, hCam)

    if (collection_mode == 1):  # Build image set
        for action in actions:
            for frame in range(number_of_frames):

                success, img = cap.read()
                results = self.detectPresence(img)
                img = self.drawLandmarks(img, results)
                landmarks = self.formatLandmarks(results, image=True, pose=pose, left=left, right=right)
                if frame == 0:
                    cv2.putText(img, 'Starting Collection!', (120, 200),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3, cv2.LINE_AA)
                    cv2.putText(img, 'Collection for action {}'.format(action), (15, 12),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255), 1, cv2.LINE_AA)
                    cv2.imshow("Collection Data", img)
                    cv2.waitKey(5000)
                else:
                    cv2.putText(img, 'Collection for action {}'.format(action), (15, 12),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255), 1, cv2.LINE_AA)
                    cv2.imshow("Collection Data", img)

                npy_path = os.path.join(dataset_folder, dataset_name, action, str(frame))
                np.save(npy_path, landmarks)

                if cv2.waitKey(10) & 0xFF == ord('q'):
                    break
        cap.release()
        cv2.destroyAllWindows()

    elif (collection_mode == 2):  # Build video set
        for action in actions:  # Loop through, different actions
            for video in range(number_of_videos):  # Loop through, videos in the action
                for frame in range(number_of_frames):  # Loop through, frames in the video

                    success, img = cap.read()
                    results = self.detectPresence(img)
                    img = self.drawLandmarks(img, results)
                    landmarks = self.formatLandmarks(results, pose=pose, left=left, right=right)

                    if frame == 0 and video == 0:
                        cv2.putText(img, 'Starting Collection!', (120, 200),
                                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3, cv2.LINE_AA)
                        cv2.putText(img, 'Collection for {}, video {}'.format(action, video), (15, 12),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255), 1, cv2.LINE_AA)
                        cv2.imshow("Collection Data", img)
                        cv2.waitKey(2000)
                    else:
                        cv2.putText(img, 'Collection for {}, video {}'.format(action, video), (15, 12),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255), 1, cv2.LINE_AA)
                        cv2.imshow("Collection Data", img)

                    npy_path = os.path.join(dataset_folder, dataset_name, action, str(video), str(frame))
                    np.save(npy_path, landmarks)

                    if cv2.waitKey(10) & 0xFF == ord('q'):
                        break

        cap.release()
        cv2.destroyAllWindows()

    with open(os.path.join('../Datasets', dataset_name, 'dataset_info.txt'), 'x') as file:
        file.write(str(pose) + '_' + str(left) + '_' + str(right))