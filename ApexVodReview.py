import numpy as np
import cv2
import ffmpy
import time

vid = cv2.VideoCapture('Apex.mp4')
#initalize empty np array, frame counters and list
prev = np.array([])
frame_total = 0
frame_detection = 0
list_detection = []

# set true to view output as it runs
debug = False
# set wait to 0 for frame by frame processing, 1 to go as fast as possible
wait = 1

# loop through video frames
while(vid.isOpened()):

    # read frame from video
    ret, frame = vid.read()

    # if frame is present
    if ret:
        frame_total += 1
        # convert to grey, narrow ROI, threshold pixels
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        roi = gray[972:1000, 1732:1778]
        ret, thresh = cv2.threshold(roi, 195, 255, cv2.THRESH_BINARY)

        # if prev array is empty, fill with current frame to give same frame result
        # necessary to run first frame without crashing
        if prev.size == 0:
            prev = thresh

        # compare current and prev frame, calculate difference percentage
        diff = cv2.absdiff(thresh, prev)
        diff = diff.astype(np.uint8)
        diff_percent = (np.count_nonzero(diff)) * 100 / diff.size

        if diff_percent > 1:
            if debug:
                print(diff_percent)
            frame_detection +=1
            list_detection.append(frame_total)

        # set debug true to show frames
        if debug:
            cv2.namedWindow('frame', cv2.WINDOW_NORMAL)
            cv2.imshow('frame', frame)
            cv2.imshow('diff', diff)
            cv2.imshow('thresh', thresh)
            cv2.imshow('prev', prev)
            if cv2.waitKey(wait) & 0xFF == ord('q'):
                break
        #update prev frame variable
        prev = thresh

    else:
        break

if debug:
    print(frame_total)
    print(frame_detection)
    print(list_detection)

start = int(list_detection[0]/30)
end = int(list_detection[-1]/30)
duration = end - start

# cuts video based on first detection time code and duration untill final detection
ff = ffmpy.FFmpeg(
                    inputs={'Apex.mp4': f'-ss "{start}"'},
                    outputs={f'test{time.strftime("%Y%m%d-%H%M%S")}.mp4':
                            f'-to "{duration}" -c "copy" -avoid_negative_ts "make_zero"'}
)
ff.run()

# set buffer size globally

# total frame counter. initialize globally at 0

# master list. initialize globally empty

# buffer list. initialize within detection loop empty

# detection flag counter. initialize globally at 0
# +1 each comparison loop. set to 0 when detection triggers.
# if detection counter is < buffer size, append current total frame to buffer list
# if detection counter is > buffer size, remove value 0 and append frame count
# if detection counter is > buffer size, append entire list to master list if list size > buffer x2


# for every sub list in master list, grab list value 0 first and -1 last
# divide first and last by frame rate to get time value
# minus first from last to get clip duration
# pass values to ffmpeg
