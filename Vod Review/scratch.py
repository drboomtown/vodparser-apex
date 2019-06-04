import cv2
from imutils import contours
import numpy as np
import imutils

vid = cv2.VideoCapture(r'H:\Downloads\Videos\Apex Legends 2019.05.24 - 14.30.11.19.DVR.mp4-merged.mp4', cv2.CAP_ANY)
# frame = cv2.imread(r'C:\Users\Hayden\PycharmProjects\apexvod\examples\kill marker 13.png')
# ret = True
kernel = np.ones((6,6),np.uint8)

frame_list = []


def kill_marker(ret, frame, debug):
    roi = frame[490:590, 910:1010]
    blue, green, red = cv2.split(roi)
    blue = cv2.bitwise_not(blue)
    blue = cv2.threshold(blue, 215, 255, cv2.THRESH_BINARY)[1]

    closing = cv2.morphologyEx(blue, cv2.MORPH_CLOSE, kernel)

    killCnt = cv2.findContours(closing, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    killCnt = imutils.grab_contours(killCnt)
    if len(killCnt) > 0:
        killCnt = contours.sort_contours(killCnt, method="left-to-right")[0]
    else:
        kill = 0
        return kill
    # cv2.drawContours(roi, killCnt, -1, (0,255,0), 1)
    kill_markers = []
    for contour in killCnt:

        rect = cv2.minAreaRect(contour)
        center, w_h, angle = cv2.minAreaRect(contour)
        box = cv2.boxPoints(rect)
        box = np.int0(box)
        cv2.drawContours(roi, [box], 0, (255, 0, 0), 1)
        # print(f'Contour area  : {cv2.contourArea(contour)}')
        #print(f'Contour length: {cv2.arcLength(contour, True)}')
        # if w_h[0] > 0 and w_h[1] > 0:
        #     print(f'Contour aspect: {float(w_h[0])/w_h[1]}')
        if 53 < cv2.arcLength(contour, True) < 62:
            kill_markers.append(contour)

    #print(len(kill_markers))
    if len(kill_markers) > 1:
        kill = 1
    else:
        kill = 0
    if debug is True:
        cv2.imshow('roi_kill', roi)
        cv2.imshow('blue_kill', blue)
        cv2.imshow('closing_kill', closing)

    return kill


while True:
    ret, frame = vid.read()
    if ret:

        kill = kill_marker(ret, frame)
        frame_list.append(kill)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    else:
        break

print(f'Detections: {frame_list}')
cv2.destroyAllWindows()
vid.release()







# meta = [1920, 1080]
# while True:
#     if ret:
#         # roi = frame[995:1029, 175:417]
#         roi = frame[int(int(meta[1]) * 0.9213): int(int(meta[1]) * 0.9528),
#               int(int(meta[0]) * 0.091): int(int(meta[0]) * 0.2172)]
#         roi = cv2.resize(roi, (242, 34))
#         # roi = cv2.equalizeHist(roi)
#         blue, green, red = cv2.split(roi)
#         cv2.imshow('red', red)
#         cv2.imshow('green', green)
#         cv2.imshow('blue', blue)
#         print(str(cv2.mean(blue)[0]) + 'blue')
#         print(str(cv2.mean(red)[0]) + 'red')
#         print(str(cv2.mean(green)[0]) + 'green')
#         roi = np.mean(np.array([blue, red]), axis=0)
#         roi = cv2.threshold(roi, 170, 255, cv2.THRESH_BINARY)[1]
#
#         # cv2.namedWindow('Video', cv2.WINDOW_NORMAL)
#         cv2.imshow('Video', roi)
#
#         if cv2.waitKey(0) & 0xFF == ord('q'):
#             break
#
# cv2.destroyAllWindows()
#
# """White armor - blue only 180 ( all are equal )
#    Blue armor - blue only 200
#    Purp armour - blue only 190 sometimes purple has more red than blue, need to use the blue frame always
#    Gold armor - red only 200
#    """




# import cv2
# import subprocess as sp
# import numpy
# import time
#
# FFMPEG_BIN = "ffmpeg"
# command = [ FFMPEG_BIN,
#         # '-nostats',
#         '-i', r'C:\Users\Hayden\PycharmProjects\apexvod\Apex.mp4',             # fifo is the named pipe
#         '-an', '-sn',  # we want to disable audio processing (there is no audio)
#         '-pix_fmt', 'bgr24',      # opencv requires bgr24 pixel format.
#         '-vcodec', 'rawvideo',
#         #'-vcodec', 'copy', # very fast!, direct copy - Note: No Filters, No Decode/Encode, no quality loss
#         # '-vframes', '20', # process n video frames only. For Debugging
#         '-vf', 'showinfo',
#         '-f', 'image2pipe', 'pipe:1']
#
# pipe = sp.Popen(command, stdout=sp.PIPE, stderr=sp.PIPE)
#
# for no in range(46):
#     info = pipe.stderr.readline()
#     print(info)
#
#
#
#
#
#
# while pipe.poll() is None:
#
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break
#
#
#     raw_image = pipe.stdout.read(1920 * 1080 * 3)
#     info = pipe.stderr.readlines()
#
#     image1 = numpy.frombuffer(raw_image, dtype='uint8')
#     image2 = image1.reshape((1080, 1920, 3))
#
#
#     cv2.namedWindow('Video', cv2.WINDOW_NORMAL )
#     cv2.imshow('Video', image2)
#     print(info)
#
#     pipe.stdout.flush()
#     pipe.stderr.flush()
#
# pipe.terminate()
#
# cv2.destroyAllWindows()





# from imutils.video import FPS
# import cv2
# from configparser import ConfigParser
#
#
# from video_edit import get_meta_cv, get_frame_data, cut_clip_ms, merge_clips, get_meta
# from video_proccessing import ammo_count, health_coord, get_health, reduction_det_ms, group_det_ms
#
# # frame = cv2.imread(r"C:\Users\Hayden\PycharmProjects\apexvod\examples\Gold_full.png")
# # ret = True
#
# health_bar_coord = None
# ammo_count = 12
# frame_count = 0
#
# filename = r'H:\ShadowPlay\Apex Legends\Apex Legends 2019.05.16 - 15.35.47.07.DVR.mp4'
#
# # vid = cv2.VideoCapture(r'C:\Users\Hayden\PycharmProjects\apexvod\Apex.mp4')
# vid = cv2.VideoCapture(r'H:\ShadowPlay\Apex Legends\Apex Legends 2019.05.16 - 15.35.47.07.DVR.mp4', cv2.CAP_FFMPEG)
#
# meta = get_meta(filename)
# print(vid.get(cv2.CAP_PROP_POS_MSEC))
#
#
# frame_data = get_frame_data(filename)
#
# while vid.isOpened():
#     ret, frame = vid.read()
#     if ret:
#         cv2.waitKey(1)
#         # cv2.namedWindow('frame', cv2.WINDOW_NORMAL)
#         # cv2.imshow('frame', frame)
#
#         ms = round(vid.get(cv2.CAP_PROP_POS_MSEC) / 1000, 6)
#
#         frame_data[frame_count].append(ms)
#         frame_count += 1
#     else:
#         break
#
#
# vid.release()
# cv2.destroyAllWindows()
#
# print(meta)
# print(frame_data)

