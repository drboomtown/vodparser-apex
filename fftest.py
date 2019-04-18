import ffmpy

ff = ffmpy.FFmpeg(
                    inputs={'Apex.mp4': f'-ss "5"'},
                    # outputs={'test1.mp4': f'-vf "trim={start}:{duration}" -af "atrim={start}:{duration}" -c "copy"'}
                    outputs={'test1.mp4': f'-to "5" -c "copy" -avoid_negative_ts_make_zeroimport'}
)
print(ff.cmd)

# total frame counter. initialize globally at 0

# master list. initialize globally empty

# sub list. initialize within detection loop empty

# detection flag counter. initialize globally at 0
# +1 each comparison loop. set to 0 when detection triggers.
# if detection counter is < buffer size, append current total frame to a list
# if detection counter is > buffer size, append entire list to master list if list not empty

# for every sub list in master list, grab list value 0 first and -1 last
# divide first and last by frame rate to get time value
# minus first from last to get clip duration
# pass values to ffmpeg



