import numpy as np
import cv2

#load frames into variables 
img1 = cv2.imread("thumb0001.png", cv2.IMREAD_COLOR)
img2 = cv2.imread("thumb0002.png", cv2.IMREAD_COLOR)

#convert frames into grey scale
gray1 = cv2.cvtColor(img1, cv2.color_BGR2GRAY)
gray2 = cv2.cvtColor(img2, cv2.color_BGR2GRAY)

#narrow region to be compared
roi1 = gray1[1700:1800, 800:900]
roi2 = gray2[1700:1800, 800:900]

#compare images
diff = cv2.absdiff(roi1, roi2)

cv2.imshow('diff', diff)

#convert to integer
diff = diff.astype(np.unit8)

#find percentage of pixels not 0, higher percent means more difference, lower percent is more similar
diff_percent = (np.count_nonzero(diff) * 100 / diff.size

#return
print(diff_percent)

cv2.imshow('image1', img1)
cv2.imshow('image2', img2)

cv2.imshow('gray1', gray1)
cv2.imshow('gray2', gray2)

cv2.imshow('roi1', roi1)
cv2.imshow('roi2', roi2)

#k = cv2.waitKey(5) & 0xFF
#    if k == 27:
#        break

cv2.waitKey(0)
cv2.destroyAllWindows()