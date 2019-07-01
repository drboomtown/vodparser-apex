from imutils import contours
import numpy as np
import imutils
import cv2


def cv_proccessing(frame_skip, meta, debug, frame_data, frame_count, health_bar_coord, vid, ref, kill_only, accuracy):
    """Main function, runs through ammo, health and kill markers to output a dictionary with a list of those values"""
    while vid.isOpened():
        cv2.waitKey(1)

        # This will only pull every n frame defined in the config by frame_skip, and copy the values from the previous
        # frame if it is skipped, also breaks the loop at the end of the video
        grabbed = vid.grab()
        if grabbed:
            frame_no = vid.get(cv2.CAP_PROP_POS_FRAMES)
            if int(frame_no) % frame_skip == 0:
                ret, frame = vid.retrieve()
            else:
                # will set dummy values to the first frame in the vid, otherwise it will crash
                if frame_count == 0:
                    ammo = 0
                    health = 0
                    kill = 0
                    frame_data[frame_count].append(ammo)
                    frame_data[frame_count].append(health)
                    frame_data[frame_count].append(kill)
                    frame_count += 1
                else:
                    prev = frame_data.get(frame_count - 1)
                    frame_data[frame_count].append(prev[-3])
                    frame_data[frame_count].append(prev[-2])
                    frame_data[frame_count].append(prev[-1])
                    frame_count += 1
                continue
        else:
            break

        if ret:
            if debug is True:
                cv2.namedWindow('Video', cv2.WINDOW_NORMAL)
                cv2.imshow('Video', frame)
                # print(f'frame: {frame_count}')
            # if kill_only is set, this will skip over those functions to save time
            if kill_only is True:
                ammo = 0
                health = 0
            else:
                # ammo is returned first as get_health uses the ammo value to determine of the inventory is open
                ammo = ammo_count(ref, frame, meta, debug)

                # this will locate the health bar first and give coordinates to get_health
                if health_bar_coord is None:
                    health_bar_coord = health_coord(frame, health_bar_coord, meta, debug)
                    # if the health bar is still not located, just say health is 0 and try again next frame
                    if health_bar_coord is None:
                        health = 0
                else:
                    # once health bar is located, we will start reading actual health levels
                    health = get_health(frame, health_bar_coord, ammo, meta, debug)

            # kill markers are always found for now
            kill = kill_marker(frame, debug, meta)

            # appends returned values in a specific order

            if accuracy is False:
                time = int(vid.get(cv2.CAP_PROP_POS_MSEC)) / 1000
                frame_no = int(vid.get(cv2.CAP_PROP_POS_FRAMES)) - 1
                frame_data[frame_no].insert(0, time)
            frame_data[frame_count].append(ammo)
            frame_data[frame_count].append(health)
            frame_data[frame_count].append(kill)
            # keeps track of the correct frame to append values to
            frame_count += 1

        else:
            break


def kill_marker(frame, debug, meta):
    """ identifies if kill marker present in the frame"""

    # cuts down frame to cross hairs
    roi = frame[int(int(meta[1]) * 0.4537):
                int(int(meta[1]) * 0.5462), int(int(meta[0]) * 0.4739): int(int(meta[0]) * 0.526)]
    roi = cv2.resize(roi, (100, 100))

    # creates mask in the shape of the kill cross hairs
    mask = np.zeros(roi.shape, np.uint8)
    cv2.line(mask, (5, 5), (23, 23), (255, 255, 255), 2)
    cv2.line(mask, (5, 95), (23, 77), (255, 255, 255), 2)
    cv2.line(mask, (95, 6), (77, 24), (255, 255, 255), 2)
    cv2.line(mask, (95, 95), (77, 77), (255, 255, 255), 2)

    # converts mask to gray scale
    mask = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)

    # range of red to detect in HSV format
    low_red = np.array([4, 190, 140])
    upp_red = np.array([7, 230, 250])

    # converts frame to HSV format
    roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

    # applys the mask to the frame and blurs it a little to get more consistent colors
    red = cv2.bitwise_and(roi, roi, mask=mask)
    red = cv2.GaussianBlur(red, (3, 3), 0)

    # thresholds frame based on red range
    roi = cv2.inRange(red, low_red, upp_red)
    if debug is True:
        cv2.imshow('kill_mark', roi)

    # returns an average value of the pixels that are lit
    brightness = np.mean(roi)

    # if a certain amount of pixels are lit up it should indicate the kill markers are on screen
    if 4.38 < brightness < 5.1:
        kill = 1
        if debug is True:
            print(f'kill:{kill}')
    else:
        kill = 0

    return kill


