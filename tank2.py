import sys
from time import sleep
from multiprocessing import Process, Manager
import cv2
import math

#Key Dictionary
left = 0x25
up   = 0x26
right= 0x27
down = 0x28
A_key= 0x41
B_key= 0x42
C_key= 0x43
D_key= 0x44
E_key= 0x45
F_key= 0x46
G_key= 0x47
H_key= 0x48


looking = [0,0]
def watch(w1,w2):
    #move in x direction
    x = w1[0]- w2[0];
    if x > 0:
        #send keyboard command
        #win32api.keybd_event(left,0 ,0 ,0)
        print('left')
    else:
        #send keyboard command
        #win32api.keybd_event(right,0 ,0 ,0)
        print('right')
    #move in y direction
    y = w1[1]- w2[1];
    if y > 0:
        #send keyboard command
        #win32api.keybd_event(up,0 ,0 ,0)
        print('up')
    else:
        #send keyboard command
        #win32api.keybd_event(down,0 ,0 ,0)
        print('down')
        
    
def h():
    global looking
    cascPath = 'haarcascade_frontalface_default.xml'
    faceCascade = cv2.CascadeClassifier(cascPath)

    video_capture = cv2.VideoCapture(0)

    while True:
        # Capture frame-by-frame
        ret, frame = video_capture.read()

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        faces = faceCascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30),
            #flags=cv2.cv.CV_HAAR_SCALE_IMAGE
        )
        cLen = 0
        
        # Draw a rectangle around the faces
        centers = []
        for (x, y, w, h) in faces:
            centerX = x + w/2
            centerY = y + h/2
            cv2.rectangle(frame, (centerX, centerY), (centerX, centerY), (255, 0, 0), 2)
            centeri = [centerX,centerY]
            centers.append(centeri)
            cLen = cLen + 1

        #print(centers)
        centers.sort()
        mid = cLen/2
        if cLen > 0:
            watchPoint =  centers[mid]
            watch(looking,watchPoint)
            #print(watchPoint)
            looking = watchPoint
            
        # Display the resulting frame
        cv2.imshow('Video', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # When everything is done, release the capture
    video_capture.release()
    cv2.destroyAllWindows()


#--------Main--------------------------------
if __name__ == '__main__':

    processes = []

    manager = Manager()

    #  Run Camera Stuff
    p = Process(target=h)
    p.start()
    processes.append(p)
    
    #  Run Blennder game
    #p = Process(target=g)
    #p.start()
    #processes.append(p)
    #print("click")  
    
    try:
        for process in processes:
            process.join()
    except KeyboardInterrupt:
        print "Keyboard interrupt in main"
    finally:
        print "Cleaning up Main"

        
