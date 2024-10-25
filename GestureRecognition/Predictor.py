import cv2
import os
import numpy as np

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.optimizers import Adam

from src.GestureRecognition.Tracker import PoseTracker

class GesturePredictor():

    def __init__(self, model_name):
        self.info = []
        self.actions = []
        self.hooman_parts = []
        with open(os.path.join('Models', model_name, 'model_info.txt'), 'r') as file:
            self.info = file.readline().split('_')
            self.actions = file.readline().split('_')
            parts = file.readline().split('_')
            for part in parts:
                if (part == 'False'):
                    self.hooman_parts.append(False)
                else:
                    self.hooman_parts.append(True)

        if (self.info[0] == 'video'):
            self.model = Sequential()  # Building the model
            self.model.add(LSTM(64, return_sequences=True, activation='relu', input_shape=(int(self.info[1]), int(self.info[2]))))
            self.model.add(LSTM(128, return_sequences=True, activation='relu'))
            self.model.add(LSTM(64, return_sequences=False, activation='relu'))
            self.model.add(Dense(64, activation='relu'))
            self.model.add(Dense(32, activation='relu'))
            self.model.add(Dense(int(self.info[3]), activation='softmax'))
            self.model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['categorical_accuracy'])
            try:
                self.model.load_weights(os.path.join('Models', model_name, model_name + '.h5'))
                print('Video model "' + model_name + '" loaded!')
            except:
                print("Video Model failed to load")
        elif (self.info[0] == 'image'):
            self.model = Sequential()  # Building the model
            self.model.add(Dense(64, input_shape=(int(self.info[1]),), activation='relu'))
            self.model.add(Dropout(0.3))
            self.model.add(Dense(128, activation='relu'))
            self.model.add(Dropout(0.3))
            self.model.add(Dense(64, activation='relu'))
            self.model.add(Dense(int(self.info[2]), activation='softmax'))
            optimizer = Adam(learning_rate=0.0001)
            self.model.compile(optimizer=optimizer, loss='categorical_crossentropy', metrics=['categorical_accuracy'])
            try:
                self.model.load_weights(os.path.join('Models', model_name, model_name + '.h5'))
                print('Image model "' + model_name + '" loaded!')
            except:
                print("Image Model failed to load")

    def camPredict(self, threshold):

        wCam, hCam = 640, 480

        cap = cv2.VideoCapture(0)
        cap.set(3, wCam)
        cap.set(4, hCam)

        gs = PoseTracker()

        if (self.info[0] == 'video'):
            frames = int(self.info[1])
            sequence=[]
            while True:
                success, img = cap.read()
                results = gs.detectPresence(img)
                img = gs.drawLandmarks(img, results)
                landmarks = gs.formatLandmarks(results)

                if landmarks[0] != 0:
                    sequence.insert(0,landmarks)
                    sequence = sequence[:frames]
                    if len(sequence) == frames:
                        try:
                            result = self.model.predict(np.expand_dims(sequence, axis=0))[0]
                            argmax =np.argmax(result)
                            print(result)
                            if argmax > threshold:
                                print(self.actions[argmax])
                        except:
                            result = self.model.predict(np.expand_dims(sequence, axis=0))[0]
                            print('Format incorrect, could not predict')


                cv2.imshow('Image', img)  # Display camera
                cv2.waitKey(1)
        elif (self.info[0] == 'image'):
            frames = int(self.info[1])
            while True:
                success, img = cap.read()
                results = gs.detectPresence(img)
                img = gs.drawLandmarks(img, results)
                landmarks = gs.formatLandmarks(results, image=True, pose=self.hooman_parts[0], left=self.hooman_parts[1], right=self.hooman_parts[2])
                landmarks = landmarks.flatten()
                if landmarks[0] != 0:
                    try:
                        result = self.model.predict(np.expand_dims(landmarks, axis=0))[0]
                        argmax =np.argmax(result)
                        if result[argmax] > threshold:
                            print(self.actions[argmax])
                    except:
                        result = self.model.predict(np.expand_dims(landmarks, axis=0))[0]
                        print('Format incorrect, could not predict')


                cv2.imshow('Image', img)  # Display camera
                cv2.waitKey(1)

    def predict(self, threshold, landmarks):

        if (self.info[0] == 'video'):
            frames = int(self.info[1])
            if len(landmarks) == frames:
                try:
                    result = self.model.predict(np.expand_dims(landmarks, axis=0))[0]
                    argmax =np.argmax(result)
                    print(result)
                    if argmax > threshold:
                        print(self.actions[argmax])
                except:
                    result = self.model.predict(np.expand_dims(landmarks, axis=0))[0]
                    print('Format incorrect, could not predict')

        elif (self.info[0] == 'image'):
            try:
                result = self.model.predict(np.expand_dims(landmarks, axis=0))[0]
                argmax =np.argmax(result)
                if result[argmax] > threshold:
                    return self.actions[argmax]
            except:
                return "404"
