import numpy as np
import cv2

#load frames into variables 
img1 = cv2.imread('thumb0043.png')
img2 = cv2.imread('thumb0001.png')

#convert frames into grey scale
gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

#narrow region to be compared
roi1 = gray1[966:1005, 1730:1780]
roi2 = gray2[966:1005, 1730:1780]

ret, thresh1 = cv2.threshold(roi1,200,255,cv2.THRESH_BINARY)
ret, thresh2 = cv2.threshold(roi2,200,255,cv2.THRESH_BINARY)

#compare images
diff = cv2.absdiff(thresh1, thresh2)

cv2.imshow('diff', diff)

#convert to integer
diff = diff.astype(np.uint8)

#find percentage of pixels not 0, higher percent means more difference, lower percent is more similar, #1.5% trigger percent seems to allow for margin of error
diff_percent = (np.count_nonzero(diff)) * 100 / diff.size

#return
print(diff_percent)

#cv2.imshow('image1', img1)
#cv2.imshow('image2', img2)

#cv2.imshow('gray1', gray1)
#cv2.imshow('gray2', gray2)

cv2.imshow('roi1', roi1)
cv2.imshow('roi2', roi2)

cv2.imshow('thresh1', thresh1)
cv2.imshow('thresh2', thresh2)

#k = cv2.waitKey(5) & 0xFF
#    if k == 27:
#        break

cv2.waitKey(0)
cv2.destroyAllWindows()
