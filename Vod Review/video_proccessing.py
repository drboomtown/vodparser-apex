from imutils import contours
import numpy as np
import imutils
import cv2


def ammo_count(ref, ret, frame, meta, frame_skip, debug):
    """ Reads ammo counter from video frame by template matching against a reference image """
    ammo_count = ""

    # ref = cv2.cvtColor(ref, cv2.COLOR_BGR2GRAY)
    ref = cv2.threshold(ref, 10, 255, cv2.THRESH_BINARY)[1]

    refCnts = cv2.findContours(ref.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    refCnts = imutils.grab_contours(refCnts)
    refCnts = contours.sort_contours(refCnts, method="left-to-right")[0]

    digits = {}
    for (i, c) in enumerate(refCnts):
        (x, y, w, h) = cv2.boundingRect(c)
        roi = ref[y:y + h, x:x + w]
        roi = cv2.resize(roi, (112, 92))
        digits[i] = roi

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
        frame = frame[int(int(meta[1]) * 0.8917):int(int(meta[1]) * 0.92595), int(int(meta[0]) * 0.9021):int(int(meta[0]) * 0.926)]

    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    frame = cv2.threshold(frame, 200, 255, cv2.THRESH_BINARY)[1]

    ammoCnts = cv2.findContours(frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    ammoCnts = imutils.grab_contours(ammoCnts)
    if len(ammoCnts) == 0:
        ammo_count = 0
        return ammo_count
    ammoCnts = contours.sort_contours(ammoCnts, method="left-to-right")[0]

    ammo = []

    for c in ammoCnts:
        (x, y, w, h) = cv2.boundingRect(c)
        roi = frame[y:y + h, x:x + w]
        roi = cv2.resize(roi, (112, 92))

        scores = []

        for (digit, digitROI) in digits.items():
            result = cv2.matchTemplate(roi, digitROI, cv2.TM_CCOEFF_NORMED)
            (_, score, _, _) = cv2.minMaxLoc(result)
            scores.append(score)

        if debug:
            print(np.argmax(scores))
            print(np.amax(scores))

        if np.amax(scores) >= 0.5:
            ammo.append(str(np.argmax(scores)))
        else:
            ammo_count = 0
            return ammo_count
    if debug:
        print(ammo)

    ammo_count = "".join(ammo)
    # print(ammo_count)

    # if debug:
    #     cv2.imshow('ref', ref)
    #     cv2.imshow('frame', frame)
    #     if cv2.waitKey(1) & 0xFF == ord('q'):
    #         break

    return ammo_count


def health_coord(ret, frame, health_bar_coord, meta):
    """Finds the health bar and returns its coordinates """
    if ret:
        if health_bar_coord is None:
            # roi = frame[995:1029, 175:417]
            roi = frame[int(int(meta[1]) * 0.9213): int(int(meta[1]) * 0.9528), int(int(meta[0]) * 0.091): int(int(meta[0]) * 0.2172)]
            roi = cv2.resize(roi, (242, 34))
            roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

            thresh = cv2.threshold(roi, 200, 255, cv2.THRESH_BINARY)[1]
            healthCnt = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            healthCnt = imutils.grab_contours(healthCnt)
            if len(healthCnt) < 1:
                health_bar_coord = None
                return health_bar_coord
            healthCnt = contours.sort_contours(healthCnt, method="left-to-right")[0]
            for c in healthCnt:
                x, y, w, h = cv2.boundingRect(c)
                aspect_ratio = float(w) / h
                area = cv2.contourArea(c)

                # print(cv2.contourArea(c))
                # print(float(w) / h)

                cv2.drawContours(thresh, c, -1, (0, 255, 0), 2)
                cv2.imshow('frame', thresh)

                if 2300 < area < 3000 and 15 < aspect_ratio < 25:
                    health_bar_coord = [x, y, w, h]
                else:
                    health_bar_coord = None
    return health_bar_coord


def myround(x, base=5):
    return base * round(x / base)


def get_health(ret, frame, health_bar_coord, ammo_count, meta):
    """ splits health and shield, finds what level they are rounded to the nearest 5 and returns that"""
    if ret:
        # roi = frame[995:1029, 175:417]
        roi = frame[int(int(meta[1]) * 0.9213): int(int(meta[1]) * 0.9528), int(int(meta[0]) * 0.091): int(int(meta[0]) * 0.2172)]
        roi = cv2.resize(roi, (242, 34))
        # roi = cv2.equalizeHist(roi)
        blue, green, red = cv2.split(roi)
        if cv2.mean(red)[0] - 50 > cv2.mean(blue)[0]:
            roi = np.mean(np.array([red]), axis=0)
        else:
            roi = np.mean(np.array([blue]), axis=0)
        roi = cv2.threshold(roi, 170, 255, cv2.THRESH_BINARY)[1]
        # cv2.imshow('roi', roi)
        roi_h = roi[health_bar_coord[1]:health_bar_coord[1] + health_bar_coord[3],
                health_bar_coord[0]:health_bar_coord[0] + health_bar_coord[2]]

        roi_s = roi[health_bar_coord[1] - 10:health_bar_coord[1] + health_bar_coord[3] - 16,
                health_bar_coord[0]:health_bar_coord[0] + health_bar_coord[2] - 6]

        cv2.imshow('roi_h', roi_h)
        cv2.imshow('roi_s', roi_s)

        # print(cv2.mean(roi_h))
        # print(cv2.mean(roi_s))

        if type(ammo_count) is str:
            health = cv2.mean(roi_h)[0]
            health = round(health * 100 / 252)
            shield = cv2.mean(roi_s)[0]
            shield = round(shield * 100 / 241)
        else:
            health = 0
            shield = 0

        # print(health + shield)

        return str(health + shield)


def health_det(health_list):
    """ Groups occurances of reduction in ammo level provided by ammo_counter """
    prev = None
    det_list = []

    for count in health_list:
        # frame = i
        if prev == None:
            prev = count
        if 6 <= int(prev) - int(count) <= 100:
            # if int(prev) - int(count) >= 1 and int(prev) - int(count) < 2:
            det_list.append(1)
            prev = count
        else:
            det_list.append(0)
            prev = count
    return det_list


def reduction_det_ms(ammo_dict):
    """ returns occurances of reduction in ammo and health """
    prev_a = None
    prev_h = None
    det_list = []

    for ms, count in ammo_dict.items():
        if prev_a == None:
            prev_a = count[1]
            prev_h = count[2]
        if int(prev_a) - int(count[1]) == 1 or 8 < int(prev_h) - int(count[2]) < 120 and int(count[2]) != 0:
            det_list.append(count[0])
            prev_a = count[1]
            prev_h = count[2]
        else:
            prev_a = count[1]
            prev_h = count[2]

    return det_list


def group_det_ms(final_det, buffer, frame_skip, debug):
    """ Groups occurances of reduction in ammo level provided by ammo_counter """
    prev_f = 0
    cut = []
    cut_list = []

    det_range = 20000
    for frame in final_det:

        frame = float(frame) * 1000

        if frame - prev_f > det_range / frame_skip:
            cut.append(prev_f)
            if len(cut) >= 3:
                cut = [cut[0], cut[-1]]
                cut_list.append(cut)
                print(cut)
                cut = []
                prev_f = frame
            else:
                cut = []
                prev_f = frame
        elif frame - prev_f <= det_range / frame_skip:
            cut.append(prev_f)
            prev_f = frame
            if debug == True:
                print(cut)
    if frame - prev_f <= det_range / frame_skip:
        cut.append(frame)
    print(cut)
    if len(cut) >= 3:
        cut = [cut[0], cut[-1]]
        cut_list.append(cut)

    return cut_list
