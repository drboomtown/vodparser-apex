import cv2
import subprocess as sp
import numpy
import time

FFMPEG_BIN = "ffmpeg"
command = [ FFMPEG_BIN,
        '-nostats',
        # '-debug_ts', # -debug_ts could provide timestamps avoiding showinfo filter (-vcodec copy). Need to check by providing expected fps TODO
        '-r', '30', # output 30 frames per second
        '-i', r'C:\Users\Hayden\PycharmProjects\apexvod\Apex.mp4',             # fifo is the named pipe
        '-an', '-sn',  # we want to disable audio processing (there is no audio)
        '-pix_fmt', 'bgr24',      # opencv requires bgr24 pixel format.
        '-vcodec', 'rawvideo',
        #'-vcodec', 'copy', # very fast!, direct copy - Note: No Filters, No Decode/Encode, no quality loss
        # '-vframes', '20', # process n video frames only. For Debugging
        '-vf', 'showinfo',
        '-f', 'image2pipe', 'pipe:1']

pipe = sp.Popen(command, stdout=sp.PIPE, stderr=sp.PIPE, bufsize=1920 * 1080 * 3+3357)


while pipe.poll() is None:

    if cv2.waitKey(0) & 0xFF == ord('q'):
        break

    raw_image = pipe.stdout.read(1920 * 1080 * 3)
    info = pipe.stderr.read(3357)

    image1 = numpy.frombuffer(raw_image, dtype='uint8')
    image2 = image1.reshape((1080, 1920, 3))

    cv2.imshow('Video', image2)
    print(info)

    pipe.stdout.flush()
    pipe.stderr.flush()

pipe.terminate()

cv2.destroyAllWindows()
