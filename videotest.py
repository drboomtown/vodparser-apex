import numpy as np
import cv2
#load clip
vid = cv2.VideoCapture('Apex.mp4')
prev = cv2.imread('thumb0043.png')

#initalize empty array for previous frame
#prev = np.empty(0)

#loop through video frames
while(vid.isOpened()):

#read frame from video
    ret, frame = vid.read()
    
    #if frame is present
    if ret:
        #convert to grey
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        #show current frame in gray, previous frame in colour
        cv2.imshow('frame', gray)
        cv2.imshow('prev', prev)
        
        #overwrite previous frame with current frame
        prev = frame
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    else:
        break
        
#release vid and close windows
vid.release()
cv2.destroyAllWindows()
