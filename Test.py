import cv2

wCam, hCam = 640, 480

cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)

while True:
    success, img  = cap.read()
    if success:
        cv2.imshow("Test", img)
        cv2.waitKey(1)
    else:
        print("Unsuccessful")