import numpy as np
import cv2
import ffmpy

vid = cv2.VideoCapture('Apex.mp4')
#initalize empty np array
prev = np.array([])
frame_c = 0
detection = 0
list_detection = []

#loop through video frames
while(vid.isOpened()):

#read frame from video
    ret, frame = vid.read()

    #if frame is present
    if ret:
        frame_c += 1
        #convert to grey, narrow ROI, threshhold pixels
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        roi = gray[972:1000, 1732:1778]
        ret, thresh = cv2.threshold(roi, 195, 255, cv2.THRESH_BINARY)

        #if prev array is empty, fill with current frame to give same frame result
        if prev.size == 0:
            prev = thresh

        #compare current and prev frame, calculate difference percentage
        diff = cv2.absdiff(thresh, prev)
        diff = diff.astype(np.uint8)
        diff_percent = (np.count_nonzero(diff)) * 100 / diff.size


        if diff_percent > 1:
            print(diff_percent)
            detection +=1
            list_detection.append(frame_c)


        cv2.namedWindow('frame', cv2.WINDOW_NORMAL)
        cv2.imshow('frame', frame)
        cv2.imshow('diff', diff)
        cv2.imshow('thresh', thresh)
        cv2.imshow('prev', prev)

        #update prev frame variable
        prev = thresh

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    else:
        break
print(frame_c)
print(detection)
print(list_detection)

start = int(list_detection[0]/30)
end = int(list_detection[-1]/30)
duration = end - start

#cuts video based on start and end frames
ff = ffmpy.FFmpeg(
                    inputs={'Apex.mp4': f'-ss "{start}"'},
                    # outputs={'test1.mp4': f'-vf "trim={start}:{duration}" -af "atrim={start}:{duration}" -c "copy"'}
                    outputs={'test1.mp4': f'-to "{duration}" -c "copy"'}
)
ff.run()


# stream = ffmpeg.input('Apex.mp4')
# # stream = ffmpeg.trim(stream, start_frame=list_detection[0], end_frame=list_detection[-1])
# # stream = ffmpeg.output(stream, 'test1.mp4')
# # ffmpeg.run(stream)