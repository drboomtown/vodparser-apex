import cv2
import threading
from imutils.video import FPS
from configparser import ConfigParser
from collections import defaultdict
from video_edit import get_meta_cv, get_frame_data, cut_clip_ms, merge_clips
from video_proccessing import cv_proccessing, reduction_det_ms, group_det_ms

# reads the config file
config = ConfigParser()
config.read('config.ini')

# global variables, need to try to set these better
health_bar_coord = None
frame_count = 0
frame_data = defaultdict(list)
debug = config.get('DEFAULT', 'debug')
merge = config.get('DEFAULT', 'merge')
kill_only = config.get('DEFAULT', 'kill_only')

# reads reference image for ammo counter template matching
ref = cv2.imread(config.get('DEFAULT', 'file_ref'), cv2.IMREAD_GRAYSCALE)
# reads video file
vid = cv2.VideoCapture(config.get('DEFAULT', 'filename'), cv2.CAP_ANY)
# returns meta data from video file
meta = get_meta_cv(vid)

fps = FPS().start()

# creates two threads, one for getting accurate frame time stamps, and one for processing video frames
thread1 = threading.Thread(target=get_frame_data, args=(config.get('DEFAULT', 'filename'),
                                                        frame_data))
thread2 = threading.Thread(target=cv_proccessing, args=(config.getint('DEFAULT', 'frame_skip'),
                                                        meta,
                                                        debug,
                                                        frame_data,
                                                        frame_count,
                                                        health_bar_coord,
                                                        vid,
                                                        ref,
                                                        kill_only,
                                                        fps))

# starts the threads
thread1.start()
thread2.start()

if debug == 'True':
    print(threading.enumerate())

# waits until the threads are finished their function before continuing
thread1.join()
thread2.join()

# releases vid and destroys and windows
vid.release()
cv2.destroyAllWindows()

# works through the combined returned list from the two functions
# and creates a list of frames where detection actions occur
final_det = reduction_det_ms(frame_data)

# groups detections into cut segments based on how far apart they occur
cut_list = group_det_ms(final_det,
                        debug,
                        config.getint('DEFAULT', 'det_range'))

# completes initial cut of segments and returns their positions to a list for merging
merge_list = cut_clip_ms(cut_list,
                         config.getint('DEFAULT', 'buffer'),
                         config.get('DEFAULT', 'filename'))

# if merge is true in config will combine all previously cut segments
if merge is 'True':
    merge_clips(config.get('DEFAULT', 'filename'),
                merge_list)

if debug == 'True':
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
