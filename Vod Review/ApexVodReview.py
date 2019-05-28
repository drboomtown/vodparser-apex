from imutils.video import FPS
import cv2
from configparser import ConfigParser
from collections import defaultdict
import time
import threading

from video_edit import get_meta_cv, get_meta, get_frame_data, cut_clip_ms, merge_clips
from video_proccessing import cv_proccessing, reduction_det_ms, group_det_ms

config = ConfigParser()
config.read('config.ini')

debug = False

ref = cv2.imread(config.get('DEFAULT', 'file_ref'), cv2.IMREAD_GRAYSCALE)
vid = cv2.VideoCapture(config.get('DEFAULT', 'filename'), cv2.CAP_ANY)

health_bar_coord = None
frame_count = 0
frame_data = defaultdict(list)
# meta = get_meta(config.get('DEFAULT', 'filename'))
meta = get_meta_cv(vid)

if debug is True:
    fps = FPS().start()

thread1 = threading.Thread(target=get_frame_data, args=(config.get('DEFAULT', 'filename'), frame_data))
thread2 = threading.Thread(target=cv_proccessing, args=(config.getint('DEFAULT', 'frame_skip'), meta, debug, frame_data, frame_count, health_bar_coord))

thread1.start()
thread2.start()

if debug is True:
    print(threading.enumerate())

thread1.join()
thread2.join()

vid.release()
cv2.destroyAllWindows()

final_det = reduction_det_ms(frame_data)

cut_list = group_det_ms(final_det, config.getint('DEFAULT', 'buffer'), config.getint('DEFAULT', 'frame_skip'), debug)

merge_list = cut_clip_ms(cut_list, config.getint('DEFAULT', 'buffer'), config.get('DEFAULT', 'filename'), meta,
                         config.getint('DEFAULT', 'frame_skip'))

merge_clips(config.get('DEFAULT', 'filename'), merge_list)

if debug is True:
    for i, item in enumerate(frame_data.values()):
        if (i + 1) % 10000 == 0:
            print(item)
        else:
            print(f'{i} {item}', end=' ')
    print(meta)
    print(final_det)
    print(cut_list)
    print(merge_list)
    fps.stop()
    print(f'[INFO] clip duration: {meta[3]}')
    print("[INFO] elapsed time: {:.2f}".format(fps.elapsed()))
    print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))
