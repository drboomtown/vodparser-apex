from subprocess import run, PIPE
from imutils import contours
from imutils.video import FPS
import numpy as np
import imutils
import cv2

filename = "H:\ShadowPlay\Apex Legends\Apex Legends 2019.05.05 - 19.14.10.04.DVR.mp4"
file_ref = "Reference.png"

ref = cv2.imread(file_ref, cv2.IMREAD_GRAYSCALE)
vid = cv2.VideoCapture(filename, cv2.IMREAD_GRAYSCALE)

#ammo_list = []
#cut_list = []
#merge_list = []
buffer = 90
frame_skip = 2
debug = False