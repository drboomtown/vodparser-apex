import cv2
import subprocess as sp
import numpy

FFMPEG_BIN = "ffmpeg"
command = [ FFMPEG_BIN,
        '-i', r'C:\Users\Hayden\PycharmProjects\apexvod\Apex.mp4',             # fifo is the named pipe
        # '-debug_ts', # -debug_ts could provide timestamps avoiding showinfo filter (-vcodec copy). Need to check by providing expected fps TODO
        '-pix_fmt', 'bgr24',      # opencv requires bgr24 pixel format.
        '-vcodec', 'rawvideo',
        #'-vcodec', 'copy', # very fast!, direct copy - Note: No Filters, No Decode/Encode, no quality loss
        '-an','-sn',              # we want to disable audio processing (there is no audio)
        '-vf', 'showinfo',
        '-f', 'image2pipe', '-']
pipe = sp.Popen(command, stdout = sp.PIPE, stderr = sp.PIPE,  bufsize=1920*1080*3)

while True:
    # Capture frame-by-frame
    raw_image = pipe.stdout.read(1920*1080*3)
    img_inf = pipe.stderr.read(244)
    print(img_inf)
    # transform the byte read into a numpy array
    image = numpy.fromstring(raw_image, dtype='uint8')
    image = image.reshape((1080,1920,3))          # Notice how height is specified first and then width
    if image is not None:
        cv2.imshow('Video', image)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    pipe.stdout.flush()
    pipe.stderr.flush()

cv2.destroyAllWindows()





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

