# while vid.isOpened():
#     cv2.waitKey(1)
#
#     # grabbed = vid.grab()
#     # if grabbed:
#     #     frame_no = vid.get(cv2.CAP_PROP_POS_FRAMES)
#     #     if int(frame_no) % config.getint('DEFAULT', 'frame_skip') == 0:
#     #         ret, frame = vid.retrieve()
#     #     else:
#     #         continue
#     # else:
#     #     break
#
#     ret, frame = vid.read()
#     if ret:
#     # cv2.imshow('frame', frame)
#         meta = get_meta_cv(vid)
#
#         ammo = ammo_count(ref, ret, frame, meta, config.getint('DEFAULT','frame_skip'), debug, fps)
#         ammo_list.append(ammo)
#
#         if int(ammo) > 0:
#             cv_list = vid.get(cv2.CAP_PROP_POS_FRAMES)
#             frame_total.append(cv_list)
#
#
#     # if health_bar_coord == None:
#     #     health_bar_coord = health_coord(ret, frame, health_bar_coord, meta)
#     #     if health_bar_coord == None:
#     #         health = 0
#     # else:
#     #     health = get_health(ret, frame, health_bar_coord, ammo, meta)
#     #
#     #
#     # health_list.append(health)
#     else:
#         break

# vid.release()
# cv2.destroyAllWindows()
#
# ammo_det = ammo_det(ammo_list, vid)
# health_det = health_det(health_list)
#
# print(meta)
# print(frame_total)
# print(ammo_list)
# print(len(ammo_list))
# print(ammo_det)
# print(len(ammo_det))
# print(sum(ammo_det))
# # print(health_list)
# # print(len(health_list))
# # print(health_det)
# # print(len(health_det))
# # print(sum(health_det))
#
# # final_det = [sum(i) for i in zip(ammo_det, health_det)]
# # print(final_det)
# # print(len(final_det))
# # print(sum(final_det))
#
# cut_list = ammo_compare(ammo_det, config.getint('DEFAULT','buffer'), config.getint('DEFAULT','frame_skip'), debug)
# print(cut_list)
# merge_list = cut_clip(cut_list, config.getint('DEFAULT', 'buffer'), config.get('DEFAULT', 'filename'), meta,
#                       config.getint('DEFAULT', 'frame_skip'))
# print(merge_list)
#
# merge_clips(config.get('DEFAULT', 'filename'), merge_list)


def cut_clip(cut_list, buffer, filename, meta, frame_skip):
    """Cut as many clips as in given list, also passes output names for merge later"""
    merge_list = []
    for frames in cut_list:
        start = round((frames[0] * frame_skip - buffer) / meta[2])
        end = round((frames[-1] * frame_skip + buffer) / meta[2])
        # start = round((frames[0] * frame_skip) / meta[2])
        # end = round((frames[-1] * frame_skip) / meta[2])
        duration = round(end - start)

        extension = filename.split('.')
        output = f'{".".join(extension[0:-2])}_{start}_{end}.{extension[-1]}'

        run(['ffmpeg', '-r', '30', '-v', 'error', '-ss', str(start), '-i', str(filename), '-t', str(duration), '-c', 'copy',
             '-avoid_negative_ts', str(1), '-y', '-r', '30', output])

        merge_list.append(output)

    return merge_list
    
    
def ammo_compare(final_det, buffer, frame_skip, debug):
    """ Groups occurances of reduction in ammo level provided by ammo_counter """
    prev = None
    prev_f = 0
    frame_list = []
    cut = []
    cut_list = []
    prev_list = None

    # for i, count in enumerate(final_det):
    #     # frame = i
    #     # if prev == None:
    #     #     prev = count
    #     if count > 0:
    #     # if int(prev) - int(count) >= 1 and int(prev) - int(count) < 2:
    #         frame_list.append(i)
    #     #     prev = count
    #     # else:
    #     #     prev = count
    #
    # print(frame_list)



    det_range = 600
    for frame in final_det:
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
    
def ammo_det(ammo_list, vid):
    """ Groups occurances of reduction in ammo level provided by ammo_counter """
    prev = None
    # prev_f = 0
    det_list = []
    # cut = []
    # cut_list = []
    # prev_list = None
    frame_total = []

    for i, count in enumerate(ammo_list):
        # frame = i
        if prev == None:
            prev = count
        # if 1 <= int(prev) - int(count) <= 2:
        if int(prev) - int(count) == 1:
            det_list.append(i)
            prev = count

        else:
            prev = count

    return det_list
    
