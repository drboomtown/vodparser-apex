from imutils.video import FPS
import cv2
from configparser import ConfigParser
from collections import defaultdict


from video_edit import get_meta_cv, cut_clip,merge_clips, cut_clip_ms, get_frame_data
from video_proccessing import ammo_count, health_coord, get_health, ammo_det, health_det, ammo_compare, ammo_det_ms, ammo_compare_ms

config = ConfigParser()
config.read('config.ini')

debug = False

# print(config.get('DEFAULT','debug'))

ref = cv2.imread(config.get('DEFAULT','file_ref'), cv2.IMREAD_GRAYSCALE)
vid = cv2.VideoCapture(config.get('DEFAULT','filename'), cv2.CAP_FFMPEG)
fps = FPS().start()


health_bar_coord = None
ammo_list = []
health_list = []
frame_total = []
frame_dict = defaultdict(list)
frame_count = 0

meta = get_meta_cv(config.get('DEFAULT','filename'))
frame_data = get_frame_data(config.get('DEFAULT','filename'))

while vid.isOpened():
    cv2.waitKey(1)

    # grabbed = vid.grab()
    # if grabbed:
    #     frame_no = vid.get(cv2.CAP_PROP_POS_FRAMES)
    #     if int(frame_no) % config.getint('DEFAULT', 'frame_skip') == 0:
    #         ret, frame = vid.retrieve()
    #     else:
    #         continue
    # else:
    #     break

    ret, frame = vid.read()
    if ret:
        # cv2.imshow('frame', frame)

        ms = vid.get(cv2.CAP_PROP_POS_MSEC)

        ammo = ammo_count(ref, ret, frame, meta, config.getint('DEFAULT', 'frame_skip'), debug)
        # ammo_list.append(ammo)
        

    if health_bar_coord == None:
        health_bar_coord = health_coord(ret, frame, health_bar_coord, meta)
        if health_bar_coord == None:
            health = 0
    else:
        health = get_health(ret, frame, health_bar_coord, ammo, meta)
        
    frame_data[count].append(ammo)
    frame_data[count].append(health)
    #frame_dict[ms] = [ammo, health]
    
    fps.update()
    frame_count += 1
    
    else:
        break

vid.release()
cv2.destroyAllWindows()

print(meta)
print(frame_data)

dup_frame = meta[4] - len(frame_data)
print(dup_frame)

final_det = reduction_det_ms(frame_data)
print(final_det)
cut_list = group_det_ms(final_det, config.getint('DEFAULT', 'buffer'), config.getint('DEFAULT', 'frame_skip'), debug)
print(cut_list)
merge_list = cut_clip_ms(cut_list, config.getint('DEFAULT', 'buffer'), config.get('DEFAULT','filename'), meta, config.getint('DEFAULT', 'frame_skip'))
print(merge_list)
merge_clips(config.get('DEFAULT', 'filename'), merge_list)


fps.stop()
print(f'[INFO] clip duration: {meta[3]}')
print("[INFO] elapsed time: {:.2f}".format(fps.elapsed()))
print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))