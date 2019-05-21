from imutils.video import FPS
import cv2
from configparser import ConfigParser

from video_edit import get_meta, cut_clip_ms, merge_clips
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
frame_dict = dict()
count = 0

meta = get_meta(config.get('DEFAULT', 'filename'))

while vid.isOpened():

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

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

        frame_dict[ms] = [ammo, health]

        fps.update()

        print(count)
        count += 1

    else:
        break

vid.release()
cv2.destroyAllWindows()

print(meta)
print(frame_dict)

dup_frame = int(meta[4]) - len(frame_dict)
print(meta[4])
print(len(frame_dict))
print(dup_frame)

final_det = reduction_det_ms(frame_dict)
print(final_det)
cut_list = group_det_ms(final_det, config.getint('DEFAULT', 'buffer'), config.getint('DEFAULT', 'frame_skip'), debug)
print(cut_list)
merge_list = cut_clip_ms(cut_list, config.getint('DEFAULT', 'buffer'), config.get('DEFAULT', 'filename'), meta,
                         config.getint('DEFAULT', 'frame_skip'))
print(merge_list)
merge_clips(config.get('DEFAULT', 'filename'), merge_list)

fps.stop()
print(f'[INFO] clip duration: {meta[3]}')
print("[INFO] elapsed time: {:.2f}".format(fps.elapsed()))
print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))