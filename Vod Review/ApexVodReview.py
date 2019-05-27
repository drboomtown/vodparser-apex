from imutils.video import FPS
import cv2
from configparser import ConfigParser
from collections import defaultdict
import time
import threading

from video_edit import get_meta_cv, get_frame_data, cut_clip_ms, merge_clips, get_meta
from video_proccessing import ammo_count, health_coord, get_health, reduction_det_ms, group_det_ms

config = ConfigParser()
config.read('config.ini')

debug = False

# print(config.get('DEFAULT','debug'))

ref = cv2.imread(config.get('DEFAULT', 'file_ref'), cv2.IMREAD_GRAYSCALE)
vid = cv2.VideoCapture(config.get('DEFAULT', 'filename'), cv2.CAP_ANY)
fps = FPS().start()

health_bar_coord = None
ammo_list = []
health_list = []
frame_total = []
frame_dict = defaultdict(list)
frame_count = 0
frame_data = defaultdict(list)

meta = get_meta(config.get('DEFAULT', 'filename'))


def cv_proccessing(frame_skip, meta, debug, frame_data): 
    while vid.isOpened():
        cv2.waitKey(1)

        grabbed = vid.grab()
        if grabbed:
            frame_no = vid.get(cv2.CAP_PROP_POS_FRAMES)
            if int(frame_no) % frame_skip == 0:
                ret, frame = vid.retrieve()
            else:
                if frame_count == 0:
                    ammo = 0
                    health = 0
                    frame_data[frame_count].append(ammo)
                    frame_data[frame_count].append(health)
                else:
                    prev = frame_data.get(frame_count - 1)
                    frame_data[frame_count].append(prev[-2])
                    frame_data[frame_count].append(prev[-1])
                continue
        else:
            break

        # ret, frame = vid.read()
        if ret:
            cv2.namedWindow('Video', cv2.WINDOW_NORMAL)
            cv2.imshow('Video', frame)

            ms = vid.get(cv2.CAP_PROP_POS_MSEC)

            ammo = ammo_count(ref, ret, frame, meta, frame_skip, debug)
            # ammo_list.append(ammo)

            if health_bar_coord == None:
                health_bar_coord = health_coord(ret, frame, health_bar_coord, meta)
                if health_bar_coord == None:
                    health = 0
            else:
                health = get_health(ret, frame, health_bar_coord, ammo, meta)

            # health = 0
            frame_data[frame_count].append(ammo)
            frame_data[frame_count].append(health)

            # frame_dict[ms] = [ammo, health]

            fps.update()
            frame_count += 1

        else:
            break
            
thread1 = threading.Thread(target=get_frame_data(), args=(config.get('DEFAULT', 'filename'), frame_data))
thread2 = threading.Thread(target=cv_proccessing(), args=(config.getint('DEFAULT', 'frame_skip'), meta, debug, frame_data))

thread1.start()
thread2.start()

# print('start')
# time_start = time.time()
# get_frame_data(config.get('DEFAULT', 'filename'))
# time_end = time.time()
# dur = time_end - time_start
# print('done' + str(dur))
            
# cv_proccessing(config.getint('DEFAULT', 'frame_skip'), meta, debug, frame_data)

thread1.join()
thread2.join()

vid.release()
cv2.destroyAllWindows()

print(meta)

for i,item in enumerate(frame_data.values()):
    if (i+1)%10000 == 0:
        print(item)
    else:
        print(f'{i} {item}',end=' ')
# print(frame_data)

dup_frame = int(meta[4]) - len(frame_data)
print(dup_frame)

final_det = reduction_det_ms(frame_data)
print(final_det)
cut_list = group_det_ms(final_det, config.getint('DEFAULT', 'buffer'), config.getint('DEFAULT', 'frame_skip'), debug)
print(cut_list)
# merge_list = cut_clip_ms(cut_list, config.getint('DEFAULT', 'buffer'), config.get('DEFAULT', 'filename'), meta,
#                          config.getint('DEFAULT', 'frame_skip'))
# print(merge_list)
# merge_clips(config.get('DEFAULT', 'filename'), merge_list)

fps.stop()
print(f'[INFO] clip duration: {meta[3]}')
print("[INFO] elapsed time: {:.2f}".format(fps.elapsed()))
print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))
