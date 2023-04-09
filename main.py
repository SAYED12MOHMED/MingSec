import threading
import winsound

import cv2
from cv2 import VideoWriter
from cv2 import VideoWriter_fourcc

from time import time

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

_, start_frame = cap.read()
start_frame = cv2.cvtColor(start_frame, cv2.COLOR_BGR2GRAY)
start_frame = cv2.GaussianBlur(start_frame, (21, 21), 0)

alarm = False
alarm_mode = False
alarm_counter = 0

recording = False
recording_start = 0
file_name = 'recording.avi'
video = cv2.VideoWriter(file_name, VideoWriter_fourcc(*'XVID'), 25.0, (640, 480))

def beep_alarm():
    global alarm
    for i in range(5):
        if not alarm_mode:
            break
        print("ALARM...",i)
        # winsound.Beep(2500, 1000)
    alarm = False

while True:
    _, frame = cap.read()

    if alarm_mode:
        frame_bw = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        frame_bw = cv2.GaussianBlur(frame_bw, (5, 5), 0)

        difference = cv2.absdiff(frame_bw, start_frame)
        threshold = cv2.threshold(difference, 25, 255, cv2.THRESH_BINARY)[1]
        start_frame = frame_bw

        if threshold.sum() > 300: # smaller is more sensitive
            alarm_counter += 1
        else:
            if alarm_counter > 0:
                alarm_counter -= 1

        cv2.imshow("Cam", threshold)

    else:
        cv2.imshow("Cam", frame)
    
    if recording:
        video.write(frame)
        if int(time() * 1000) - recording_start > 5000:
            print("stop recording")
            recording_start = 0
            recording = False

    if alarm_counter > 20:
        if not alarm:
            alarm = True
            if recording_start == 0:
                file_name = 'recording'+str(int(time() * 1000))+'.avi'
                video = cv2.VideoWriter(file_name, VideoWriter_fourcc(*'XVID'), 25.0, (640, 480))
                recording = True
            recording_start = int(time() * 1000)
            threading.Thread(target=beep_alarm).start()

    key_pressed = cv2.waitKey(30)
    if key_pressed == ord("t"):
        alarm_mode = not alarm_mode
        alarm_counter = 0

    if key_pressed == ord("q"):
        alarm_mode = False
        break

video.release()
cap.release()
cv2.destroyAllWindows()