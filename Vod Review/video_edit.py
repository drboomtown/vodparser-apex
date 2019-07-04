from subprocess import run, PIPE
import cv2
import re


def get_meta_cv(vid):
    """ Extract Meta info using openCV """
    width = int(vid.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(vid.get(cv2.CAP_PROP_FRAME_HEIGHT))
    frames_per = round(vid.get(cv2.CAP_PROP_FPS), 4)
    duration = round(vid.get(cv2.CAP_PROP_FRAME_COUNT) / frames_per, 1)
    frame_total = vid.get(cv2.CAP_PROP_FRAME_COUNT)

    meta = [width, height, frames_per, duration, frame_total]

    return meta


def get_meta(filename):
    """ Extract Meta info using ffprobe """
    cmd = run(['ffprobe',
               '-v',
               'quiet',
               '-select_streams',
               'v:0',
               '-show_entries',
               'stream=width,height,avg_frame_rate,duration,nb_frames',
               '-of',
               'csv=p=0',
               filename],
               stderr=PIPE,
               stdout=PIPE)
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


def get_frame_data(filename,
                   frame_data):
    """ Extract time code for every frame using ffprobe """
    # print('start probe')
    cmd = run(['ffprobe',
               '-v',
               'quiet',
               '-select_streams',
               'v:0',
               '-show_frames',
               '-show_entries',
               'frame=best_effort_timestamp_time,coded_picture_number',
               '-of',
               'csv=p=0',
               filename],
               stderr=PIPE,
               stdout=PIPE)
    # print('done probe')
    if cmd.returncode != 0:
        stdout = cmd.stdout.decode('utf-8')
        stderr = cmd.stderr.decode('utf-8')
        raise ChildProcessError(
            f'ffprobe exited with error code {cmd.returncode}\nstdout:\n{stdout}\n\nstderror:\n{stderr}'
        )
    output = cmd.stdout.decode('utf-8')
    # print(output)
    frame_list = [x.strip() for x in re.split('\n|,', output)]
    # print(frame_list)

    while len(frame_list) > 2:
        msec = frame_list.pop(0)
        frame = int(frame_list.pop(0))
        frame_data[frame].insert(0, msec)


# '-vcodec', 'h264', '-acodec', 'aac',


def cut_clip_ms(cut_list,
                buffer,
                filename,
                output_path=''):
    """Cut as many clips as in given list, also passes output names for merge later"""
    merge_list = []
    for frames in cut_list:
        start = round(frames[0] - buffer)
        end = round(frames[-1] + buffer)
        duration = round(end - start)
        # extension = filename.split('\\')
        extension = re.split('\\/', filename)
        extension = extension[-1].split('.')
        output = f'{output_path}{".".join(extension[0:-2])}_{start}_{end}.{extension[-1]}'

        run(['ffmpeg',
             '-v',
             'error',
             '-ss',
             str(start),
             '-i',
             str(filename),
             '-t',
             str(duration),
             '-c',
             'copy',
             '-avoid_negative_ts',
             str(1),
             '-y',
             output])

        merge_list.append(output)

    return merge_list


def merge_clips(filename,
                merge_list,
                output_path=''):
    """concat clips previously cut by cut_clip if desired"""
    extension = re.split('\\/', filename)
    extension = extension[-1].split('.')
    output = f'{output_path}{".".join(extension[0:-2])}_highlights.{extension[-1]}'
    temp_merge = 'temp_merge.txt'
    f = open(temp_merge, 'w')

    for name in merge_list:
        f.write(f"file '{name}'\n")
    f.close()

    run(['ffmpeg',
         '-v',
         'error',
         '-f',
         'concat',
         '-safe',
         '0',
         '-i',
         temp_merge,
         '-c',
         'copy',
         '-y',
         output])
    
