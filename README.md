# vodparser-apex
VOD Parser for Apex Legends

probs get some video stats, resolution, frame rate. needed to calc ROI of ammo counter

load frame

start count of frames where no event is detected

append frame to buffer, if buffer full remove first frame of buffer and append current frame

convert to grey scale

narrow ROI

#identify ammo counter using template matching -not needed if only checking for difference of previous frame

use absdiff to check if different to previous frame, load current frame into prevframe variable to be checked against the next

if ammo counter has changed, write buffer to file, empty buffer, set frame count to 0
what if instead of writing buffer now, add event frames to buffer exceeding its default size and write all at same time once 

stop writing frames when frame count equals buffer size