def ammo_count(ref, frame, meta, debug):
    """ Reads ammo counter from video frame by template matching against a reference image """
    # ammo_count = ""

    # removes any small noise from the ref image, probably not necessary
    ref = cv2.threshold(ref, 10, 255, cv2.THRESH_BINARY)[1]

    # finds all contours in the ref image and sorts them into a list, with the left most contour in position 0
    ref_cnts = cv2.findContours(ref.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    ref_cnts = imutils.grab_contours(ref_cnts)
    ref_cnts = contours.sort_contours(ref_cnts, method="left-to-right")[0]

    # assigns each contour a number based on its position in the list, we will use this later to match digits to
    digits = {}
    for (i, c) in enumerate(ref_cnts):
        # probably don't need to identify their bounding rectangles
        (x, y, w, h) = cv2.boundingRect(c)
        roi = ref[y:y + h, x:x + w]
        roi = cv2.resize(roi, (112, 92))
        digits[i] = roi

    # cuts down frame to ammo display location. percentages are accurate enough i can probably remove if and elif
    # 1080p
    # 963 is 89.17%  1000 is 92.595%
    # 1732 is 90.21% 1778 is 92.6%
    if int(meta[1]) == 1080:
        frame = frame[963:1000, 1730:1780]

    # 720p
    # 642.024 is 89.17% 666.684 is 92.595%
    # 1154.688 is 90.21% 1185.28 is 92.6%
    elif meta[1] == 720:
        frame = frame[642:667, 1154:1186]
    else:
        frame = frame[int(int(meta[1]) * 0.8917):int(int(meta[1]) * 0.92595),
                int(int(meta[0]) * 0.9021):int(int(meta[0]) * 0.926)]

    # converts ammo display to gray scale and thresholds out unwanted noise
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    frame = cv2.threshold(frame, 200, 255, cv2.THRESH_BINARY)[1]

    # finds contours of ammo display and returns them sorted in a list, left to right
    ammo_cnts = cv2.findContours(frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    ammo_cnts = imutils.grab_contours(ammo_cnts)
    if len(ammo_cnts) == 0:
        ammo_count = 0
        return ammo_count
    ammo_cnts = contours.sort_contours(ammo_cnts, method="left-to-right")[0]

    # initialise ammo list
    ammo = []

    # compares results from ammo display and reference image and returns most confident answer
    for c in ammo_cnts:
        (x, y, w, h) = cv2.boundingRect(c)
        roi = frame[y:y + h, x:x + w]
        roi = cv2.resize(roi, (112, 92))

        scores = []

        for (digit, digitROI) in digits.items():
            result = cv2.matchTemplate(roi, digitROI, cv2.TM_CCOEFF_NORMED)
            (_, score, _, _) = cv2.minMaxLoc(result)
            scores.append(score)

        # if debug is True:
        #     if np.amax(scores) >= 0.5:
        #         print(f'ammo: {np.argmax(scores)}')
        #         # print(np.amax(scores))

        if np.amax(scores) >= 0.7:
            ammo.append(str(np.argmax(scores)))
        else:
            ammo_count = 0
            return ammo_count

    # joins answers into a string to return a final value
    ammo_count = "".join(ammo)

    if debug is True:
        cv2.imshow('ref_ammo', ref)
        cv2.imshow('frame_ammo', frame)
        print(f'ammo: {ammo_count}')

    return ammo_count


def health_coord(frame, health_bar_coord, meta, debug):
    """Finds the health bar and returns its coordinates """

    # cuts down frame to general area to be searched for the health bar
    # roi = frame[995:1029, 175:417]
    roi = frame[int(int(meta[1]) * 0.9213): int(int(meta[1]) * 0.9528),
          int(int(meta[0]) * 0.091): int(int(meta[0]) * 0.2172)]
    roi = cv2.resize(roi, (242, 34))
    roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(roi, 200, 255, cv2.THRESH_BINARY)[1]

    # finds contours in the frame and sorts them
    health_cnt = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    health_cnt = imutils.grab_contours(health_cnt)
    if len(health_cnt) < 1:
        health_bar_coord = None
        return health_bar_coord
    health_cnt = contours.sort_contours(health_cnt, method="left-to-right")[0]

    # for each contour found assigns their position and width and height
    for c in health_cnt:
        x, y, w, h = cv2.boundingRect(c)
        aspect_ratio = float(w) / h
        area = cv2.contourArea(c)

        if debug is True:
            print(f'contour area: {cv2.contourArea(c)}, aspect ratio: {float(w) / h}')
            cv2.drawContours(thresh, c, -1, (0, 255, 0), 2)
            cv2.imshow('frame', thresh)

        # if the contour has certain area and aspect ratio values it is most likely the health bar
        if 2300 < area < 3000 and 15 < aspect_ratio < 25:
            # stores the health bars location and height and width to be returned
            health_bar_coord = [x, y, w, h]
        else:
            health_bar_coord = None
    return health_bar_coord


def myround(x, base=5):
    """rounds numbers to the nearest 5"""
    return base * round(x / base)


def get_health(frame, health_bar_coord, ammo_count, meta, debug):
    """ splits health and shield, finds what level they are rounded to the nearest 5 and returns that"""

    # if the ammo display is present and has returned a string value we will read the health and shield level
    if type(ammo_count) is str:
        # cuts down frame to general area where health bar is located
        # roi = frame[995:1029, 175:417]
        roi = frame[int(int(meta[1]) * 0.9213): int(int(meta[1]) * 0.9528),
              int(int(meta[0]) * 0.091): int(int(meta[0]) * 0.2172)]
        roi = cv2.resize(roi, (242, 34))
        # roi = cv2.equalizeHist(roi)

        # splits image into three separate channels, this helps identify what rarity of armour is worn for shields
        # and returns a better value based on their colour
        blue, green, red = cv2.split(roi)
        # if red channel is brightest, most likely gold armour is worn and we use the red channel to detect it
        if cv2.mean(red)[0] - 50 > cv2.mean(blue)[0]:
            roi = np.mean(np.array([red]), axis=0)
        # otherwise, blue channel is acceptable for white, blue and purple armour
        else:
            roi = np.mean(np.array([blue]), axis=0)
        roi = cv2.threshold(roi, 170, 255, cv2.THRESH_BINARY)[1]

        # narrows frame further to only include the health bar
        roi_h = roi[health_bar_coord[1]:health_bar_coord[1] + health_bar_coord[3],
                health_bar_coord[0]:health_bar_coord[0] + health_bar_coord[2]]

        # narrows frame further to only include the shield bar
        roi_s = roi[health_bar_coord[1] - 10:health_bar_coord[1] + health_bar_coord[3] - 16,
                health_bar_coord[0]:health_bar_coord[0] + health_bar_coord[2] - 6]

        # calculates what percentage of the health and shield bar is full based on their brightness
        health = cv2.mean(roi_h)[0]
        health = round(health * 100 / 252)
        shield = cv2.mean(roi_s)[0]
        shield = round(shield * 100 / 241)

        if debug is True:
            cv2.imshow('roi_h', roi_h)
            cv2.imshow('roi_s', roi_s)
            print(f'health:{health}, Shield:{shield}')

    # if ammo display is not present and we do not take a reading
    else:
        health = 0
        shield = 0

    return str(health + shield)


def reduction_det_ms(frame_data):
    """ returns occurrences of reduction in ammo and health """
    prev_a = None
    prev_h = None
    det_list = []

    for frame, values in frame_data.items():
        # if this is the first loop, just compare first frame to its self to get things moving
        if prev_a is None:
            prev_a = values[1]
            prev_h = values[2]
        # compares current frame to previous frame, looking for a reduction in ammo or reduction in health or
        # if the hit marker was present
        if int(prev_a) - int(values[1]) == 1 or \
                8 < int(prev_h) - int(values[2]) < 120 and int(values[2]) != 0 or \
                int(values[3]) == 1:
            # if one of those triggers, append the msec value of the frame to a list to be returned,
            # and load current frame info into prev variables to be compared next loop
            det_list.append(float(values[0]))
            prev_a = values[1]
            prev_h = values[2]
        else:
            prev_a = values[1]
            prev_h = values[2]

    return det_list


def group_det_ms(final_det, debug, det_range):
    """ Groups occurrences of reduction in ammo level and health level """
    prev_f = 0
    cut = []
    cut_list = []

    for frame in final_det:

        # if the prev frame and current frame are within the detection range, add the prev frame to the current list
        if frame - prev_f <= det_range:
            cut.append(prev_f)
            prev_f = frame

        # if prev frame and current frame and further apart than the detection range, split off the current list of
        # frames and append them to the cut list
        elif frame - prev_f > det_range:
            cut.append(prev_f)
            # this will only split off the current list if it is longer than 3, this reduces false positives
            if len(cut) >= 3:
                cut = [cut[0], cut[-1]]
                cut_list.append(cut)
                # print(cut)
                cut = []
                prev_f = frame
            else:
                # if its less than 3, discard the list and start building again
                cut = []
                prev_f = frame

    # at the end of the list if the check the last frame and add it to the list of necessary
    if frame - prev_f <= det_range:
        cut.append(frame)

    # at the end of the list check if current list is greater than 3 and add it to the cut list if necessary
    if len(cut) >= 3:
        cut = [cut[0], cut[-1]]
        cut_list.append(cut)

    if debug is True:
        print(cut)

    return cut_list