# def ammo_counter(ref, vid, meta, frame_skip, debug, fps):
#     """ Reads ammo counter from video frame by template matching against a reference image """
#     ammo_list = []
#
#     # ref = cv2.cvtColor(ref, cv2.COLOR_BGR2GRAY)
#     ref = cv2.threshold(ref, 10, 255, cv2.THRESH_BINARY)[1]
#
#     refCnts = cv2.findContours(ref.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
#     refCnts = imutils.grab_contours(refCnts)
#     refCnts = contours.sort_contours(refCnts, method="left-to-right")[0]
#
#     digits = {}
#     for (i, c) in enumerate(refCnts):
#         (x, y, w, h) = cv2.boundingRect(c)
#         roi = ref[y:y + h, x:x + w]
#         roi = cv2.resize(roi, (112, 92))
#         digits[i] = roi
#
#     while vid.isOpened():
#
#         grabbed = vid.grab()
#         if grabbed:
#             frame_no = vid.get(cv2.CAP_PROP_POS_FRAMES)
#             if int(frame_no) % int(frame_skip) == 0:
#                 ret, frame = vid.retrieve()
#             else:
#                 continue
#         else:
#             break
#
#         if ret:
#
#             if debug == True:
#                 cv2.imshow('frame1', frame)
#
#             # 1080p
#             # 963 is 89.17%  1000 is 92.595%
#             # 1732 is 90.21% 1778 is 92.6%
#             if int(meta[1]) == 1080:
#                 frame = frame[963:1000, 1730:1780]
#
#             # 720p
#             # 642.024 is 89.17% 666.684 is 92.595%
#             # 1154.688 is 90.21% 1185.28 is 92.6%
#             elif meta[1] == 720:
#                 frame = frame[642:667, 1154:1186]
#             else:
#                 frame = frame[int(meta[1] * 0.8917):int(meta[1] * 0.92595), int(meta[0] * 0.9021):int(meta[0] * 0.926)]
#
#             frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
#             frame = cv2.threshold(frame, 200, 255, cv2.THRESH_BINARY)[1]
#
#             ammoCnts = cv2.findContours(frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
#             ammoCnts = imutils.grab_contours(ammoCnts)
#             if len(ammoCnts) == 0:
#                 ammo_list.append(0)
#                 continue
#             ammoCnts = contours.sort_contours(ammoCnts, method="left-to-right")[0]
#
#             ammo = []
#
#             # for (i, c) in enumerate(ammoCnts):
#             #    (x, y, w, h) = cv2.boundingRect(c)
#             #     roi = frame[y:y + h, x:x + w]
#             #     roi = cv2.resize(roi, (112, 92))
#
#             for c in ammoCnts:
#                 (x, y, w, h) = cv2.boundingRect(c)
#                 roi = frame[y:y + h, x:x + w]
#                 roi = cv2.resize(roi, (112, 92))
#
#                 scores = []
#
#                 for (digit, digitROI) in digits.items():
#                     result = cv2.matchTemplate(roi, digitROI, cv2.TM_CCOEFF_NORMED)
#                     (_, score, _, _) = cv2.minMaxLoc(result)
#                     scores.append(score)
#
#                 if debug == True:
#                     print(np.argmax(scores))
#                     print(np.amax(scores))
#
#                 if np.amax(scores) >= 0.5:
#                     ammo.append(str(np.argmax(scores)))
#                 else:
#                     ammo.append('0')
#             if debug == True:
#                 print(ammo)
#             fps.update()
#             # temp = "".join(ammo)
#             ammo_list.append("".join(ammo))
#
#             if debug == True:
#                 cv2.imshow('ref', ref)
#                 cv2.imshow('frame', frame)
#                 if cv2.waitKey(1) & 0xFF == ord('q'):
#                     break
#
#         else:
#             break
#
#     vid.release()
#     cv2.destroyAllWindows()
#     return ammo_list


# def ammo_compare(ammo_list, buffer, frame_skip, debug):
#     """ Groups occurances of reduction in ammo level provided by ammo_counter """
#     prev = None
#     prev_f = 0
#     frame_list = []
#     cut = []
#     cut_list = []
#     prev_list = None
#
#     for i, count in enumerate(ammo_list):
#         frame = i
#         if prev == None:
#             prev = count
#         if 1 <= int(prev) - int(count) <= 2:
#         # if int(prev) - int(count) >= 1 and int(prev) - int(count) < 2:
#             frame_list.append(frame)
#             prev = count
#         else:
#             prev = count
#
#     print(frame_list)
#
#     det_range = 600
#     for frame in frame_list:
#         if frame - prev_f > det_range / frame_skip:
#             cut.append(prev_f)
#             if len(cut) >= 3:
#                 cut = [cut[0], cut[-1]]
#                 cut_list.append(cut)
#                 cut = []
#                 prev_f = frame
#             else:
#                 cut = []
#                 prev_f = frame
#         elif frame - prev_f <= det_range / frame_skip:
#             cut.append(prev_f)
#             prev_f = frame
#             if debug == True:
#                 print(cut)
#     if frame - prev_f <= det_range / frame_skip:
#         cut.append(frame)
#     print(cut)
#     if len(cut) >= 3:
#         cut = [cut[0], cut[-1]]
#         cut_list.append(cut)
#
#     return cut_list