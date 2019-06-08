from subprocess import run, PIPE
import cv2
import re


def get_meta_cv(vid):
    """ Extract Meta info using openCV """
    # uses opencv's inbuilt functions to pull meta info, fast but possibly inaccurate
    width = int(vid.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(vid.get(cv2.CAP_PROP_FRAME_HEIGHT))
    frames_per = round(vid.get(cv2.CAP_PROP_FPS), 4)
    duration = round(vid.get(cv2.CAP_PROP_FRAME_COUNT) / frames_per, 1)
    frame_total = vid.get(cv2.CAP_PROP_FRAME_COUNT)

    meta = [width, height, frames_per, duration, frame_total]

    return meta


def get_meta(filename):
    """ Extract Meta info using ffprobe """
    # calls ffprobe in as a subprocess to get meta info, more accurate but slower
    cmd = run(['ffprobe', '-v', 'quiet', '-select_streams', 'v:0', '-show_entries',
               'stream=width,height,avg_frame_rate,duration,nb_frames', '-of', 'csv=p=0', filename], stderr=PIPE,
              stdout=PIPE)
    # returncode will show a 0 if ffprobe ran successfully
    if cmd.returncode != 0:
        stdout = cmd.stdout.decode('utf-8')
        stderr = cmd.stderr.decode('utf-8')
        raise ChildProcessError(
            f'ffprobe exited with error code {cmd.returncode}\nstdout:\n{stdout}\n\nstderror:\n{stderr}'
        )
    output = cmd.stdout.decode('utf-8')
    meta = [x.strip() for x in output.split(',')]

    meta[2] = eval(meta[2])

    return meta


def get_frame_data(filename, frame_data):
    """ Extract time code for every frame using ffprobe """
    cmd = run(['ffprobe', '-v', 'quiet', '-select_streams', 'v:0', '-show_frames', '-show_entries',
               'frame=best_effort_timestamp_time,coded_picture_number', '-of', 'csv=p=0', filename], stderr=PIPE,
              stdout=PIPE)
    # returncode will show a 0 if ffprobe ran successfully
    if cmd.returncode != 0:
        stdout = cmd.stdout.decode('utf-8')
        stderr = cmd.stderr.decode('utf-8')
        raise ChildProcessError(
            f'ffprobe exited with error code {cmd.returncode}\nstdout:\n{stdout}\n\nstderror:\n{stderr}'
        )

    # filters out frame number and msec of the frame and adds them to the dictionary list in order
    output = cmd.stdout.decode('utf-8')
    frame_list = [x.strip() for x in re.split('\n|,', output)]

    while len(frame_list) > 2:
        msec = frame_list.pop(0)
        frame = int(frame_list.pop(0))
        frame_data[frame].insert(0, msec)

# codecs for best youtube quality
# '-vcodec', 'h264', '-acodec', 'aac',


def cut_clip_ms(cut_list, buffer, filename):
    """Cut as many clips as in given list, also passes output names for merge later"""
    merge_list = []
    # calls ffmpeg to cut the clips out of the the source video, will call this multiple times for each identified clip
    for frames in cut_list:
        start = round(frames[0] - buffer)
        end = round(frames[-1] + buffer)
        duration = round(end - start)

        # builds a new file name based on input video name and time of clip
        extension = filename.split('.')
        output = f'{".".join(extension[0:-2])}_{start}_{end}.{extension[-1]}'

        # -c copy, is stream copy and is very fast
        run(['ffmpeg', '-v', 'error', '-ss', str(start), '-i', str(filename), '-t', str(duration), '-c', 'copy',
             '-avoid_negative_ts', str(1), '-y', output])

        # adds name of files to the merge list, to be used in the merge_clips function
        merge_list.append(output)

    return merge_list


def merge_clips(filename, merge_list):
    """concat clips previously cut by cut_clip if desired"""
    # builds name for final merged video
    extension = filename.split('.')
    output = f'{".".join(extension[0:-2])}_highlights.{extension[-1]}'

    # a txt document is neccecary for the concat option to function correctly in ffmpeg
    temp_merge = 'temp_merge.txt'
    f = open(temp_merge, 'w')

    for name in merge_list:
        f.write(f"file '{name}'\n")
    f.close()

    # -c copy, is stream copy and is very fast.
    # could run '-vcodec', 'h264', '-acodec', 'aac', instead to make the final clip ready for youtube
    # possible to add that in as a config option
    run(['ffmpeg', '-v', 'error', '-f', 'concat', '-safe', '0', '-i', temp_merge, '-c', 'copy', '-y', output])
