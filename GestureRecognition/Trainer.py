import os
import numpy as np
from sklearn.model_selection import train_test_split
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.callbacks import TensorBoard
from tensorflow.keras.optimizers import Adam

def trainModel(self, dataset_name, model_name, epochs=2000):
    dataset_folder = 'Datasets'
    # Testing for .npy's or folders, to train the model on the correct type
    dataset_type = 0
    folder_or_file = \
    os.listdir(os.path.join(dataset_folder, dataset_name, os.listdir(os.path.join(dataset_folder, dataset_name))[0]))[0]
    if (folder_or_file.endswith('.npy')):
        dataset_type = 1  # Images
    else:
        dataset_type = 2  # Videos

    if (dataset_type == 1):  # NEEDS WORK
        actions = os.listdir(os.path.join(dataset_folder, dataset_name))  # Grabbing dataset actions

        for action in actions:
            if (os.path.isdir(os.path.join(dataset_folder, dataset_name, action)) == False):
                actions.remove(action)

        label_map = {label: num for num, label in enumerate(actions)}  # making a map of each action
        frame_count = len(os.listdir(
            os.path.join(dataset_folder, dataset_name, os.listdir(os.path.join(dataset_folder, dataset_name))[0])))

        frames, labels = [], []

        for action in actions:
            for frame in range(frame_count):
                result = np.load(os.path.join(dataset_folder, dataset_name, action, str(frame) + '.npy'))
                frames.append(result.flatten())
                labels.append(label_map[action])

        x = np.array(frames)
        y = to_categorical(labels).astype(int)
        print(x.shape)
        print(y.shape)
        x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.15)

        log_dir = os.path.join('../../Models', model_name, 'TensorBoard Logs')  # Logging training with Tensorboard
        tb_callback = TensorBoard(log_dir=log_dir)
        model = Sequential()  # Building the model
        model.add(Dense(64, input_shape=(x.shape[1],), activation='relu'))
        model.add(Dropout(0.3))
        model.add(Dense(128, activation='relu'))
        model.add(Dropout(0.3))
        model.add(Dense(64, activation='relu'))
        action_shape = np.array(actions).shape[0]
        model.add(Dense(action_shape, activation='softmax'))
        optimizer = Adam(learning_rate=0.0001)
        model.compile(optimizer=optimizer, loss='categorical_crossentropy', metrics=['categorical_accuracy'])

        model.fit(x_train, y_train, epochs=epochs, callbacks=[tb_callback])
        model_dir = os.path.join('../../Models', model_name, model_name + '.h5')
        model.save(model_dir)

        with open(os.path.join('../../Models', model_name, 'model_info.txt'), 'x') as file:
            file.write('image_' + str(x.shape[1]) + '_' + str(action_shape) + '\n')
            for action in actions:
                file.write(action)
                if action != actions[len(actions) - 1]:
                    file.write('_')
            with open(os.path.join('../Datasets', dataset_name, 'dataset_info.txt'), 'r') as dsi:
                file.write('\n' + dsi.readline())


    elif (dataset_type == 2):
        actions = os.listdir(os.path.join(dataset_folder, dataset_name))  # Grabbing dataset actions
        label_map = {label: num for num, label in enumerate(actions)}  # making a map of each action
        dir = os.path.join(dataset_folder, dataset_name)
        action = os.listdir(dir)[0]

        video_count = len(os.listdir(os.path.join(dir, action)))
        frame_count = len(os.listdir(os.path.join(dir, action, '0')))
        videos, labels = [], []

        for action in actions:
            for video in range(video_count):
                window = []
                for frame in range(frame_count):
                    result = np.load(
                        os.path.join(dataset_folder, dataset_name, action, str(video), str(frame) + '.npy'))
                    window.append(result)
                videos.append(window)
                labels.append(label_map[action])

        x = np.array(videos)
        y = to_categorical(labels).astype(int)

        x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.30)

        log_dir = os.path.join('../../Models', model_name, 'TensorBoard Logs')  # Logging training with Tensorboard

        tb_callback = TensorBoard(log_dir=log_dir)
        print(x.shape)
        model = Sequential()  # Building the model
        model.add(LSTM(64, return_sequences=True, activation='relu', input_shape=(x.shape[1], x.shape[2])))
        model.add(LSTM(128, return_sequences=True, activation='relu'))
        model.add(LSTM(64, return_sequences=False, activation='relu'))
        model.add(Dense(64, activation='relu'))
        model.add(Dense(32, activation='relu'))
        action_shape = np.array(actions).shape[0]
        model.add(Dense(action_shape, activation='softmax'))

        model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['categorical_accuracy'])
        model.fit(x_train, y_train, epochs=epochs, callbacks=[tb_callback], validation_data=(x_test, y_test))
        model_dir = os.path.join('../../Models', model_name, model_name + '.h5')
        model.save(model_dir)
        with open(os.path.join('../../Models', model_name, 'model_info.txt'), 'x') as file:
            file.write('video_' + str(x.shape[1]) + '_' + str(x.shape[2]) + '_' + str(action_shape) + '\n')
            for action in actions:
                file.write(action)
                if action != actions[len(actions) - 1]:
                    file.write('_')
            with open(os.path.join('../Datasets', dataset_name, 'dataset_info.txt'), 'r') as dsi:
                file.write('\n' + dsi.readline())
