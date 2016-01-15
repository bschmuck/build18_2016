import os
import cv2
import sys


def faceTracker(threadName, delay):
    faceCascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

    video_capture = cv2.VideoCapture(0)
    centerX = 0;

    while True:
        # Capture frame-by-frame
        ret, frame = video_capture.read()

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        faces = faceCascade.detectMultiScale(
                                             gray,
                                             scaleFactor=1.1,
                                             minNeighbors=5,
                                             minSize=(150, 150),    )

        #Draw a rectangle around the faces
        #for (x, y, w, h) in faces:
        #    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
    
        if len(faces) >= 1:
            (x,y,w,h) = faces[0]
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            centerNew = x + w/2
            if centerNew > centerX + 10:
                print('left')
            if centerNew < centerX - 10:
                print('right')
            centerX = centerNew
    

        # Display the resulting frame
        #cv2.imshow('Video', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # When everything is done, release the capture
    video_capture.release()
    cv2.destroyAllWindows()

def main():
    #faceTracker()
    try:
        thread.start_new_thread(faceTracker, ("Thread-1", 2, ))
    except:
        print "Face Track Error"

main()