import numpy as np
import cv2
import imutils

map = cv2.imread('map.jpg')
vid = cv2.VideoCapture(filename, cv2.CAP_ANY)

width = int(vid.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(vid.get(cv2.CAP_PROP_FRAME_HEIGHT))
frames_per = round(vid.get(cv2.CAP_PROP_FPS), 4)
duration = round(vid.get(cv2.CAP_PROP_FRAME_COUNT) / frames_per, 1)
frame_total = vid.get(cv2.CAP_PROP_FRAME_COUNT)

meta = [width, height, frames_per, duration, frame_total]

centers = []
found = None

while vid.isOpened():
    cv2.waitKey(1)
    grabbed = vid.grab()
    if grabbed:
        frame_num = vid.get(cv2.CAP_PROP_POS_FRAMES)
        if int(frame_num) % 30 == 0:
            ret, frame = vid.retrieve()
    else:
        break
        
    template = frame[0:0,
                     400:400]
                
    h, w = template.shape[:2]
                
    template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
    map = cv2.cvtColor(map, cv2.COLOR_BGR2GRAY)
    
    for scale in np.linspace(0.2, 1.0, 20)[::-1]: 

        resized = imutils.resize(map, width = int(map.shape[1] * scale))
		ratio = map.shape[1] / float(resized.shape[1])
        
        if resized.shape[0] < h or resized.shape[1] < w:
			break
        
        res = cv2.matchTemplate(map, template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv.minMaxLoc(res)
        
        if found is None or max_val > found[0]:
            found = (max_val, max_loc, ratio)
        
    _, max_loc, ratio = found
    x_start, y_start = int(max_loc[0] * ratio), int(max_loc[1] * r)
    x_fin, y_fin = int((max_loc[0]+ w) * ratio), int((max_loc[1]+ h) * r)
    
    cv2.rectangle(map, (x_fin, y_fin), (x_fin, y_fin), (0,255,0), 2)
    
    cv2.imshow('map', map)
    
    center = [int((max_loc[0] + w/2) * ratio), int((max_loc[1] + h/2) * r)]
    centers.append(center)
    
vid.release()

pts = np.array(centers, np.int32)
pts = pts.reshape((-1,1,2))
cv2.polylines(map,[pts],False,(0,255,255))
cv.imwrite('test_map.png', map)

cv2.imshow('path', map)
cv2.waitKey(0)

cv2.destroyAllWindows()
