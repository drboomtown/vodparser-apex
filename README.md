# vodparser-apex
VOD Parser for Apex Legends

load frame

start count of frames where no event is detected

append frame to buffer, if buffer full remove first frame of buffer and append current frame

convert to grey scale

narrow ROI

identify ammo counter using template matching

somehow check if different to previous frame?? big mystery 

if ammo counter has changed, write buffer to file, empty buffer, set frame count to 0

stop writing frames when frame count equals buffer size
