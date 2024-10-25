#Author Sam Pope
import customtkinter as ctk
import cv2
import numpy as np

from src.GUI.ctkMirror import MirrorGUI
from src.GestureRecognition.Tracker import PoseTracker
from src.GestureRecognition.Predictor import GesturePredictor

import threading


current_gesture = "404"

def checkGesture():
    wCam, hCam = 640, 480

    threshold = 0.90

    cap = cv2.VideoCapture(0)
    cap.set(3, wCam)
    cap.set(4, hCam)
    print("Camera Set")
    gs = PoseTracker()
    print("Tracker On")
    gp = GesturePredictor("OpenClosePinch")
    print("Predictor Loaded")
    while True:
        success, img = cap.read()
        lms = gs.detectPresence(img)
        lms = gs.formatLandmarks(lms, image=True, pose=False, left=False, right=True)
        lms.flatten()
        global current_gesture
        try:
            res  = gp.predict(threshold=threshold,landmarks=lms)
            current_gesture = res
        except:
            current_gesture = "None"

        cv2.imshow("Image", img)
        cv2.waitKey(1)



def main():
    global current_gesture
    print('Mirror Booting ... ')
    tracker = threading.Thread(target=checkGesture, daemon=False).start()


    window = ctk.CTk()
    window.title("MirrorGUI")
    window.geometry("1920x1080")
    window.configure(fg_color='black')

    mirror_gui = MirrorGUI(window)

    mirror_gui.place(relx=0, rely=0, relwidth=1, relheight=1)

    def gestureCheck():
        if current_gesture == "open":
            mirror_gui.animate()
        window.after(800, gestureCheck)

    window.after(800, gestureCheck)
    window.mainloop()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
